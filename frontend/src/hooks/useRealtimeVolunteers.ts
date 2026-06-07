'use client';
import { useEffect, useState, useRef } from 'react';
import { supabase } from '@/lib/supabase';
import type { Volunteer } from '@/types/volunteer';

let instanceCount = 0;

export function useRealtimeVolunteers() {
  const [volunteers, setVolunteers] = useState<Volunteer[]>([]);
  const channelName = useRef(`volunteers-live-${++instanceCount}`);

  useEffect(() => {
    // Initial fetch
    supabase
      .from('volunteers')
      .select('*')
      .neq('status', 'offline')
      .then(({ data }) => { if (data) setVolunteers(data as Volunteer[]); });

    // One unbroken fluent chain: .on() always before .subscribe()
    const channel = supabase
      .channel(channelName.current)
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'volunteers' },
        (payload) => {
          setVolunteers(prev => {
            if (payload.eventType === 'INSERT') {
              return [...prev, payload.new as Volunteer];
            }
            if (payload.eventType === 'UPDATE') {
              return prev.map(v =>
                v.id === (payload.new as Volunteer).id ? (payload.new as Volunteer) : v
              );
            }
            if (payload.eventType === 'DELETE') {
              return prev.filter(v => v.id !== (payload.old as Volunteer).id);
            }
            return prev;
          });
        }
      )
      .subscribe((status) => {
        if (status === 'CHANNEL_ERROR') {
          console.error('Realtime volunteers channel error:', status);
        }
      });

    return () => { supabase.removeChannel(channel); };
  }, []);

  return volunteers;
}
