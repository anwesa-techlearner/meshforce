"""
Applies schema.sql to Supabase via Management API (database/query endpoint).
Enables Realtime on volunteers and incidents tables.
Generates backend/.env and frontend/.env.local from .credentials.
Idempotent — safe to re-run.
"""
import requests, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from load_credentials import load

PROJECT_REF = "ioecofskfpchbxbchwdx"

def apply_sql(service_key: str, sql: str, label: str = ""):
    """Execute a single SQL statement via Supabase Management API."""
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }
    r = requests.post(url, json={"query": sql}, headers=headers, timeout=30)
    if r.status_code in (200, 201):
        print(f"  ✓ {label or sql[:60].strip()}")
        return True
    else:
        print(f"  ⚠ {label or sql[:60].strip()}")
        print(f"    → {r.status_code}: {r.text[:200]}")
        return False

def generate_env_files(creds: dict, backend_url: str = "http://localhost:8000"):
    """Write backend/.env and frontend/.env.local from credentials."""
    os.makedirs("backend", exist_ok=True)
    os.makedirs("frontend", exist_ok=True)

    backend_env = f"""SUPABASE_URL={creds['SUPABASE_URL']}
SUPABASE_SERVICE_KEY={creds['SUPABASE_SERVICE_KEY']}
ANTHROPIC_API_KEY={creds['ANTHROPIC_API_KEY']}
USE_MOCK_LLM=true
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=
"""
    with open("backend/.env", "w") as f:
        f.write(backend_env)
    print("  ✓ backend/.env generated")

    frontend_env = f"""NEXT_PUBLIC_SUPABASE_URL={creds['SUPABASE_URL']}
NEXT_PUBLIC_SUPABASE_ANON_KEY={creds['SUPABASE_ANON_KEY']}
NEXT_PUBLIC_BACKEND_URL={backend_url}
"""
    with open("frontend/.env.local", "w") as f:
        f.write(frontend_env)
    print("  ✓ frontend/.env.local generated")

def main():
    creds = load()

    print("\n1. Generating env files...")
    generate_env_files(creds)

    svc = creds["SUPABASE_SERVICE_KEY"]

    print("\n2. Applying schema statements one by one...")

    statements = [
        ("postgis", "CREATE EXTENSION IF NOT EXISTS postgis;"),
        ("sectors table", """CREATE TABLE IF NOT EXISTS sectors (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  center_lat DOUBLE PRECISION NOT NULL,
  center_lng DOUBLE PRECISION NOT NULL
);"""),
        ("volunteers table", """CREATE TABLE IF NOT EXISTS volunteers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  phone TEXT NOT NULL UNIQUE,
  skills TEXT[] NOT NULL DEFAULT '{}',
  languages TEXT[] NOT NULL DEFAULT '{}',
  sector_id TEXT REFERENCES sectors(id),
  status TEXT NOT NULL DEFAULT 'active_idle'
    CHECK (status IN ('active_idle','on_mission','resting','offline')),
  active_mission_id UUID,
  hours_worked DOUBLE PRECISION NOT NULL DEFAULT 0.0,
  shift_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_mock BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);"""),
        ("volunteers_sector_idx", "CREATE INDEX IF NOT EXISTS volunteers_sector_idx ON volunteers(sector_id);"),
        ("volunteers_status_idx", "CREATE INDEX IF NOT EXISTS volunteers_status_idx ON volunteers(status);"),
        ("incidents table", """CREATE TABLE IF NOT EXISTS incidents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reported_by UUID REFERENCES volunteers(id),
  raw_text TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('CRITICAL','HIGH','MEDIUM','LOW')),
  category TEXT NOT NULL CHECK (category IN ('medical','crowd_control','lost_found','infrastructure','general')),
  required_skills TEXT[] NOT NULL DEFAULT '{}',
  summary TEXT NOT NULL,
  sector_id TEXT REFERENCES sectors(id),
  location_lat DOUBLE PRECISION NOT NULL,
  location_lng DOUBLE PRECISION NOT NULL,
  status TEXT NOT NULL DEFAULT 'reported' CHECK (status IN ('reported','dispatched','resolved')),
  assigned_volunteer_ids UUID[] NOT NULL DEFAULT '{}',
  source TEXT NOT NULL DEFAULT 'app' CHECK (source IN ('app','sms')),
  is_mock BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at TIMESTAMPTZ
);"""),
        ("incidents_status_idx", "CREATE INDEX IF NOT EXISTS incidents_status_idx ON incidents(status);"),
        ("dispatch_log table", """CREATE TABLE IF NOT EXISTS dispatch_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  incident_id UUID REFERENCES incidents(id),
  volunteer_id UUID REFERENCES volunteers(id),
  score DOUBLE PRECISION NOT NULL,
  dispatched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);"""),
        ("sectors seed", """INSERT INTO sectors (id, name, center_lat, center_lng) VALUES
  ('SEC-01','Sangam Nose',  25.4244,81.8846),
  ('SEC-02','Triveni Ghat', 25.4358,81.8836),
  ('SEC-03','Parade Ground',25.4484,81.8661),
  ('SEC-04','Jhunsi',       25.4512,81.8340),
  ('SEC-05','Arail',        25.4125,81.9012),
  ('SEC-06','Medical Zone', 25.4390,81.8750)
ON CONFLICT (id) DO NOTHING;"""),
    ]

    for label, sql in statements:
        apply_sql(svc, sql, label)
        time.sleep(0.4)

    print("\n3. Enabling Realtime on volunteers and incidents...")
    for table in ['volunteers', 'incidents']:
        apply_sql(svc, f"ALTER PUBLICATION supabase_realtime ADD TABLE {table};", f"realtime {table}")
        time.sleep(0.3)

    print("\n4. Verifying sectors count...")
    url = f"https://{PROJECT_REF}.supabase.co/rest/v1/sectors?select=id"
    r = requests.get(url, headers={
        "apikey": svc,
        "Authorization": f"Bearer {svc}"
    })
    if r.status_code == 200:
        count = len(r.json())
        print(f"  ✓ {count} sectors in database")
        if count != 6:
            print(f"  WARNING: expected 6 sectors, got {count}")
    else:
        print(f"  ⚠ Could not verify sectors: {r.status_code} {r.text[:100]}")

    print("\n✓ Supabase setup complete.")

if __name__ == "__main__":
    main()
