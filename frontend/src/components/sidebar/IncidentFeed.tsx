import type { Incident } from '@/types/incident';
import { SeverityBadge } from '@/components/ui/SeverityBadge';
import { CategoryIcon } from '@/components/ui/CategoryIcon';

interface Props {
  incidents: Incident[];
}

const statusColor: Record<string, string> = {
  reported: 'border-yellow-500',
  dispatched: 'border-blue-500',
  resolved: 'border-green-600 opacity-60',
};

export function IncidentFeed({ incidents }: Props) {
  if (incidents.length === 0) {
    return (
      <div className="p-4 text-center text-slate-500 text-sm">
        No incidents yet.<br />Click ⚡ Simulate to generate demo data.
      </div>
    );
  }

  return (
    <div className="p-2 space-y-2">
      <p className="text-xs text-slate-500 px-1">Live Incident Log ({incidents.length})</p>
      {incidents.map((inc) => (
        <div
          key={inc.id}
          className={`bg-slate-800 border-l-2 rounded p-2 ${statusColor[inc.status] ?? 'border-slate-600'}`}
        >
          <div className="flex items-center gap-1 mb-1">
            <CategoryIcon category={inc.category} />
            <SeverityBadge severity={inc.severity} />
            <span className="ml-auto text-xs text-slate-500">{inc.sector_id}</span>
          </div>
          <p className="text-xs text-slate-300 line-clamp-2">{inc.summary}</p>
          <p className="text-xs text-slate-600 mt-1">{new Date(inc.created_at).toLocaleTimeString()}</p>
        </div>
      ))}
    </div>
  );
}
