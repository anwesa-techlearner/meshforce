'use client';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import type { Incident } from '@/types/incident';

export function useRealtimeIncidents() {
  const [incidents, setIncidents] = useState<Incident[]>([]);

  useEffect(() => {
    // Initial fetch — active incidents only
    supabase
      .from('incidents')
      .select('*')
      .neq('status', 'resolved')
      .order('created_at', { ascending: false })
      .then(({ data }) => { if (data) setIncidents(data); });

    const channel = supabase
      .channel('incidents-live')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'incidents' },
        (payload) => {
          setIncidents(prev => {
            if (payload.eventType === 'INSERT') {
              return [payload.new as Incident, ...prev];
            }
            if (payload.eventType === 'UPDATE') {
              return prev.map(i => i.id === (payload.new as Incident).id ? payload.new as Incident : i);
            }
            if (payload.eventType === 'DELETE') {
              return prev.filter(i => i.id !== (payload.old as Incident).id);
            }
            return prev;
          });
        }
      )
      .subscribe();

    return () => { supabase.removeChannel(channel); };
  }, []);

  return incidents;
}
