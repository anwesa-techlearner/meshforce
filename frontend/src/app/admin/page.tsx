'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import { useRealtimeIncidents } from '@/hooks/useRealtimeIncidents';
import { useRealtimeVolunteers } from '@/hooks/useRealtimeVolunteers';
import { IncidentFeed } from '@/components/sidebar/IncidentFeed';
import { StatsHeader } from '@/components/sidebar/StatsHeader';
import { SimulateButton } from '@/components/ui/SimulateButton';

// Leaflet must be dynamically imported (no SSR)
const CommandMap = dynamic(() => import('@/components/map/CommandMap'), { ssr: false });

export default function AdminPage() {
  const router = useRouter();
  const { incidents } = useRealtimeIncidents();
  const { volunteers } = useRealtimeVolunteers();
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (sessionStorage.getItem('adminAuth') !== 'true') {
        router.replace('/admin/login');
      } else {
        setAuthed(true);
      }
    }
  }, [router]);

  if (!authed) return null;

  return (
    <div className="flex h-screen bg-slate-950 text-white overflow-hidden">
      {/* Sidebar 30% */}
      <aside className="w-[30%] min-w-[280px] flex flex-col border-r border-slate-700 overflow-hidden">
        <div className="p-3 border-b border-slate-700">
          <h1 className="font-bold text-lg">🛡️ MeshForce</h1>
          <p className="text-slate-400 text-xs">Admin Command Center</p>
        </div>
        <StatsHeader incidents={incidents} volunteers={volunteers} />
        <div className="p-3 border-b border-slate-700">
          <SimulateButton />
        </div>
        <div className="flex-1 overflow-y-auto">
          <IncidentFeed incidents={incidents} />
        </div>
      </aside>

      {/* Map 70% */}
      <main className="flex-1">
        <CommandMap incidents={incidents} volunteers={volunteers} />
      </main>
    </div>
  );
}
