'use client';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import type { Volunteer } from '@/types/volunteer';

export function useRealtimeVolunteers() {
  const [volunteers, setVolunteers] = useState<Volunteer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase
      .from('volunteers')
      .select('*')
      .then(({ data }) => {
        if (data) setVolunteers(data as Volunteer[]);
        setLoading(false);
      });

    const channel = supabase
      .channel('volunteers-changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'volunteers' },
        (payload) => {
          if (payload.eventType === 'INSERT') {
            setVolunteers((prev) => [...prev, payload.new as Volunteer]);
          } else if (payload.eventType === 'UPDATE') {
            setVolunteers((prev) =>
              prev.map((v) => v.id === (payload.new as Volunteer).id ? (payload.new as Volunteer) : v)
            );
          } else if (payload.eventType === 'DELETE') {
            setVolunteers((prev) => prev.filter((v) => v.id !== (payload.old as Volunteer).id));
          }
        }
      )
      .subscribe();

    return () => { supabase.removeChannel(channel); };
  }, []);

  return { volunteers, loading };
}
