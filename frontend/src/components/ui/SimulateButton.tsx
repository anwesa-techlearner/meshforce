'use client';
import { useState } from 'react';

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export function SimulateButton() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  async function handleSimulate() {
    setRunning(true);
    setResult(null);
    try {
      // Clear stale mock data first to avoid phone uniqueness conflicts
      await fetch(`${BACKEND}/api/simulate/clear`, { method: 'DELETE' });

      const res = await fetch(`${BACKEND}/api/simulate/run`, { method: 'POST' });
      if (!res.ok) {
        const text = await res.text();
        setResult(`Error ${res.status}: ${text.slice(0, 120)}`);
        return;
      }
      const data = await res.json() as { message: string };
      setResult(data.message);
    } catch (e: unknown) {
      setResult(e instanceof Error ? `Network error: ${e.message}` : 'Failed to reach backend');
    } finally {
      setRunning(false);
    }
  }

  async function handleClear() {
    setRunning(true);
    setResult(null);
    try {
      const res = await fetch(`${BACKEND}/api/simulate/clear`, { method: 'DELETE' });
      if (!res.ok) { setResult(`Clear failed: ${res.status}`); return; }
      const data = await res.json() as { message: string };
      setResult(data.message);
    } catch (e: unknown) {
      setResult(e instanceof Error ? e.message : 'Clear failed');
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <button onClick={handleSimulate} disabled={running}
          className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 text-white text-xs font-semibold py-2 px-3 rounded transition-colors">
          {running ? '⏳ Running...' : '⚡ Simulate'}
        </button>
        <button onClick={handleClear} disabled={running}
          className="flex-1 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 text-white text-xs font-semibold py-2 px-3 rounded transition-colors">
          🗑 Clear
        </button>
      </div>
      {result && <p className="text-xs text-slate-400 break-words">{result}</p>}
    </div>
  );
}
