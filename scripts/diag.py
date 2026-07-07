import requests, time

BACKEND = 'https://meshforce-api.onrender.com'
SVC = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlvZWNvZnNrZnBjaGJ4YmNod2R4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDgyMjU4OCwiZXhwIjoyMDk2Mzk4NTg4fQ.xsMnbYkA53iN5lYAeS6xYzl5pFaZfdksKNE4aSGnURY'
SUPABASE = 'https://ioecofskfpchbxbchwdx.supabase.co'
RENDER_TOKEN = 'rnd_axAiwekJGZDPYuKA3BgHJkG77GRr'

print('=== 1. Backend /health ===')
try:
    r = requests.get(BACKEND + '/health', timeout=35)
    print('  status:', r.status_code, r.text[:100])
except Exception as e:
    print('  FAILED:', e)

print()
print('=== 2. POST /api/volunteers exact error ===')
phone = '+9188' + str(int(time.time()) % 10000000).zfill(7)
r = requests.post(BACKEND + '/api/volunteers',
    json={'name': 'DiagTest', 'phone': phone, 'skills': ['first_aid'],
          'languages': ['Hindi'], 'sector_id': 'SEC-01'}, timeout=20)
print('  status:', r.status_code)
print('  body:', r.text[:500])

print()
print('=== 3. Supabase tables reachable ===')
h = {'apikey': SVC, 'Authorization': 'Bearer ' + SVC}
for table in ['volunteers', 'incidents', 'sectors']:
    r2 = requests.get(SUPABASE + '/rest/v1/' + table + '?select=id&limit=1', headers=h)
    count = len(r2.json()) if r2.status_code == 200 else 'ERR'
    print(f'  {table}: {r2.status_code} rows_sample={count}')

print()
print('=== 4. Render latest deploy ===')
r3 = requests.get(
    'https://api.render.com/v1/services/srv-d8in4a7lk1mc738bvuhg/deploys?limit=1',
    headers={'Authorization': 'Bearer ' + RENDER_TOKEN, 'Accept': 'application/json'})
if r3.status_code == 200 and r3.json():
    dep = r3.json()[0].get('deploy', r3.json()[0])
    print('  status:', dep.get('status'), '| created:', str(dep.get('createdAt', ''))[:19])
else:
    print('  render API:', r3.status_code, r3.text[:100])

print()
print('=== 5. Backend env vars (via /openapi.json to confirm it is alive) ===')
r4 = requests.get(BACKEND + '/openapi.json', timeout=15)
paths = list(r4.json().get('paths', {}).keys()) if r4.status_code == 200 else []
print('  routes:', paths)
