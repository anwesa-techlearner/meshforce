'use client';
import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const CORRECT_PIN = '1234';

export default function AdminLogin() {
  const router = useRouter();
  const [pin, setPin] = useState('');
  const [error, setError] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (sessionStorage.getItem('adminAuth') === 'true') {
      router.replace('/admin');
    }
    inputRef.current?.focus();
  }, [router]);

  function handleInput(val: string) {
    const digits = val.replace(/\D/g, '').slice(0, 4);
    setPin(digits);
    setError(false);
    if (digits.length === 4) {
      if (digits === CORRECT_PIN) {
        sessionStorage.setItem('adminAuth', 'true');
        router.push('/admin');
      } else {
        setError(true);
        setPin('');
        setTimeout(() => inputRef.current?.focus(), 100);
      }
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="bg-slate-900 rounded-xl p-8 w-full max-w-sm shadow-2xl border border-slate-700">
        <div className="text-center mb-8">
          <div className="text-4xl mb-2">🛡️</div>
          <h1 className="text-2xl font-bold text-white">MeshForce Admin</h1>
          <p className="text-slate-400 text-sm mt-1">Command Center Access</p>
        </div>

        <div className="space-y-4">
          <label className="block text-sm font-medium text-slate-300 text-center">Enter PIN</label>
          <input
            ref={inputRef}
            type="password"
            inputMode="numeric"
            maxLength={4}
            value={pin}
            onChange={(e) => handleInput(e.target.value)}
            className={`w-full text-center text-3xl tracking-widest bg-slate-800 border rounded-lg py-4 text-white focus:outline-none transition-colors ${
              error ? 'border-red-500 animate-pulse' : 'border-slate-600 focus:border-blue-500'
            }`}
            placeholder="••••"
          />
          {error && (
            <p className="text-red-400 text-sm text-center">Incorrect PIN. Try again.</p>
          )}
          <div className="flex justify-center gap-2 mt-2">
            {[0, 1, 2, 3].map((i) => (
              <div
                key={i}
                className={`w-3 h-3 rounded-full transition-colors ${
                  i < pin.length ? 'bg-blue-500' : 'bg-slate-700'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
