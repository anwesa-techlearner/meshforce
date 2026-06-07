'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { StatusToggle } from '@/components/volunteer/StatusToggle';
import { ReportIncident } from '@/components/volunteer/ReportIncident';

export default function VolunteerHome() {
  const router = useRouter();
  const [volunteerId, setVolunteerId] = useState<string | null>(null);
  const [volunteerName, setVolunteerName] = useState('Volunteer');
  const [sectorId, setSectorId] = useState<string | undefined>(undefined);

  useEffect(() => {
    const id = localStorage.getItem('volunteerId');
    if (!id) { router.push('/volunteer/register'); return; }
    setVolunteerId(id);
    setVolunteerName(localStorage.getItem('volunteerName') || 'Volunteer');
    setSectorId(localStorage.getItem('volunteerSector') || 'SEC-01');
  }, [router]);

  if (!volunteerId) return null;

  return (
    <div className="min-h-screen bg-slate-900 text-white p-4 max-w-md mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold">MeshForce</h1>
          <p className="text-slate-400 text-sm">Welcome, {volunteerName}</p>
        </div>
        <button onClick={() => { localStorage.clear(); router.push('/volunteer/register'); }}
          className="text-xs text-slate-500 hover:text-slate-300 border border-slate-700 rounded px-2 py-1">
          Logout
        </button>
      </div>

      <div className="space-y-4">
        <StatusToggle volunteerId={volunteerId} />
        <ReportIncident volunteerId={volunteerId} sectorId={sectorId} />
      </div>

      <p className="text-center text-xs text-slate-600 mt-8">
        {typeof navigator !== 'undefined' && navigator.onLine ? '🟢 Online' : '🔴 Offline'}
      </p>
    </div>
  );
}
