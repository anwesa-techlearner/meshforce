import type { IncidentCategory } from '@/types/incident';

const icons: Record<IncidentCategory, string> = {
  medical: '🏥',
  crowd_control: '👥',
  lost_found: '🔍',
  infrastructure: '🔧',
  general: 'ℹ️',
};

export function CategoryIcon({ category }: { category: IncidentCategory }) {
  return <span title={category}>{icons[category] ?? 'ℹ️'}</span>;
}
