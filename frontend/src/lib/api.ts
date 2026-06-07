const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BACKEND_URL}${path}`);
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json();
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
  return res.json();
}

export async function apiPatch<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`PATCH ${path} failed: ${res.status}`);
  return res.json();
}

export async function apiDelete(path: string): Promise<void> {
  const res = await fetch(`${BACKEND_URL}${path}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`DELETE ${path} failed: ${res.status}`);
}

export const volunteersApi = {
  list: (params?: { status?: string; sector_id?: string }) => {
    const qs = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : '';
    return apiGet(`/api/volunteers${qs}`);
  },
  create: (body: unknown) => apiPost('/api/volunteers', body),
  updateStatus: (id: string, status: string) => apiPatch(`/api/volunteers/${id}/status`, { status }),
};

export const incidentsApi = {
  list: (params?: { status?: string; sector_id?: string }) => {
    const qs = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : '';
    return apiGet(`/api/incidents${qs}`);
  },
  report: (body: unknown) => apiPost('/api/incidents/report', body),
  resolve: (id: string) => apiPatch(`/api/incidents/${id}/resolve`),
};

export const simulateApi = {
  run: () => apiPost('/api/simulate/run', {}),
  clear: () => apiDelete('/api/simulate/clear'),
  stats: () => apiGet('/api/simulate/stats'),
};
