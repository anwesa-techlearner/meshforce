'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { volunteersApi, incidentsApi } from '@/lib/api';
import { useOfflineQueue } from '@/hooks/useOfflineQueue';
import type { VolunteerStatus } from '@/types/volunteer';

const STATUS_LABELS: Record<VolunteerStatus, string> = {
  active_idle: '🟢 Active (Idle)',
  on_mission: '🔴 On Mission',
  resting: '🟡 Resting',
  offline: '⚫ Offline',
};

export default function VolunteerHome() {
  const router = useRouter();
  const { enqueue } = useOfflineQueue();
  const [volunteerId, setVolunteerId] = useState<string | null>(null);
  const [volunteerName, setVolunteerName] = useState('');
  const [status, setStatus] = useState<VolunteerStatus>('active_idle');
  const [statusLoading, setStatusLoading] = useState(false);

  const [showReport, setShowReport] = useState(false);
  const [reportText, setReportText] = useState('');
  const [reportLoading, setReportLoading] = useState(false);
  const [reportResult, setReportResult] = useState<{ severity: string; summary: string } | null>(null);

  useEffect(() => {
    const id = localStorage.getItem('volunteerId');
    const name = localStorage.getItem('volunteerName');
    if (!id) {
      router.push('/volunteer/register');
      return;
    }
    setVolunteerId(id);
    setVolunteerName(name || 'Volunteer');
  }, [router]);

  async function handleStatusChange(newStatus: VolunteerStatus) {
    if (!volunteerId) return;
    setStatusLoading(true);
    try {
      if (navigator.onLine) {
        await volunteersApi.updateStatus(volunteerId, newStatus);
      } else {
        enqueue(
          `${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/volunteers/${volunteerId}/status`,
          'PATCH',
          { status: newStatus }
        );
      }
      setStatus(newStatus);
    } catch {
      // status update failed silently
    } finally {
      setStatusLoading(false);
    }
  }

  async function handleReport(e: React.FormEvent) {
    e.preventDefault();
    if (!reportText.trim()) return;
    setReportLoading(true);
    setReportResult(null);
    try {
      if (navigator.onLine) {
        const res = await incidentsApi.report({ raw_text: reportText, reported_by: volunteerId || undefined }) as {
          parsed: { severity: string; summary: string };
        };
        setReportResult(res.parsed);
      } else {
        enqueue(
          `${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/incidents/report`,
          'POST',
          { raw_text: reportText, reported_by: volunteerId }
        );
        setReportResult({ severity: 'QUEUED', summary: 'Saved offline — will sync when online' });
      }
      setReportText('');
    } catch {
      setReportResult({ severity: 'ERROR', summary: 'Failed to submit — try again' });
    } finally {
      setReportLoading(false);
    }
  }

  const severityColor: Record<string, string> = {
    CRITICAL: 'bg-red-600',
    HIGH: 'bg-orange-500',
    MEDIUM: 'bg-yellow-500',
    LOW: 'bg-green-500',
    QUEUED: 'bg-slate-500',
    ERROR: 'bg-red-800',
  };

  if (!volunteerId) return null;

  return (
    <div className="min-h-screen bg-slate-900 text-white p-4 max-w-md mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold">MeshForce</h1>
          <p className="text-slate-400 text-sm">Welcome, {volunteerName}</p>
        </div>
        <button
          onClick={() => { localStorage.clear(); router.push('/volunteer/register'); }}
          className="text-xs text-slate-500 hover:text-slate-300"
        >
          Logout
        </button>
      </div>

      {/* Status Toggle */}
      <div className="bg-slate-800 rounded-lg p-4 mb-4">
        <p className="text-sm text-slate-400 mb-3">Your Status</p>
        <div className="grid grid-cols-2 gap-2">
          {(Object.keys(STATUS_LABELS) as VolunteerStatus[]).map((s) => (
            <button
              key={s}
              disabled={statusLoading}
              onClick={() => handleStatusChange(s)}
              className={`py-2 px-3 rounded text-sm font-medium transition-colors ${
                status === s
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {STATUS_LABELS[s]}
            </button>
          ))}
        </div>
      </div>

      {/* Report Incident Button */}
      {!showReport ? (
        <button
          onClick={() => setShowReport(true)}
          className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-4 rounded-lg text-lg mb-4 transition-colors"
        >
          🚨 Report Incident
        </button>
      ) : (
        <div className="bg-slate-800 rounded-lg p-4 mb-4">
          <div className="flex justify-between items-center mb-3">
            <h2 className="font-semibold">Report Incident</h2>
            <button onClick={() => { setShowReport(false); setReportResult(null); }} className="text-slate-400 hover:text-white">✕</button>
          </div>
          <form onSubmit={handleReport} className="space-y-3">
            <textarea
              value={reportText}
              onChange={(e) => setReportText(e.target.value)}
              rows={4}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-red-500 resize-none"
              placeholder="Describe what's happening in plain language..."
            />
            <button
              type="submit"
              disabled={reportLoading || !reportText.trim()}
              className="w-full bg-red-600 hover:bg-red-700 disabled:bg-slate-700 text-white py-2 rounded font-medium text-sm transition-colors"
            >
              {reportLoading ? 'Submitting...' : 'Submit Report'}
            </button>
          </form>

          {reportResult && (
            <div className={`mt-3 p-3 rounded ${severityColor[reportResult.severity] || 'bg-slate-600'} bg-opacity-20 border border-current`}>
              <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${severityColor[reportResult.severity] || 'bg-slate-600'} text-white mr-2`}>
                {reportResult.severity}
              </span>
              <span className="text-sm">{reportResult.summary}</span>
            </div>
          )}
        </div>
      )}

      <p className="text-center text-xs text-slate-600 mt-8">
        {navigator.onLine ? '🟢 Online' : '🔴 Offline — changes will sync'}
      </p>
    </div>
  );
}
