'use client';
import { useState } from 'react';
import { incidentsApi } from '@/lib/api';
import { useOfflineQueue } from '@/hooks/useOfflineQueue';
import { SeverityBadge } from '@/components/ui/SeverityBadge';
import type { Severity } from '@/types/incident';

interface Props {
  volunteerId: string;
  sectorId?: string;
}

export function ReportIncident({ volunteerId, sectorId }: Props) {
  const { enqueue } = useOfflineQueue();
  const [open, setOpen] = useState(false);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ severity: Severity; summary: string } | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      if (navigator.onLine) {
        const res = await incidentsApi.report({
          raw_text: text,
          sector_id: sectorId,
          reported_by: volunteerId,
        }) as { parsed: { severity: Severity; summary: string } };
        setResult(res.parsed);
      } else {
        const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
        enqueue(`${BACKEND}/api/incidents/report`, 'POST', {
          raw_text: text, sector_id: sectorId, reported_by: volunteerId,
        });
        setResult({ severity: 'LOW', summary: 'Saved offline — will sync when online' });
      }
      setText('');
    } catch {
      setResult({ severity: 'LOW', summary: 'Failed to submit — please try again' });
    } finally {
      setLoading(false);
    }
  }

  if (!open) {
    return (
      <button onClick={() => setOpen(true)}
        className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-4 rounded-lg text-lg transition-colors">
        🚨 Report Incident
      </button>
    );
  }

  return (
    <div className="bg-slate-800 rounded-lg p-4">
      <div className="flex justify-between items-center mb-3">
        <h2 className="font-semibold">Report Incident</h2>
        <button onClick={() => { setOpen(false); setResult(null); }} className="text-slate-400 hover:text-white text-xl leading-none">✕</button>
      </div>
      <form onSubmit={handleSubmit} className="space-y-3">
        <textarea value={text} onChange={(e) => setText(e.target.value)} rows={4}
          className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-red-500 resize-none"
          placeholder="Describe what's happening in plain language..." />
        <button type="submit" disabled={loading || !text.trim()}
          className="w-full bg-red-600 hover:bg-red-700 disabled:bg-slate-700 text-white py-2 rounded font-medium text-sm transition-colors">
          {loading ? 'Submitting...' : 'Submit Report'}
        </button>
      </form>
      {result && (
        <div className="mt-3 p-3 rounded bg-slate-700 border border-slate-500">
          <div className="flex items-center gap-2 mb-1">
            <SeverityBadge severity={result.severity} />
          </div>
          <p className="text-sm text-slate-300">{result.summary}</p>
        </div>
      )}
    </div>
  );
}
