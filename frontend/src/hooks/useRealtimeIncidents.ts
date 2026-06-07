'use client';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import type { Incident } from '@/types/incident';

export function useRealtimeIncidents() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase
      .from('incidents')
      .select('*')
      .order('created_at', { ascending: false })
      .then(({ data }) => {
        if (data) setIncidents(data as Incident[]);
        setLoading(false);
      });

    const channel = supabase
      .channel('incidents-changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'incidents' },
        (payload) => {
          if (payload.eventType === 'INSERT') {
            setIncidents((prev) => [payload.new as Incident, ...prev]);
          } else if (payload.eventType === 'UPDATE') {
            setIncidents((prev) =>
              prev.map((i) => (i.id === (payload.new as Incident).id ? (payload.new as Incident) : i))
            );
          } else if (payload.eventType === 'DELETE') {
            setIncidents((prev) => prev.filter((i) => i.id !== (payload.old as Incident).id));
          }
        }
      )
      .subscribe();

    return () => { supabase.removeChannel(channel); };
  }, []);

  return { incidents, loading };
}
