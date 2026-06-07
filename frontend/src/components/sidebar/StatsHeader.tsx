import type { Incident } from '@/types/incident';
import type { Volunteer } from '@/types/volunteer';

interface Props {
  incidents: Incident[];
  volunteers: Volunteer[];
}

export function StatsHeader({ incidents, volunteers }: Props) {
  const activeVols = volunteers.filter((v) => v.status === 'active_idle' || v.status === 'on_mission').length;
  const openIncs = incidents.filter((i) => i.status !== 'resolved').length;
  const resolvedToday = incidents.filter((i) => {
    if (i.status !== 'resolved' || !i.resolved_at) return false;
    const d = new Date(i.resolved_at);
    const now = new Date();
    return d.toDateString() === now.toDateString();
  }).length;

  return (
    <div className="grid grid-cols-3 gap-1 p-3 border-b border-slate-700">
      <div className="bg-slate-800 rounded p-2 text-center">
        <div className="text-lg font-bold text-green-400">{activeVols}</div>
        <div className="text-xs text-slate-400">Active Vols</div>
      </div>
      <div className="bg-slate-800 rounded p-2 text-center">
        <div className="text-lg font-bold text-orange-400">{openIncs}</div>
        <div className="text-xs text-slate-400">Open Incidents</div>
      </div>
      <div className="bg-slate-800 rounded p-2 text-center">
        <div className="text-lg font-bold text-blue-400">{resolvedToday}</div>
        <div className="text-xs text-slate-400">Resolved Today</div>
      </div>
    </div>
  );
}
