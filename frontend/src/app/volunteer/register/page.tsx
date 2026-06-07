'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { SECTORS, SKILLS, LANGUAGES } from '@/lib/sectors';
import { volunteersApi } from '@/lib/api';

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    name: '',
    phone: '',
    skills: [] as string[],
    languages: [] as string[],
    sector_id: 'SEC-01',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  function toggleArr(arr: string[], val: string): string[] {
    return arr.includes(val) ? arr.filter((x) => x !== val) : [...arr, val];
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const vol = await volunteersApi.create(form) as { id: string };
      localStorage.setItem('volunteerId', vol.id);
      localStorage.setItem('volunteerName', form.name);
      router.push('/volunteer');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center p-4">
      <form onSubmit={handleSubmit} className="w-full max-w-md space-y-5">
        <h1 className="text-2xl font-bold text-center">MeshForce Volunteer</h1>
        <p className="text-slate-400 text-center text-sm">Register to help at Mahakumbh 2025</p>

        {error && <div className="bg-red-900/50 border border-red-500 text-red-300 p-3 rounded text-sm">{error}</div>}

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Full Name *</label>
          <input
            required
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
            placeholder="Your name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Phone (E.164) *</label>
          <input
            required
            value={form.phone}
            onChange={(e) => setForm({ ...form, phone: e.target.value })}
            className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
            placeholder="+919876543210"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Assigned Sector *</label>
          <select
            value={form.sector_id}
            onChange={(e) => setForm({ ...form, sector_id: e.target.value })}
            className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
          >
            {SECTORS.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Skills</label>
          <div className="flex flex-wrap gap-2">
            {SKILLS.map((sk) => (
              <button
                key={sk}
                type="button"
                onClick={() => setForm({ ...form, skills: toggleArr(form.skills, sk) })}
                className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                  form.skills.includes(sk)
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-slate-800 border-slate-600 text-slate-300 hover:border-blue-500'
                }`}
              >
                {sk.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Languages</label>
          <div className="flex flex-wrap gap-2">
            {LANGUAGES.map((lang) => (
              <button
                key={lang}
                type="button"
                onClick={() => setForm({ ...form, languages: toggleArr(form.languages, lang) })}
                className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                  form.languages.includes(lang)
                    ? 'bg-green-600 border-green-500 text-white'
                    : 'bg-slate-800 border-slate-600 text-slate-300 hover:border-green-500'
                }`}
              >
                {lang}
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white font-semibold py-3 rounded transition-colors"
        >
          {loading ? 'Registering...' : 'Register as Volunteer'}
        </button>
      </form>
    </div>
  );
}
