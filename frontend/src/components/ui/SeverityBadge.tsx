import type { Severity } from '@/types/incident';

const colors: Record<Severity, string> = {
  CRITICAL: 'bg-red-600 text-white',
  HIGH: 'bg-orange-500 text-white',
  MEDIUM: 'bg-yellow-500 text-black',
  LOW: 'bg-green-500 text-white',
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${colors[severity]}`}>
      {severity}
    </span>
  );
}
