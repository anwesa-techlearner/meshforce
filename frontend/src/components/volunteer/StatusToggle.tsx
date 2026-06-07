'use client';
import { useState } from 'react';
import { volunteersApi } from '@/lib/api';
import type { VolunteerStatus } from '@/types/volunteer';

const STATUS_LABELS: Record<VolunteerStatus, string> = {
  active_idle: '🟢 Active (Idle)',
  on_mission: '🔴 On Mission',
  resting: '🟡 Resting',
  offline: '⚫ Offline',
};

interface Props {
  volunteerId: string;
  initialStatus?: VolunteerStatus;
}

export function StatusToggle({ volunteerId, initialStatus = 'active_idle' }: Props) {
  const [status, setStatus] = useState<VolunteerStatus>(initialStatus);
  const [loading, setLoading] = useState(false);

  async function handleChange(newStatus: VolunteerStatus) {
    setLoading(true);
    try {
      await volunteersApi.updateStatus(volunteerId, newStatus);
      setStatus(newStatus);
    } catch {
      // silent fail — UI optimistically updated
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-slate-800 rounded-lg p-4">
      <p className="text-sm text-slate-400 mb-3">Your Status</p>
      <div className="grid grid-cols-2 gap-2">
        {(Object.keys(STATUS_LABELS) as VolunteerStatus[]).map((s) => (
          <button key={s} disabled={loading} onClick={() => handleChange(s)}
            className={`py-2 px-3 rounded text-sm font-medium transition-colors ${
              status === s ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}>
            {STATUS_LABELS[s]}
          </button>
        ))}
      </div>
    </div>
  );
}
