'use client';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import type { Volunteer } from '@/types/volunteer';

export function useRealtimeVolunteers() {
  const [volunteers, setVolunteers] = useState<Volunteer[]>([]);

  useEffect(() => {
    // Initial fetch
    supabase
      .from('volunteers')
      .select('*')
      .neq('status', 'offline')
      .then(({ data }) => { if (data) setVolunteers(data); });

    // Realtime subscription
    const channel = supabase
      .channel('volunteers-live')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'volunteers' },
        (payload) => {
          setVolunteers(prev => {
            if (payload.eventType === 'INSERT') {
              return [...prev, payload.new as Volunteer];
            }
            if (payload.eventType === 'UPDATE') {
              return prev.map(v => v.id === (payload.new as Volunteer).id ? payload.new as Volunteer : v);
            }
            if (payload.eventType === 'DELETE') {
              return prev.filter(v => v.id !== (payload.old as Volunteer).id);
            }
            return prev;
          });
        }
      )
      .subscribe();

    return () => { supabase.removeChannel(channel); };
  }, []);

  return volunteers;
}
