'use client';
import { useState } from 'react';
import { simulateApi } from '@/lib/api';

export function SimulateButton() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  async function handleSimulate() {
    setRunning(true);
    setResult(null);
    try {
      const res = await simulateApi.run() as { message: string };
      setResult(res.message);
    } catch (e: unknown) {
      setResult(e instanceof Error ? e.message : 'Simulation failed');
    } finally {
      setRunning(false);
    }
  }

  async function handleClear() {
    setRunning(true);
    setResult(null);
    try {
      await simulateApi.clear();
      setResult('Mock data cleared');
    } catch {
      setResult('Clear failed');
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <button
          onClick={handleSimulate}
          disabled={running}
          className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 text-white text-xs font-semibold py-2 px-3 rounded transition-colors"
        >
          {running ? '⏳ Running...' : '⚡ Simulate'}
        </button>
        <button
          onClick={handleClear}
          disabled={running}
          className="flex-1 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 text-white text-xs font-semibold py-2 px-3 rounded transition-colors"
        >
          🗑 Clear
        </button>
      </div>
      {result && <p className="text-xs text-slate-400 break-words">{result}</p>}
    </div>
  );
}
