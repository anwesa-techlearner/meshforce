import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
      <div className="w-full max-w-sm space-y-8 text-center">

        {/* Logo / title */}
        <div>
          <div className="text-5xl mb-3">🛡️</div>
          <h1 className="text-3xl font-bold tracking-tight">MeshForce</h1>
          <p className="text-slate-400 mt-2 text-sm">
            AI-Powered Volunteer Dispatch<br />Mahakumbh 2025
          </p>
        </div>

        {/* Role selector */}
        <div className="space-y-3">
          <Link
            href="/admin/login"
            className="flex items-center justify-center gap-3 w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-xl transition-colors text-lg"
          >
            <span className="text-2xl">🖥️</span>
            Open as Admin
          </Link>

          <Link
            href="/volunteer"
            className="flex items-center justify-center gap-3 w-full bg-slate-700 hover:bg-slate-600 text-white font-semibold py-4 px-6 rounded-xl transition-colors text-lg"
          >
            <span className="text-2xl">🙋</span>
            Open as Volunteer
          </Link>
        </div>

        <p className="text-slate-600 text-xs">
          Admin PIN: 1234
        </p>
      </div>
    </div>
  );
}
