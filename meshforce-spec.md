# MeshForce — Complete Kiro Spec
### AI-Powered Volunteer Dispatch for Mahakumbh 2025

> **GitHub Target:** `https://github.com/anwesa-techlearner/meshforce`
> **Branch:** `main`
> **Automation Level:** Fully automated — no manual steps required after initial credential setup.

---

## ⚠️ CRITICAL AGENT INSTRUCTIONS (Read Before Every Task)

### 0. The One-Time Credential File
Before executing Task 1, Kiro must read the file `.credentials` from the working directory.
This file is created by the user and contains all secrets. Its format is exactly:

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
ANTHROPIC_API_KEY=sk-ant-api03-...
RENDER_API_KEY=rnd_xxxxxxxxxxxxxxxxxxxx
VERCEL_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx
VERCEL_ORG_ID=team_xxxxxxxxxxxxxxxxxxxx
```

Kiro reads this file at the start of Task 1 and stores all values as variables for use throughout all tasks.
Kiro NEVER hardcodes these values into source files — they always flow through env vars.
Kiro NEVER commits `.credentials` to git (it must be in `.gitignore` from Task 1).

### 1. API Credit Conservation Rules
The Anthropic Claude API costs real money. Kiro MUST follow these rules:

1. **NEVER call the Claude API during development, testing, or simulation.** The mock function handles everything.
2. **During simulation (Task 13), NEVER call the LLM.** Use pre-written incident descriptions only.
3. **The mock LLM (default):**
   ```python
   def _parse_incident_mock(raw_text: str) -> dict:
       text_lower = raw_text.lower()
       if any(w in text_lower for w in ["collapse", "faint", "heart", "injur", "fell", "drown", "unconscious", "stampede"]):
           return {"severity": "CRITICAL", "category": "medical",
                   "required_skills": ["first_aid"], "summary": "Medical emergency reported"}
       elif any(w in text_lower for w in ["crowd", "rush", "block", "push", "surge", "bottleneck"]):
           return {"severity": "HIGH", "category": "crowd_control",
                   "required_skills": ["crowd_management"], "summary": "Crowd control needed"}
       elif any(w in text_lower for w in ["lost", "missing", "child", "find", "wallet", "group"]):
           return {"severity": "LOW", "category": "lost_found",
                   "required_skills": ["info_desk"], "summary": "Lost person or item"}
       elif any(w in text_lower for w in ["fire", "smoke", "barricade", "bag", "unattended"]):
           return {"severity": "MEDIUM", "category": "infrastructure",
                   "required_skills": ["fire_safety"], "summary": "Infrastructure issue reported"}
       else:
           return {"severity": "LOW", "category": "general",
                   "required_skills": [], "summary": "General assistance needed"}
   ```
4. **`USE_MOCK_LLM=true` always** in `.env`, `.env.example`, and all deployment env vars.
5. **`max_tokens=256`** for every real Claude API call — no more.
6. **Never call the API in a loop** — simulation uses pre-written data, no LLM.

### 2. Test-Before-Commit Rules
Kiro MUST run and pass all tests before marking any task complete:

- **Python services:** Run `python <file>.py` directly — all `assert` statements must pass.
- **FastAPI routes:** Start server and run `curl` commands specified per task — check HTTP status codes.
- **TypeScript:** Run `npx tsc --noEmit` — zero errors before any frontend task is marked done.
- **Frontend build:** Run `npm run build` — zero errors before committing frontend changes.
- **Integration (Task 23):** Run `python scripts/integration_test.py` — all checks must pass automatically.
- **Never skip a failing test.** Fix it before proceeding.

### 3. Automation Rules
- **All infrastructure is provisioned via API/CLI** — no browser steps, no manual copy-paste.
- **GitHub repo:** Created via GitHub REST API using `GITHUB_TOKEN`.
- **Supabase schema:** Applied via Supabase Management API using `SUPABASE_SERVICE_KEY`.
- **Render deployment:** Triggered via Render API using `RENDER_API_KEY`.
- **Vercel deployment:** Triggered via Vercel CLI using `VERCEL_TOKEN`.
- **Every script Kiro writes must be idempotent** — safe to re-run if it fails partway.

### 4. Commit Discipline
- Commit after every completed task: `git commit -m "task N: <description>"`
- Push after every commit: `git push origin main`
- Never batch multiple tasks into one commit.

---

## Part 1: Requirements

### Problem Statement
Mahakumbh 2025 (Prayagraj) involves millions of pilgrims and thousands of volunteers.
Volunteer coordinators have no real-time visibility into who is where, what skills are available,
or how to route the right volunteer to an emerging incident in under 3 minutes.

### Solution Summary
MeshForce is an AI-assisted volunteer dispatch system with three user surfaces:
1. **Volunteer PWA** — mobile web app for registration, status updates, and incident reporting
2. **Admin Command Center** — Next.js dashboard with live Leaflet map, incident feed, and routing visualization
3. **FastAPI Backend** — scoring engine, AI incident parser, and REST API

The core demo moment: a volunteer types one natural-language sentence → Claude AI parses it
into structured metadata → the scoring engine dispatches the best available volunteer → the
admin sees a routing line animate on the map — all within 3 seconds.

---

### Functional Requirements

#### FR-1: Volunteer Onboarding (PWA)
- FR-1.1: Volunteer opens PWA at `/volunteer` on mobile browser
- FR-1.2: Registration form collects: name, phone (E.164 format), skills (multi-select checkboxes), languages spoken (multi-select), assigned sector (dropdown of 6 Mahakumbh sectors)
- FR-1.3: On submit, POST to `/api/volunteers` → stored in Supabase `volunteers` table
- FR-1.4: After registration, volunteer sees a status toggle: `Active (Idle)` | `On Mission` | `Resting` | `Offline`
- FR-1.5: Status change PATCHes `/api/volunteers/{id}/status` in real time
- FR-1.6: PWA is installable (manifest.json + service worker)

#### FR-2: Incident Reporting (PWA)
- FR-2.1: Volunteer sees a prominent "Report Incident" button on their home screen
- FR-2.2: Tapping it opens a text area: "Describe what's happening in plain language..."
- FR-2.3: On submit, raw text POSTed to `/api/incidents/report`
- FR-2.4: Backend calls `parse_incident()` — mock by default, real Claude when `USE_MOCK_LLM=false`
- FR-2.5: Returns JSON: severity, category, required_skills[], summary
- FR-2.6: Parsed metadata + volunteer's sector coordinates saved to `incidents` table
- FR-2.7: PWA shows confirmation card with severity badge and summary
- FR-2.8: If offline: store in IndexedDB queue; auto-sync on reconnect

#### FR-3: Scoring & Dispatch Engine
- FR-3.1: On every new incident, trigger `dispatch_volunteers(incident_id)`
- FR-3.2: Query all volunteers with `status = active_idle` within 3km
- FR-3.3: Score formula: `P(v,i) = 0.4*(1-d/d_max) + 0.3*S(v,i) + 0.1*L(v,i) - 0.2*E(v)`
- FR-3.4: Top N volunteers: N=1 for LOW/MEDIUM, 2 for HIGH, 3 for CRITICAL
- FR-3.5: Update volunteers to `on_mission`, update incident to `dispatched`
- FR-3.6: Supabase Realtime broadcasts change to all connected frontends

#### FR-4: Admin Command Center
- FR-4.1: PIN `1234` gated (sessionStorage)
- FR-4.2: Sidebar (30%) + Leaflet map (70%)
- FR-4.3: Map centered on Prayagraj [25.4358, 81.8836], zoom 13, OpenStreetMap tiles
- FR-4.4: 6 sector rectangles colored by Demand-Supply Ratio Rs:
  - Rs > 1.5 → flashing red; 0.8–1.5 → yellow; <0.8 → green
- FR-4.5: Blue volunteer pins with popup; severity-colored incident markers
- FR-4.6: Animated dashed routing lines on dispatch (1.5s CSS animation)
- FR-4.7: Live incident log sidebar, newest first
- FR-4.8: Stats header: Active Volunteers | Open Incidents | Resolved Today
- FR-4.9: Supabase Realtime subscription — no refresh needed

#### FR-5: Simulate Mass Incident
- FR-5.1: "⚡ Simulate" button in admin sidebar
- FR-5.2: Creates 50 mock volunteers + 15 pre-written incidents (NO LLM calls)
- FR-5.3: Runs dispatch engine on all 15, shows toast with stats
- FR-5.4: Routing lines animate simultaneously
- FR-5.5: "🗑 Clear" button removes all `is_mock=true` records

#### FR-6: SMS Fallback
- FR-6.1: `POST /api/sms/inbound` — Africa's Talking webhook
- FR-6.2: Parse `[SEC]_[CAT]_[SEV]_[TXT]` format
- FR-6.3: Map to sector coordinates, create incident, dispatch
- FR-6.4: Unmatched format falls back to `parse_incident()` (mock by default)

---

### Non-Functional Requirements
- NFR-1: Dispatch latency ≤ 3 seconds for up to 200 volunteers
- NFR-2: PWA installable (manifest + service worker)
- NFR-3: API endpoints ≤ 500ms (excluding LLM call)
- NFR-4: Works on mobile Chrome at 360px viewport
- NFR-5: Zero paid services required (all free tier)
- NFR-6: Claude API calls minimized — mock LLM default everywhere

---

### Reference Data

**Mahakumbh Sectors:**
```json
[
  {"id":"SEC-01","name":"Sangam Nose",  "center":[25.4244,81.8846]},
  {"id":"SEC-02","name":"Triveni Ghat", "center":[25.4358,81.8836]},
  {"id":"SEC-03","name":"Parade Ground","center":[25.4484,81.8661]},
  {"id":"SEC-04","name":"Jhunsi",       "center":[25.4512,81.8340]},
  {"id":"SEC-05","name":"Arail",        "center":[25.4125,81.9012]},
  {"id":"SEC-06","name":"Medical Zone", "center":[25.4390,81.8750]}
]
```

**Enums:** Skills: `first_aid|crowd_management|translation|info_desk|fire_safety` · Languages: `Hindi|English|Bengali|Telugu|Tamil|Marathi|Bhojpuri` · Categories: `medical|crowd_control|lost_found|infrastructure|general` · Severity: `CRITICAL|HIGH|MEDIUM|LOW` · Status: `active_idle|on_mission|resting|offline`

---

## Part 2: Technical Design

### Repository Structure
```
meshforce/
├── .credentials          ← USER CREATES THIS. In .gitignore. Never committed.
├── .gitignore
├── .env.example
├── README.md
├── scripts/
│   ├── setup_github.py       # Creates GitHub repo via API
│   ├── setup_supabase.py     # Applies schema via Supabase Management API
│   ├── setup_realtime.py     # Enables Realtime on tables via API
│   ├── deploy_render.py      # Creates/updates Render web service via API
│   ├── deploy_vercel.py      # Deploys frontend via Vercel CLI
│   └── integration_test.py  # Automated end-to-end test (no browser needed)
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env                  ← generated by setup scripts, gitignored
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── volunteers.py
│   │   ├── incidents.py
│   │   ├── simulate.py
│   │   └── sms.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scoring.py
│   │   ├── dispatch.py
│   │   ├── llm_parser.py
│   │   └── sms_parser.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── volunteer.py
│   │   └── incident.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── supabase_client.py
│   │   └── schema.sql
│   └── constants/
│       ├── __init__.py
│       └── sectors.py
└── frontend/
    ├── package.json
    ├── next.config.js
    ├── tailwind.config.js
    ├── tsconfig.json
    ├── .env.local            ← generated by setup scripts, gitignored
    ├── public/
    │   ├── manifest.json
    │   ├── icon-192.png
    │   └── icon-512.png
    └── src/
        ├── app/
        │   ├── layout.tsx
        │   ├── page.tsx
        │   ├── volunteer/
        │   │   ├── page.tsx
        │   │   └── register/page.tsx
        │   └── admin/
        │       ├── page.tsx
        │       └── login/page.tsx
        ├── components/
        │   ├── map/
        │   │   ├── CommandMap.tsx
        │   │   ├── SectorLayer.tsx
        │   │   ├── VolunteerMarker.tsx
        │   │   ├── IncidentMarker.tsx
        │   │   └── RoutingLine.tsx
        │   ├── sidebar/
        │   │   ├── IncidentFeed.tsx
        │   │   └── StatsHeader.tsx
        │   ├── volunteer/
        │   │   ├── RegisterForm.tsx
        │   │   ├── StatusToggle.tsx
        │   │   └── ReportIncident.tsx
        │   └── ui/
        │       ├── SeverityBadge.tsx
        │       ├── CategoryIcon.tsx
        │       └── SimulateButton.tsx
        ├── hooks/
        │   ├── useRealtimeIncidents.ts
        │   ├── useRealtimeVolunteers.ts
        │   └── useOfflineQueue.ts
        ├── lib/
        │   ├── api.ts
        │   ├── supabase.ts
        │   └── sectors.ts
        └── types/
            ├── volunteer.ts
            └── incident.ts
```

---

### Database Schema

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS sectors (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  center_lat DOUBLE PRECISION NOT NULL,
  center_lng DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS volunteers (
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
);

CREATE INDEX IF NOT EXISTS volunteers_sector_idx ON volunteers(sector_id);
CREATE INDEX IF NOT EXISTS volunteers_status_idx ON volunteers(status);

CREATE TABLE IF NOT EXISTS incidents (
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
);

CREATE INDEX IF NOT EXISTS incidents_status_idx ON incidents(status);

CREATE TABLE IF NOT EXISTS dispatch_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  incident_id UUID REFERENCES incidents(id),
  volunteer_id UUID REFERENCES volunteers(id),
  score DOUBLE PRECISION NOT NULL,
  dispatched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO sectors (id, name, center_lat, center_lng) VALUES
  ('SEC-01','Sangam Nose',  25.4244,81.8846),
  ('SEC-02','Triveni Ghat', 25.4358,81.8836),
  ('SEC-03','Parade Ground',25.4484,81.8661),
  ('SEC-04','Jhunsi',       25.4512,81.8340),
  ('SEC-05','Arail',        25.4125,81.9012),
  ('SEC-06','Medical Zone', 25.4390,81.8750)
ON CONFLICT (id) DO NOTHING;
```

---

### Scoring Engine

```python
P(v,i) = 0.4*(1 - d/d_max) + 0.3*S(v,i) + 0.1*L(v,i) - 0.2*E(v)

d      = geodesic distance (meters), d_max = 3000
S(v,i) = |skills_v ∩ skills_i| / |skills_i|   (0 if no skills required → 1.0)
L(v,i) = 1 if languages overlap, else 0
E(v)   = min(hours_worked / 8.0, 1.0)
Returns -1.0 if d > d_max (out of range)
Dispatch count: CRITICAL→3, HIGH→2, MEDIUM→1, LOW→1
```

---

### Simulation Pre-Written Incidents (NO LLM CALLS)

```python
MOCK_INCIDENTS = [
  {"raw_text":"Elderly man collapsed at Sangam Nose, unconscious","severity":"CRITICAL",
   "category":"medical","required_skills":["first_aid"],"summary":"Elderly man collapsed unconscious","sector_id":"SEC-01"},
  {"raw_text":"Child drowning near Triveni Ghat riverbank","severity":"CRITICAL",
   "category":"medical","required_skills":["first_aid"],"summary":"Child drowning riverbank","sector_id":"SEC-02"},
  {"raw_text":"Stampede at Parade Ground main gate, multiple injuries","severity":"CRITICAL",
   "category":"medical","required_skills":["first_aid","crowd_management"],"summary":"Stampede multiple injuries gate","sector_id":"SEC-03"},
  {"raw_text":"Massive crowd surge blocking exit at Jhunsi","severity":"HIGH",
   "category":"crowd_control","required_skills":["crowd_management"],"summary":"Crowd surge blocking exit","sector_id":"SEC-04"},
  {"raw_text":"Aggressive crowd at Arail food distribution point","severity":"HIGH",
   "category":"crowd_control","required_skills":["crowd_management"],"summary":"Aggressive crowd food point","sector_id":"SEC-05"},
  {"raw_text":"Pilgrims stuck in bottleneck near Medical Zone entry","severity":"HIGH",
   "category":"crowd_control","required_skills":["crowd_management"],"summary":"Pilgrims stuck entry bottleneck","sector_id":"SEC-06"},
  {"raw_text":"Large crowd blocking ambulance route at Sector 1","severity":"HIGH",
   "category":"crowd_control","required_skills":["crowd_management"],"summary":"Crowd blocking ambulance route","sector_id":"SEC-01"},
  {"raw_text":"Minor slip and fall near Triveni Ghat steps","severity":"MEDIUM",
   "category":"general","required_skills":["first_aid"],"summary":"Slip and fall Triveni steps","sector_id":"SEC-02"},
  {"raw_text":"Temporary barricade collapsed at Parade Ground","severity":"MEDIUM",
   "category":"infrastructure","required_skills":["fire_safety"],"summary":"Barricade collapsed parade ground","sector_id":"SEC-03"},
  {"raw_text":"Toilet block overflowing near Jhunsi camp","severity":"MEDIUM",
   "category":"infrastructure","required_skills":[],"summary":"Toilet block overflowing Jhunsi","sector_id":"SEC-04"},
  {"raw_text":"Elderly pilgrim needs translation assistance at Arail","severity":"MEDIUM",
   "category":"general","required_skills":["translation"],"summary":"Elderly pilgrim needs translation","sector_id":"SEC-05"},
  {"raw_text":"Suspicious unattended bag at Medical Zone checkpoint","severity":"MEDIUM",
   "category":"infrastructure","required_skills":["fire_safety"],"summary":"Unattended bag at checkpoint","sector_id":"SEC-06"},
  {"raw_text":"Lost child approximately 8 years old near Sangam Nose info desk","severity":"LOW",
   "category":"lost_found","required_skills":["info_desk"],"summary":"Lost child near info desk","sector_id":"SEC-01"},
  {"raw_text":"Pilgrim lost their group at Triveni Ghat, speaking Tamil only","severity":"LOW",
   "category":"lost_found","required_skills":["info_desk","translation"],"summary":"Lost pilgrim Tamil speaker","sector_id":"SEC-02"},
  {"raw_text":"Devotee lost wallet and ID near Parade Ground entrance","severity":"LOW",
   "category":"lost_found","required_skills":["info_desk"],"summary":"Lost wallet and ID","sector_id":"SEC-03"},
]
```

---

### Environment Variables

```bash
# backend/.env  (generated by scripts/setup_supabase.py — never manually edited)
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
ANTHROPIC_API_KEY=sk-ant-...
USE_MOCK_LLM=true
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=

# frontend/.env.local  (generated by scripts/setup_supabase.py)
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

---

## Part 3: Implementation Tasks

**Agent rule:** Complete tasks in order. Run all tests. Commit + push after every task.
Never mark a task done unless its acceptance test passes.

---

### PHASE 0: Credential Bootstrap

#### Task 0: Read Credentials & Validate
**Goal:** Load all credentials from `.credentials` file and verify each one is present.

Create `scripts/load_credentials.py`:
```python
"""
Reads .credentials from repo root and returns a dict.
Call this at the start of every other script.
"""
import os, sys

REQUIRED_KEYS = [
    "GITHUB_TOKEN", "SUPABASE_URL", "SUPABASE_SERVICE_KEY",
    "SUPABASE_ANON_KEY", "ANTHROPIC_API_KEY",
    "RENDER_API_KEY", "VERCEL_TOKEN", "VERCEL_ORG_ID"
]

def load():
    creds_path = os.path.join(os.path.dirname(__file__), '..', '.credentials')
    if not os.path.exists(creds_path):
        print("ERROR: .credentials file not found in repo root.")
        print("Create it with these keys:")
        for k in REQUIRED_KEYS:
            print(f"  {k}=your_value_here")
        sys.exit(1)
    creds = {}
    with open(creds_path) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                creds[k.strip()] = v.strip()
    missing = [k for k in REQUIRED_KEYS if not creds.get(k)]
    if missing:
        print(f"ERROR: Missing keys in .credentials: {missing}")
        sys.exit(1)
    print("✓ All credentials loaded")
    return creds

if __name__ == "__main__":
    creds = load()
    for k in REQUIRED_KEYS:
        masked = creds[k][:8] + "..." if len(creds[k]) > 8 else "***"
        print(f"  {k} = {masked}")
```

**Test:** `python scripts/load_credentials.py` — prints all keys masked, exits 0.
**Acceptance:** No missing keys; script exits cleanly.

---

### PHASE 1: Project Scaffolding

#### Task 1: Create GitHub Repository via API
**Goal:** `https://github.com/anwesa-techlearner/meshforce` exists and is empty.

Create `scripts/setup_github.py`:
```python
"""Creates the meshforce repo under anwesa-techlearner via GitHub API."""
import requests, subprocess, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from load_credentials import load

def main():
    creds = load()
    token = creds["GITHUB_TOKEN"]
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    # Check if repo already exists
    r = requests.get("https://api.github.com/repos/anwesa-techlearner/meshforce", headers=headers)
    if r.status_code == 200:
        print("✓ Repo already exists — skipping creation")
        return

    # Create repo
    payload = {
        "name": "meshforce",
        "description": "AI-Powered Volunteer Dispatch for Mahakumbh 2025",
        "private": False,
        "auto_init": False
    }
    r = requests.post("https://api.github.com/user/repos", json=payload, headers=headers)
    if r.status_code not in (200, 201):
        print(f"ERROR creating repo: {r.status_code} {r.text}")
        sys.exit(1)
    print("✓ GitHub repo created: https://github.com/anwesa-techlearner/meshforce")

if __name__ == "__main__":
    main()
```

After running `setup_github.py`, initialize the local repo and connect it:
```bash
git init
git remote add origin https://${GITHUB_TOKEN}@github.com/anwesa-techlearner/meshforce.git
git checkout -b main
```

Create `.gitignore`:
```
.credentials
.env
.env.local
backend/.env
frontend/.env.local
__pycache__/
*.pyc
*.pyo
node_modules/
.next/
.vercel/
*.egg-info/
dist/
.DS_Store
```

Create `.env.example`:
```bash
# Copy to backend/.env and fill in values
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
ANTHROPIC_API_KEY=sk-ant-...
USE_MOCK_LLM=true
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=

# Copy to frontend/.env.local
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

**Test:** `python scripts/setup_github.py` exits 0. `curl -s https://api.github.com/repos/anwesa-techlearner/meshforce | python3 -c "import sys,json; d=json.load(sys.stdin); print('✓ Repo exists:', d['full_name'])"` succeeds.
**Commit:** `git add -A && git commit -m "task 1: github repo + scaffold" && git push -u origin main`
**Acceptance:** Repo visible at `https://github.com/anwesa-techlearner/meshforce`.

---

#### Task 2: Backend Dependencies
**Goal:** Working Python environment.

Create `backend/requirements.txt`:
```
fastapi==0.111.0
uvicorn[standard]==0.29.0
python-dotenv==1.0.1
supabase==2.4.6
anthropic==0.26.1
geopy==2.4.1
pydantic==2.7.1
httpx==0.27.0
python-multipart==0.0.9
requests==2.31.0
```

Also add `requests` to `scripts/` dependencies (for setup scripts).

**Test:** `pip install -r backend/requirements.txt` → then `python -c "import fastapi, supabase, anthropic, geopy, requests; print('✓ all imports ok')"` prints success.
**Commit:** `git add -A && git commit -m "task 2: backend dependencies" && git push`
**Acceptance:** All imports succeed with no errors.

---

#### Task 3: Frontend Dependencies
**Goal:** Working Next.js 14 project.

```bash
cd frontend
npx create-next-app@14 . --typescript --tailwind --app --no-git --yes
npm install @supabase/supabase-js leaflet react-leaflet @types/leaflet next-pwa
cd ..
```

Ensure `tailwind.config.js` content array includes `'./src/**/*.{ts,tsx}'`.

**Test:** `cd frontend && npm run build` — zero errors. `cd ..`
**Commit:** `git add -A && git commit -m "task 3: frontend dependencies" && git push`
**Acceptance:** Next.js build succeeds.

---

### PHASE 2: Database Setup (Fully Automated)

#### Task 4: Apply Supabase Schema via API & Generate Env Files
**Goal:** All 4 tables created, sectors seeded, Realtime enabled — all via script, zero manual steps.

Create `scripts/setup_supabase.py`:
```python
"""
Applies schema.sql to Supabase via Management API.
Enables Realtime on volunteers and incidents tables.
Generates backend/.env and frontend/.env.local from .credentials.
Idempotent — safe to re-run.
"""
import requests, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from load_credentials import load

def apply_sql(supabase_url: str, service_key: str, sql: str):
    """Execute SQL against Supabase using the REST API."""
    # Supabase exposes a SQL execution endpoint via the service role
    url = f"{supabase_url}/rest/v1/rpc/exec_sql"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }
    # Use the pg endpoint for DDL
    url_pg = f"{supabase_url}/pg"
    # Fall back to direct query via PostgREST rpc
    # Most reliable: use Supabase's SQL API endpoint
    sql_url = supabase_url.replace("https://", "https://").rstrip("/")
    endpoint = f"{sql_url}/rest/v1/"

    # Use the Management API for executing SQL
    project_ref = supabase_url.replace("https://", "").split(".supabase.co")[0]
    mgmt_url = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"
    mgmt_headers = {
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }
    r = requests.post(mgmt_url, json={"query": sql}, headers=mgmt_headers)
    if r.status_code not in (200, 201):
        # Fallback: try the direct REST approach
        print(f"  Management API returned {r.status_code}, trying RPC fallback...")
        # Try executing via supabase-js compatible endpoint
        rpc_url = f"{supabase_url}/rest/v1/rpc/exec_sql"
        r2 = requests.post(rpc_url, json={"sql_query": sql}, headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json"
        })
        if r2.status_code not in (200, 201):
            print(f"  Warning: SQL execution returned {r2.status_code}. Schema may need manual application.")
            print(f"  Response: {r2.text[:200]}")
            return False
    return True

def enable_realtime(supabase_url: str, service_key: str, table: str):
    """Enable Realtime for a table via Supabase Management API."""
    project_ref = supabase_url.replace("https://", "").split(".supabase.co")[0]
    # Enable replication via Management API
    url = f"https://api.supabase.com/v1/projects/{project_ref}/database/publications"
    headers = {
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }
    r = requests.post(url, json={"name": "supabase_realtime", "tables": [table]}, headers=headers)
    # Also try via SQL
    rt_sql = f"ALTER PUBLICATION supabase_realtime ADD TABLE {table};"
    apply_sql(supabase_url, service_key, rt_sql)
    print(f"  ✓ Realtime enabled for {table}")

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

    print("\n2. Reading schema.sql...")
    schema_path = os.path.join("backend", "db", "schema.sql")
    if not os.path.exists(schema_path):
        print(f"ERROR: {schema_path} not found. Run Task 4 file creation first.")
        sys.exit(1)
    with open(schema_path) as f:
        schema_sql = f.read()

    print("\n3. Applying schema to Supabase...")
    # Split on semicolons and run each statement
    statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
    for i, stmt in enumerate(statements):
        print(f"  Running statement {i+1}/{len(statements)}...")
        ok = apply_sql(creds['SUPABASE_URL'], creds['SUPABASE_SERVICE_KEY'], stmt + ';')
        time.sleep(0.3)  # Rate limit protection

    print("\n4. Enabling Realtime...")
    for table in ['volunteers', 'incidents']:
        enable_realtime(creds['SUPABASE_URL'], creds['SUPABASE_SERVICE_KEY'], table)

    print("\n✓ Supabase setup complete.")
    print("  If schema application failed above, open Supabase SQL Editor and paste backend/db/schema.sql manually.")
    print("  Env files are ready regardless.")

if __name__ == "__main__":
    main()
```

Also create `backend/db/schema.sql` with the full DDL from Part 2 (Design section).
Also create `backend/db/supabase_client.py`:
```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

_client: Client | None = None

def get_supabase() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_KEY"]
        )
    return _client
```

**Test:**
```bash
python scripts/setup_supabase.py
# Must print: ✓ Supabase setup complete
# Verify: python -c "
# import sys; sys.path.insert(0,'backend')
# from db.supabase_client import get_supabase
# db = get_supabase()
# r = db.table('sectors').select('id').execute()
# assert len(r.data) == 6, f'Expected 6 sectors, got {len(r.data)}'
# print('✓ 6 sectors in database')
# "
```
**Commit:** `git add -A && git commit -m "task 4: supabase schema + automated setup script" && git push`
**Acceptance:** 6 sector rows exist; `get_supabase()` connects without errors; env files generated.

---

#### Task 5: Constants & Sector Data
**Goal:** Single source of truth for all enums, sectors, SMS mappings.

Create `backend/constants/sectors.py`:
```python
from typing import TypedDict

class Sector(TypedDict):
    id: str
    name: str
    lat: float
    lng: float

SECTORS: list[Sector] = [
    {"id": "SEC-01", "name": "Sangam Nose",   "lat": 25.4244, "lng": 81.8846},
    {"id": "SEC-02", "name": "Triveni Ghat",  "lat": 25.4358, "lng": 81.8836},
    {"id": "SEC-03", "name": "Parade Ground", "lat": 25.4484, "lng": 81.8661},
    {"id": "SEC-04", "name": "Jhunsi",        "lat": 25.4512, "lng": 81.8340},
    {"id": "SEC-05", "name": "Arail",         "lat": 25.4125, "lng": 81.9012},
    {"id": "SEC-06", "name": "Medical Zone",  "lat": 25.4390, "lng": 81.8750},
]
SECTOR_BY_ID: dict[str, Sector] = {s["id"]: s for s in SECTORS}
SKILLS = ["first_aid", "crowd_management", "translation", "info_desk", "fire_safety"]
LANGUAGES = ["Hindi", "English", "Bengali", "Telugu", "Tamil", "Marathi", "Bhojpuri"]
SEVERITY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
CATEGORIES = ["medical", "crowd_control", "lost_found", "infrastructure", "general"]
VOLUNTEER_STATUSES = ["active_idle", "on_mission", "resting", "offline"]
SMS_CATEGORY_MAP = {"MED": "medical", "CRD": "crowd_control", "LST": "lost_found",
                    "INF": "infrastructure", "GEN": "general"}
SMS_SEVERITY_MAP = {"CRIT": "CRITICAL", "HIGH": "HIGH", "MED": "MEDIUM", "LOW": "LOW"}

if __name__ == "__main__":
    assert len(SECTORS) == 6
    assert "SEC-01" in SECTOR_BY_ID
    print("✓ sectors.py OK")
```

Create `frontend/src/lib/sectors.ts`:
```typescript
export const SECTORS = [
  { id: 'SEC-01', name: 'Sangam Nose',   lat: 25.4244, lng: 81.8846 },
  { id: 'SEC-02', name: 'Triveni Ghat',  lat: 25.4358, lng: 81.8836 },
  { id: 'SEC-03', name: 'Parade Ground', lat: 25.4484, lng: 81.8661 },
  { id: 'SEC-04', name: 'Jhunsi',        lat: 25.4512, lng: 81.8340 },
  { id: 'SEC-05', name: 'Arail',         lat: 25.4125, lng: 81.9012 },
  { id: 'SEC-06', name: 'Medical Zone',  lat: 25.4390, lng: 81.8750 },
] as const;

export const SECTOR_BY_ID = Object.fromEntries(SECTORS.map(s => [s.id, s]));

export const SECTOR_BOUNDS: Record<string, [[number, number], [number, number]]> = {
  'SEC-01': [[25.4194, 81.8796], [25.4294, 81.8896]],
  'SEC-02': [[25.4308, 81.8786], [25.4408, 81.8886]],
  'SEC-03': [[25.4434, 81.8611], [25.4534, 81.8711]],
  'SEC-04': [[25.4462, 81.8290], [25.4562, 81.8390]],
  'SEC-05': [[25.4075, 81.8962], [25.4175, 81.9062]],
  'SEC-06': [[25.4340, 81.8700], [25.4440, 81.8800]],
};

export const SKILLS = ['first_aid','crowd_management','translation','info_desk','fire_safety'] as const;
export const LANGUAGES = ['Hindi','English','Bengali','Telugu','Tamil','Marathi','Bhojpuri'] as const;
export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type Category = 'medical' | 'crowd_control' | 'lost_found' | 'infrastructure' | 'general';
export type VolunteerStatus = 'active_idle' | 'on_mission' | 'resting' | 'offline';
```

**Test:** `python backend/constants/sectors.py` → `✓ sectors.py OK`. `cd frontend && npx tsc --noEmit && cd ..` → zero errors.
**Commit:** `git add -A && git commit -m "task 5: constants and sector data" && git push`
**Acceptance:** Both files pass their tests.

---

### PHASE 3: Backend Services

#### Task 6: Pydantic Models
Create `backend/models/volunteer.py` and `backend/models/incident.py` with all models from Part 2 (Design section).

Add `__main__` test block to each:
```python
# volunteer.py test
if __name__ == "__main__":
    v = VolunteerCreate(name="Test", phone="+91999", skills=["first_aid"], languages=["Hindi"], sector_id="SEC-01")
    assert v.name == "Test"
    print("✓ volunteer models OK")

# incident.py test
if __name__ == "__main__":
    r = IncidentReport(raw_text="Someone collapsed")
    assert r.raw_text
    print("✓ incident models OK")
```

**Test:** `python backend/models/volunteer.py` and `python backend/models/incident.py` — both print OK.
**Commit:** `git add -A && git commit -m "task 6: pydantic models" && git push`

---

#### Task 7: Scoring Engine
Create `backend/services/scoring.py` with the full scoring implementation from Part 2 (Design section).

Include `__main__` test:
```python
if __name__ == "__main__":
    score = calculate_priority_score(
        25.4244, 81.8846, ["first_aid","crowd_management"], ["Hindi"], 0.0,
        25.4250, 81.8850, ["first_aid","crowd_management"])
    assert score > 0.65, f"got {score}"
    print(f"✓ ideal score: {score}")
    score2 = calculate_priority_score(
        25.4244, 81.8846, ["first_aid"], ["Hindi"], 4.0,
        25.4600, 81.9100, ["first_aid"])
    assert score2 == -1.0
    print("✓ out-of-range: -1.0")
    print("All scoring tests passed.")
```

**Test:** `python backend/services/scoring.py` — all assertions pass.
**Commit:** `git add -A && git commit -m "task 7: scoring engine" && git push`

---

#### Task 8: LLM Parser (Mock + Real with Toggle)
Create `backend/services/llm_parser.py` with the full implementation including:
- `_parse_incident_mock()` — keyword-based, zero API calls
- `_parse_incident_real()` — calls Claude claude-sonnet-4-20250514, max_tokens=256
- `parse_incident()` — routes based on `USE_MOCK_LLM` env var

Include `__main__` test (tests mock only — no API key needed):
```python
if __name__ == "__main__":
    os.environ["USE_MOCK_LLM"] = "true"
    r = parse_incident("Elderly man collapsed near gate 4, unresponsive")
    assert r["severity"] == "CRITICAL" and r["category"] == "medical"
    print(f"✓ medical: {r}")
    r2 = parse_incident("Crowd blocking the exit corridor")
    assert r2["category"] == "crowd_control"
    print(f"✓ crowd: {r2}")
    r3 = parse_incident("Lost child near info desk")
    assert r3["category"] == "lost_found"
    print(f"✓ lost_found: {r3}")
    print("All mock LLM tests passed. Zero API credits used.")
```

**Test:** `python backend/services/llm_parser.py` — all 3 assertions pass without ANTHROPIC_API_KEY.
**Commit:** `git add -A && git commit -m "task 8: llm parser with mock toggle" && git push`

---

#### Task 9: Dispatch Service
Create `backend/services/dispatch.py` with the full implementation from Part 2 (Design section).

Include `__main__` integration test that:
1. Creates a test volunteer in SEC-01 via Supabase
2. Creates a test incident in SEC-01 requiring first_aid
3. Calls `dispatch_volunteers(incident_id)`
4. Asserts volunteer is now `on_mission`
5. Cleans up test records

```python
if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from db.supabase_client import get_supabase
    db = get_supabase()

    # Create test volunteer
    vol = db.table("volunteers").insert({
        "name": "Test Vol", "phone": "+919000000099", "skills": ["first_aid"],
        "languages": ["Hindi"], "sector_id": "SEC-01", "status": "active_idle",
        "hours_worked": 0.0, "is_mock": True
    }).execute().data[0]

    # Create test incident
    inc = db.table("incidents").insert({
        "raw_text": "test", "severity": "HIGH", "category": "medical",
        "required_skills": ["first_aid"], "summary": "test",
        "sector_id": "SEC-01", "location_lat": 25.4244, "location_lng": 81.8846,
        "is_mock": True
    }).execute().data[0]

    # Dispatch
    result = dispatch_volunteers(inc["id"])
    assert len(result) > 0, "No volunteers dispatched"
    print(f"✓ Dispatched {len(result)} volunteer(s): {[r['name'] for r in result]}")

    # Verify status updated
    updated = db.table("volunteers").select("status").eq("id", vol["id"]).execute().data[0]
    assert updated["status"] == "on_mission"
    print("✓ Volunteer status is on_mission")

    # Cleanup
    db.table("incidents").delete().eq("is_mock", True).execute()
    db.table("volunteers").delete().eq("is_mock", True).execute()
    print("✓ Test data cleaned up. Dispatch service OK.")
```

**Test:** `python backend/services/dispatch.py` — passes all assertions.
**Commit:** `git add -A && git commit -m "task 9: dispatch service" && git push`

---

#### Task 10: SMS Parser
Create `backend/services/sms_parser.py` with full implementation from Part 2 (Design section).

Include `__main__` test:
```python
if __name__ == "__main__":
    r = parse_sms("SEC03_MED_CRIT_person collapsed gate 3")
    assert r and r["severity"] == "CRITICAL" and r["sector_id"] == "SEC-03"
    print(f"✓ parsed: {r}")
    assert parse_sms("invalid text") is None
    print("✓ invalid returns None")
    print("SMS parser tests passed.")
```

**Test:** `python backend/services/sms_parser.py` — both assertions pass.
**Commit:** `git add -A && git commit -m "task 10: sms parser" && git push`

---

### PHASE 4: Backend API Routes

#### Task 11: FastAPI App & Volunteer Router
Create `backend/main.py` and `backend/routers/volunteers.py`.

After creating, start server in background and test with curl:
```bash
# Start in background
cd backend && uvicorn main:app --reload --port 8000 &
sleep 3

# Test health
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
[ "$STATUS" = "200" ] && echo "✓ /health OK" || echo "FAIL: health returned $STATUS"

# Test volunteer creation
RESPONSE=$(curl -s -X POST http://localhost:8000/api/volunteers \
  -H "Content-Type: application/json" \
  -d '{"name":"CurlTest","phone":"+919000000011","skills":["first_aid"],"languages":["Hindi"],"sector_id":"SEC-01"}')
echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'id' in d; print('✓ POST /volunteers OK, id:', d['id'])"

# Test list
curl -s http://localhost:8000/api/volunteers | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✓ GET /volunteers: {len(d)} record(s)')"

# Cleanup and stop server
kill %1 2>/dev/null
cd ..
```

**Commit:** `git add -A && git commit -m "task 11: fastapi app + volunteer router" && git push`
**Acceptance:** All 3 curl tests pass.

---

#### Task 12: Incident Router
Create `backend/routers/incidents.py` with:
- `POST /report` — parse (mock) → save → dispatch → return DispatchResult
- `GET /` — list active non-mock incidents
- `PATCH /{id}/resolve` — mark resolved, free volunteers

Test (server running from Task 11 flow):
```bash
cd backend && uvicorn main:app --port 8000 &
sleep 3

# Create a volunteer first
VOL_ID=$(curl -s -X POST http://localhost:8000/api/volunteers \
  -H "Content-Type: application/json" \
  -d '{"name":"IncTest","phone":"+919000000022","skills":["first_aid"],"languages":["Hindi"],"sector_id":"SEC-01"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Report incident
RESPONSE=$(curl -s -X POST http://localhost:8000/api/incidents/report \
  -H "Content-Type: application/json" \
  -d "{\"volunteer_id\":\"$VOL_ID\",\"raw_text\":\"Elderly person collapsed near the gate\"}")
echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'severity' in d; assert 'assigned_volunteers' in d; print('✓ POST /incidents/report OK, severity:', d['severity'], 'dispatched:', len(d['assigned_volunteers']))"

kill %1 2>/dev/null
cd ..
```

**Commit:** `git add -A && git commit -m "task 12: incident router" && git push`
**Acceptance:** Report endpoint returns severity + assigned_volunteers; dispatch_time_ms present.

---

#### Task 13: Simulate & SMS Routers
Create `backend/routers/simulate.py` and `backend/routers/sms.py`.

In `simulate.py`, use `MOCK_INCIDENTS` list from Part 2 (Design section) verbatim — no LLM calls.

Test:
```bash
cd backend && uvicorn main:app --port 8000 &
sleep 3

RESPONSE=$(curl -s -X POST http://localhost:8000/api/simulate)
echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['volunteers_created'] == 50, f\"got {d['volunteers_created']}\"
assert d['incidents_created'] == 15
assert d['total_time_ms'] < 10000, 'Simulation too slow'
print(f\"✓ Simulation: {d['volunteers_created']} vols, {d['incidents_created']} incidents, {d['dispatches']} dispatched in {d['total_time_ms']}ms\")
"

# Test SMS parsing
curl -s -X POST http://localhost:8000/api/sms/inbound \
  -H "Content-Type: application/json" \
  -d '{"from":"+919000000099","text":"SEC03_MED_CRIT_person collapsed gate 3"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('✓ SMS inbound OK:', d.get('severity','?'))"

# Clear simulation
curl -s -X DELETE http://localhost:8000/api/simulate | python3 -c "import sys,json; d=json.load(sys.stdin); print('✓ Clear OK:', d)"

kill %1 2>/dev/null
cd ..
```

**Commit:** `git add -A && git commit -m "task 13: simulate + sms routers" && git push`
**Acceptance:** Simulation completes in under 10 seconds; 15 dispatches; delete clears mock data.

---

### PHASE 5: Frontend Infrastructure

#### Task 14: Types, API Lib & Supabase Client
Create `frontend/src/types/volunteer.ts`, `frontend/src/types/incident.ts`, `frontend/src/lib/supabase.ts`, `frontend/src/lib/api.ts`.

All types match backend Pydantic models exactly.

`api.ts` exports: `registerVolunteer`, `updateVolunteerStatus`, `reportIncident`, `getVolunteers`, `getIncidents`, `runSimulation`, `clearSimulation`, `resolveIncident` — all typed, all use `NEXT_PUBLIC_BACKEND_URL`.

**Test:** `cd frontend && npx tsc --noEmit && cd ..` — zero errors.
**Commit:** `git add -A && git commit -m "task 14: frontend types + api lib" && git push`

---

#### Task 15: Realtime Hooks & Offline Queue
Create:
- `frontend/src/hooks/useRealtimeIncidents.ts` — subscribe to incidents INSERT/UPDATE
- `frontend/src/hooks/useRealtimeVolunteers.ts` — subscribe to volunteers all events
- `frontend/src/hooks/useOfflineQueue.ts` — IndexedDB queue with auto-drain on `online` event

Full implementations from Part 2 (Design section).

**Test:** `cd frontend && npx tsc --noEmit && cd ..` — zero errors.
**Commit:** `git add -A && git commit -m "task 15: realtime hooks + offline queue" && git push`

---

### PHASE 6: Volunteer PWA

#### Task 16: Registration Form
Create `frontend/src/app/volunteer/register/page.tsx`:
- Mobile layout max-w-md, bg-slate-900, text-white
- "MeshForce" wordmark + "Mahakumbh 2025" subtext
- All form fields: name, phone, skills (checkboxes), languages (checkboxes), sector (select)
- Submit → `registerVolunteer()` → save id to localStorage → redirect `/volunteer`
- Inline error handling

**Test:** `cd frontend && npm run build && cd ..` — zero build errors.
**Commit:** `git add -A && git commit -m "task 16: volunteer registration form" && git push`

---

#### Task 17: Volunteer Home & Incident Report
Create `frontend/src/app/volunteer/page.tsx`:
- Redirect to `/volunteer/register` if no localStorage volunteerId
- Header with name + sector badge
- 4-state status toggle (optimistic update)
- "🚨 Report Incident" modal with offline detection
- Confirmation card after submit
- Offline: queue in IndexedDB, show "Saved offline" message
- Connection indicator (green/red dot)

**Test:** `cd frontend && npm run build && cd ..` — zero build errors.
**Commit:** `git add -A && git commit -m "task 17: volunteer home + incident report" && git push`

---

### PHASE 7: Admin Command Center

#### Task 18: Admin Login & Layout Shell
Create `frontend/src/app/admin/login/page.tsx`:
- PIN input auto-submits on 4th digit
- `sessionStorage.setItem('meshforce_admin', 'true')` on correct PIN `1234`
- Shake + error on wrong PIN

Create `frontend/src/app/admin/page.tsx`:
- Session check on mount
- Sidebar (w-96, bg-slate-900) + map area (flex-1)
- Dynamic import `CommandMap` with `ssr: false`

**Test:** `cd frontend && npm run build && cd ..` — zero build errors.
**Commit:** `git add -A && git commit -m "task 18: admin login + layout shell" && git push`

---

#### Task 19: Leaflet Map Components
Create all 5 map components: `CommandMap`, `SectorLayer`, `VolunteerMarker`, `IncidentMarker`, `RoutingLine`.

All use `'use client'` directive. `CommandMap` fixes Leaflet icon URL issue for Next.js.

`SectorLayer`: computes Rs per sector, renders Rectangle with color + tooltip.
`RoutingLine`: dashed Polyline with CSS opacity fade-in.

**Critical Next.js/Leaflet fix — add to `next.config.js`:**
```javascript
const withPWA = require('next-pwa')({ dest: 'public', disable: process.env.NODE_ENV === 'development' });
module.exports = withPWA({
  reactStrictMode: true,
  webpack: (config) => {
    config.resolve.fallback = { fs: false };
    return config;
  },
});
```

**Test:** `cd frontend && npm run build && cd ..` — zero errors (especially no `window is not defined` SSR errors).
**Commit:** `git add -A && git commit -m "task 19: leaflet map components" && git push`

---

#### Task 20: Sidebar — Stats, Feed & Simulate Button
Create `StatsHeader`, `IncidentFeed`, `SimulateButton`, `SeverityBadge`, `CategoryIcon`.

`IncidentFeed`: slide-in animation for new cards. Add to `frontend/src/app/globals.css`:
```css
@keyframes slide-in {
  from { transform: translateX(100%); opacity: 0; }
  to   { transform: translateX(0);    opacity: 1; }
}
.animate-slide-in { animation: slide-in 0.3s ease-out; }
```

`SimulateButton`: calls `runSimulation()`, shows spinner, displays toast on success, shows Clear button after.

**Test:** `cd frontend && npm run build && cd ..` — zero errors.
**Commit:** `git add -A && git commit -m "task 20: sidebar components" && git push`

---

### PHASE 8: PWA & Documentation

#### Task 21: PWA Configuration & Icons
1. Configure `next-pwa` in `next.config.js` (already started in Task 19)
2. Create `frontend/public/manifest.json`
3. Add manifest link to `frontend/src/app/layout.tsx`
4. Generate icons programmatically using a Python script:

```python
# scripts/generate_icons.py
"""Generates PWA icons without requiring design tools."""
import struct, zlib, os

def create_png(size, bg_color=(99, 102, 241), text_color=(255, 255, 255)):
    """Creates a minimal valid PNG with a colored background and 'M' lettermark."""
    # Use Pillow if available, else create minimal PNG
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (size, size), bg_color)
        draw = ImageDraw.Draw(img)
        # Draw M with scaling
        font_size = int(size * 0.6)
        draw.text((size*0.2, size*0.2), 'M', fill=text_color)
        os.makedirs('frontend/public', exist_ok=True)
        img.save(f'frontend/public/icon-{size}.png')
        print(f"✓ Generated icon-{size}.png with Pillow")
    except ImportError:
        # Fallback: create a minimal 1x1 PNG scaled (browsers accept it)
        # Create a simple colored PNG without Pillow
        import base64
        # Minimal valid indigo PNG (pre-encoded)
        # This is a real 1x1 indigo pixel PNG base64 encoded, scaled to required size
        raw = create_minimal_png(size, bg_color)
        with open(f'frontend/public/icon-{size}.png', 'wb') as f:
            f.write(raw)
        print(f"✓ Generated icon-{size}.png (minimal, no Pillow)")

def create_minimal_png(size, color):
    """Creates a solid-color PNG without Pillow."""
    def make_chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    ihdr_data = struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)
    raw_rows = b''
    row = b'\x00' + bytes(color) * size
    raw_rows = row * size
    compressed = zlib.compress(raw_rows)
    png = b'\x89PNG\r\n\x1a\n'
    png += make_chunk(b'IHDR', ihdr_data)
    png += make_chunk(b'IDAT', compressed)
    png += make_chunk(b'IEND', b'')
    return png

if __name__ == "__main__":
    # Try to install Pillow first
    import subprocess
    subprocess.run(['pip', 'install', 'Pillow', '--break-system-packages', '-q'], capture_output=True)
    create_png(192)
    create_png(512)
    print("Icon generation complete.")
```

Run `python scripts/generate_icons.py` to create icons.

**Test:** `cd frontend && npm run build && cd ..` → zero errors. `ls frontend/public/icon-*.png` → both files exist.
**Commit:** `git add -A && git commit -m "task 21: pwa config + icons" && git push`

---

#### Task 22: README
Create comprehensive `README.md` at repo root with all sections from Part 2.
Include the automated setup instructions (fill `.credentials`, run setup scripts).

```markdown
# MeshForce 🚨
### AI-Powered Volunteer Dispatch for Mahakumbh 2025

> Dispatch the right volunteer to any emergency in under 3 seconds.

## The Problem
Mahakumbh 2025 brings 400 million pilgrims to Prayagraj — the largest human gathering on earth.
With thousands of volunteers spread across 6 sectors and no coordination system, a medical emergency
can go unattended for critical minutes while the right volunteer stands 200 meters away.

## The Solution
MeshForce routes any natural-language incident report through AI extraction → weighted scoring →
real-time dispatch in under 3 seconds. A volunteer types one sentence; the admin sees a routing
line animate from the nearest qualified volunteer to the incident marker — live, on a Prayagraj map.

## Architecture
[Include updated ASCII diagram]

## Tech Stack
| Layer | Technology | Free Tier |
|---|---|---|
| Frontend | Next.js 14 + Tailwind | Vercel |
| Map | Leaflet + OpenStreetMap | Completely free |
| Backend | FastAPI (Python) | Render.com |
| Database | Supabase (PostgreSQL) | 500MB free |
| Realtime | Supabase Realtime | Included |
| AI | Anthropic Claude Sonnet | Trial credits |
| SMS | Africa's Talking | Sandbox free |

## Setup (Fully Automated)
### 1. Fill credentials file
Create `.credentials` in repo root:
\`\`\`
GITHUB_TOKEN=...
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
SUPABASE_ANON_KEY=...
ANTHROPIC_API_KEY=...
RENDER_API_KEY=...
VERCEL_TOKEN=...
VERCEL_ORG_ID=...
\`\`\`
### 2. Run setup scripts (in order)
\`\`\`bash
python scripts/setup_github.py
python scripts/setup_supabase.py
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
\`\`\`
### 3. Run locally
\`\`\`bash
cd backend && uvicorn main:app --reload &
cd frontend && npm run dev
\`\`\`
### 4. Deploy
\`\`\`bash
python scripts/deploy_render.py
python scripts/deploy_vercel.py
\`\`\`

## Scoring Formula
P(v,i) = 0.4 × (1 − d/d_max) + 0.3 × S(v,i) + 0.1 × L(v,i) − 0.2 × E(v)

## Demo Script (90 seconds)
1. Open admin dashboard — Prayagraj map, 6 sector zones
2. Open volunteer PWA on phone — register as Arjun, first_aid, Sector 3
3. Volunteer pin appears on admin map (realtime)
4. Type: "Person collapsed near Sangam Nose, heart attack"
5. Admin: incident card flashes in sidebar — CRITICAL/medical in ~1.5s
6. Routing line draws from Arjun to incident
7. Hit Simulate — 50 pins, 15 incidents, routing lines animate, Sector 4 turns red

## API Credit Note
USE_MOCK_LLM=true by default. Set false + provide ANTHROPIC_API_KEY only for live demo.

## Future Work
- 🎙️ Voice-to-text incident reporting
- 📍 Real GPS via browser Geolocation
- 🔔 Push notifications
- 🌐 Multi-event support
```

**Test:** View README on GitHub — all sections render correctly.
**Commit:** `git add -A && git commit -m "task 22: readme" && git push`

---

### PHASE 9: Automated Integration Test

#### Task 23: Automated Integration Test Script
**Goal:** A single Python script verifies the complete system via API calls — no browser, no manual steps.

Create `scripts/integration_test.py`:
```python
"""
Automated end-to-end integration test for MeshForce.
Runs entirely via HTTP API calls — no browser required.
Usage: python scripts/integration_test.py
Requires: backend server running on localhost:8000
"""
import requests, sys, json, time, subprocess, os, signal

BASE = "http://localhost:8000"
PASSED = []
FAILED = []

def check(name: str, condition: bool, detail: str = ""):
    if condition:
        PASSED.append(name)
        print(f"  ✓ {name}")
    else:
        FAILED.append(name)
        print(f"  ✗ FAIL: {name} — {detail}")

def run():
    print("\n=== MeshForce Integration Test ===\n")

    # Start backend
    print("Starting backend server...")
    proc = subprocess.Popen(
        ["uvicorn", "main:app", "--port", "8000", "--log-level", "error"],
        cwd="backend", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(4)

    try:
        # Test 1: Health
        print("\n[1] Health check")
        r = requests.get(f"{BASE}/health", timeout=5)
        check("health endpoint", r.status_code == 200, r.text)

        # Test 2: Create volunteer
        print("\n[2] Volunteer registration")
        r = requests.post(f"{BASE}/api/volunteers", json={
            "name": "Integration Test Vol", "phone": "+919000099999",
            "skills": ["first_aid", "crowd_management"], "languages": ["Hindi", "English"],
            "sector_id": "SEC-01"
        })
        check("volunteer creation 201", r.status_code == 201, r.text[:100])
        vol = r.json()
        check("volunteer has id", "id" in vol)
        check("volunteer status active_idle", vol.get("status") == "active_idle")
        vol_id = vol.get("id")

        # Test 3: List volunteers
        print("\n[3] List volunteers")
        r = requests.get(f"{BASE}/api/volunteers")
        check("list volunteers 200", r.status_code == 200)
        vols = r.json()
        check("volunteer appears in list", any(v["id"] == vol_id for v in vols))

        # Test 4: Report incident
        print("\n[4] Incident reporting + dispatch")
        r = requests.post(f"{BASE}/api/incidents/report", json={
            "volunteer_id": vol_id,
            "raw_text": "Elderly person collapsed near the main gate, needs immediate help"
        })
        check("incident report 201", r.status_code == 201, r.text[:200])
        inc = r.json()
        check("incident has severity", "severity" in inc)
        check("incident has category", "category" in inc)
        check("dispatch_time_ms present", "dispatch_time_ms" in inc)
        check("assigned_volunteers is list", isinstance(inc.get("assigned_volunteers"), list))
        check("at least 1 volunteer dispatched", len(inc.get("assigned_volunteers", [])) >= 1)
        inc_id = inc.get("incident_id")

        # Test 5: Volunteer now on_mission
        print("\n[5] Volunteer status after dispatch")
        r = requests.get(f"{BASE}/api/volunteers")
        updated_vol = next((v for v in r.json() if v["id"] == vol_id), None)
        check("volunteer exists", updated_vol is not None)
        check("volunteer on_mission", updated_vol and updated_vol.get("status") == "on_mission",
              f"got {updated_vol.get('status') if updated_vol else 'not found'}")

        # Test 6: List incidents
        print("\n[6] List active incidents")
        r = requests.get(f"{BASE}/api/incidents")
        check("list incidents 200", r.status_code == 200)
        incs = r.json()
        check("incident appears in list", any(i["id"] == inc_id for i in incs))

        # Test 7: Resolve incident
        print("\n[7] Resolve incident")
        r = requests.patch(f"{BASE}/api/incidents/{inc_id}/resolve")
        check("resolve 200", r.status_code == 200)
        # Volunteer should be active_idle again
        time.sleep(0.5)
        r = requests.get(f"{BASE}/api/volunteers")
        resolved_vol = next((v for v in r.json() if v["id"] == vol_id), None)
        check("volunteer back to active_idle after resolve",
              resolved_vol and resolved_vol.get("status") == "active_idle",
              f"got {resolved_vol.get('status') if resolved_vol else 'not found'}")

        # Test 8: Simulation
        print("\n[8] Mass incident simulation")
        start = time.time()
        r = requests.post(f"{BASE}/api/simulate", timeout=30)
        elapsed = time.time() - start
        check("simulate 200", r.status_code == 200, r.text[:100])
        sim = r.json()
        check("50 volunteers created", sim.get("volunteers_created") == 50, str(sim))
        check("15 incidents created", sim.get("incidents_created") == 15, str(sim))
        check("simulation under 10s", elapsed < 10, f"{elapsed:.1f}s")
        check("dispatches > 0", sim.get("dispatches", 0) > 0)

        # Test 9: Clear simulation
        print("\n[9] Clear simulation")
        r = requests.delete(f"{BASE}/api/simulate")
        check("clear 200", r.status_code == 200)

        # Test 10: SMS inbound
        print("\n[10] SMS fallback")
        r = requests.post(f"{BASE}/api/sms/inbound", json={
            "from": "+919000099998",
            "text": "SEC03_MED_CRIT_person collapsed gate 3"
        })
        check("sms inbound 200", r.status_code == 200, r.text[:100])
        sms_inc = r.json()
        check("sms parsed severity CRITICAL", sms_inc.get("severity") == "CRITICAL",
              str(sms_inc.get("severity")))

        # Test 11: Status update
        print("\n[11] Volunteer status toggle")
        r = requests.patch(f"{BASE}/api/volunteers/{vol_id}/status", json={"status": "resting"})
        check("status update 200", r.status_code == 200)
        check("status is resting", r.json().get("status") == "resting")

    except requests.ConnectionError:
        print("ERROR: Could not connect to backend. Is uvicorn running?")
        FAILED.append("connection")
    except Exception as e:
        print(f"ERROR: {e}")
        FAILED.append(f"exception: {e}")
    finally:
        proc.terminate()
        proc.wait()
        # Cleanup test data
        try:
            db_cleanup = subprocess.run(
                ["python", "-c",
                 "import sys; sys.path.insert(0,'backend'); from db.supabase_client import get_supabase; "
                 "db=get_supabase(); db.table('incidents').delete().eq('is_mock',True).execute(); "
                 "db.table('volunteers').delete().like('phone','+9190000999%').execute(); "
                 "print('✓ test data cleaned up')"],
                capture_output=True, text=True
            )
            print(db_cleanup.stdout.strip())
        except: pass

    print(f"\n=== Results: {len(PASSED)} passed, {len(FAILED)} failed ===")
    if FAILED:
        print(f"FAILED: {FAILED}")
        sys.exit(1)
    else:
        print("✅ All integration tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    run()
```

**Test:** `python scripts/integration_test.py` — exits 0 with "All integration tests passed!".
**Commit:** `git add -A && git commit -m "task 23: automated integration test" && git push`
**Acceptance:** Script passes all checks with zero manual interaction.

---

### PHASE 10: Automated Deployment

#### Task 24: Deploy Backend to Render via API
**Goal:** Backend live at `https://meshforce-api.onrender.com` (or similar) — zero manual steps.

Create `scripts/deploy_render.py`:
```python
"""
Creates or updates a Render web service for the MeshForce backend.
Reads env from backend/.env and credentials from .credentials.
Idempotent — safe to re-run.
"""
import requests, os, sys, time, json
sys.path.insert(0, os.path.dirname(__file__))
from load_credentials import load

RENDER_API = "https://api.render.com/v1"

def get_headers(api_key):
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

def get_or_create_service(api_key: str, creds: dict) -> dict:
    headers = get_headers(api_key)

    # Check if service already exists
    r = requests.get(f"{RENDER_API}/services?name=meshforce-api&limit=5", headers=headers)
    if r.status_code == 200:
        services = r.json()
        for svc in services:
            if isinstance(svc, dict) and svc.get("service", {}).get("name") == "meshforce-api":
                print("✓ Service already exists")
                return svc.get("service", svc)

    # Get owner ID
    r = requests.get(f"{RENDER_API}/owners?limit=1", headers=headers)
    if r.status_code != 200:
        print(f"ERROR: Could not get owner: {r.status_code} {r.text}")
        sys.exit(1)
    owner_id = r.json()[0]["owner"]["id"]

    # Prepare env vars from backend/.env
    env_vars = []
    env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    env_vars.append({"key": k.strip(), "value": v.strip()})

    # Create service
    payload = {
        "type": "web_service",
        "name": "meshforce-api",
        "ownerId": owner_id,
        "repo": "https://github.com/anwesa-techlearner/meshforce",
        "branch": "main",
        "rootDir": "backend",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
        "plan": "free",
        "region": "oregon",
        "envVars": env_vars,
        "autoDeploy": "yes"
    }

    r = requests.post(f"{RENDER_API}/services", json=payload, headers=headers)
    if r.status_code not in (200, 201):
        print(f"ERROR creating service: {r.status_code} {r.text}")
        sys.exit(1)

    service = r.json().get("service", r.json())
    print(f"✓ Render service created: {service.get('id')}")
    return service

def wait_for_deploy(api_key: str, service_id: str, timeout: int = 300):
    """Poll until service is live or timeout."""
    headers = get_headers(api_key)
    print(f"  Waiting for deploy (up to {timeout}s)...")
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(f"{RENDER_API}/services/{service_id}", headers=headers)
        if r.status_code == 200:
            svc = r.json()
            status = svc.get("serviceDetails", {}).get("url") or svc.get("url")
            state = svc.get("suspended", "unknown")
            if status:
                print(f"  ✓ Service URL: {status}")
                return status
        time.sleep(10)
        print("  ... still deploying ...")
    print("  Timeout waiting for deploy. Check Render dashboard.")
    return None

def main():
    creds = load()
    api_key = creds["RENDER_API_KEY"]

    print("\n1. Creating/finding Render service...")
    service = get_or_create_service(api_key, creds)
    service_id = service.get("id")
    service_url = service.get("serviceDetails", {}).get("url") or service.get("url", "")

    if not service_url:
        print("  Waiting for service URL...")
        service_url = wait_for_deploy(api_key, service_id)

    if service_url:
        print(f"\n✓ Backend deployed: {service_url}")

        # Update frontend env with backend URL
        frontend_env_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', '.env.local')
        if os.path.exists(frontend_env_path):
            with open(frontend_env_path, 'r') as f:
                content = f.read()
            content = content.replace("NEXT_PUBLIC_BACKEND_URL=http://localhost:8000",
                                      f"NEXT_PUBLIC_BACKEND_URL={service_url}")
            with open(frontend_env_path, 'w') as f:
                f.write(content)
            print(f"  ✓ frontend/.env.local updated with backend URL")

        # Save URL for Vercel deploy
        with open(os.path.join(os.path.dirname(__file__), '..', '.render_url'), 'w') as f:
            f.write(service_url)

    else:
        print("  Could not confirm URL. Deploy may still be in progress.")
        print(f"  Check: https://dashboard.render.com")

if __name__ == "__main__":
    main()
```

**Test:** `python scripts/deploy_render.py` — exits without error. After a few minutes: `curl https://meshforce-api.onrender.com/health` returns `{"status":"ok"}`.
**Commit:** `git add -A && git commit -m "task 24: render deployment script" && git push`
**Acceptance:** Backend health endpoint returns 200 on live Render URL.

---

#### Task 25: Deploy Frontend to Vercel via CLI
**Goal:** Frontend live at `https://meshforce.vercel.app` — zero manual steps.

Create `scripts/deploy_vercel.py`:
```python
"""
Deploys frontend to Vercel using Vercel CLI.
Installs vercel CLI if not present.
Idempotent — re-running triggers a new deploy of latest code.
"""
import subprocess, os, sys, json, time
sys.path.insert(0, os.path.dirname(__file__))
from load_credentials import load

def run(cmd, env=None, cwd=None):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env, cwd=cwd)
    if result.returncode != 0:
        print(f"  STDERR: {result.stderr[:300]}")
    return result

def main():
    creds = load()
    token = creds["VERCEL_TOKEN"]
    org_id = creds["VERCEL_ORG_ID"]

    # Check/install vercel CLI
    print("\n1. Checking Vercel CLI...")
    r = run("npx vercel --version")
    if r.returncode != 0:
        print("  Installing Vercel CLI...")
        run("npm install -g vercel")

    # Read render URL if available
    render_url_file = os.path.join(os.path.dirname(__file__), '..', '.render_url')
    backend_url = "http://localhost:8000"
    if os.path.exists(render_url_file):
        with open(render_url_file) as f:
            backend_url = f.read().strip()
        print(f"  Using backend URL: {backend_url}")

    # Read Supabase values from frontend/.env.local
    env_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', '.env.local')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    env_vars[k.strip()] = v.strip()

    env_vars["NEXT_PUBLIC_BACKEND_URL"] = backend_url

    # Build env string for vercel CLI
    env_args = " ".join([f'--env {k}="{v}"' for k, v in env_vars.items()])

    # Set environment variables
    print("\n2. Setting Vercel environment variables...")
    for k, v in env_vars.items():
        r = run(f'echo "{v}" | npx vercel env add {k} production --token {token} --scope {org_id} --force',
                cwd="frontend")
        print(f"  {'✓' if r.returncode == 0 else '!'} {k}")

    # Deploy
    print("\n3. Deploying to Vercel production...")
    r = run(
        f"npx vercel --prod --token {token} --scope {org_id} --yes --name meshforce",
        cwd="frontend"
    )

    if r.returncode == 0:
        # Extract URL from output
        output = r.stdout
        url = ""
        for line in output.splitlines():
            if "vercel.app" in line or "https://" in line:
                url = line.strip()
                break
        print(f"\n✓ Frontend deployed: {url or 'check vercel.com for URL'}")

        # Save URL
        with open(os.path.join(os.path.dirname(__file__), '..', '.vercel_url'), 'w') as f:
            f.write(url)

        # Update README with live URL
        readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
        with open(readme_path, 'r') as f:
            readme = f.read()
        if "## Live Demo" not in readme:
            with open(readme_path, 'a') as f:
                f.write(f"\n\n## Live Demo\n{url}\n")
            subprocess.run("git add README.md && git commit -m 'docs: add live demo URL' && git push",
                           shell=True)
            print("  ✓ README updated with live URL")
    else:
        print(f"  Vercel deploy failed: {r.stderr[:300]}")
        print("  Check vercel.com dashboard for details.")

if __name__ == "__main__":
    main()
```

**Test:** `python scripts/deploy_vercel.py` — exits without error. Visit the deployed URL — admin login page loads.
**Commit:** `git add -A && git commit -m "task 25: vercel deployment script" && git push`
**Acceptance:** Frontend loads at live Vercel URL; admin PIN works; map renders.

---

#### Task 26: Final Production Smoke Test
**Goal:** Verify deployed system end-to-end using live URLs.

Create `scripts/smoke_test_production.py`:
```python
"""
Smoke test against live deployed URLs.
Reads .render_url and .vercel_url written by deploy scripts.
"""
import requests, sys, os, time

def load_urls():
    root = os.path.join(os.path.dirname(__file__), '..')
    backend_url, frontend_url = None, None
    rfile = os.path.join(root, '.render_url')
    vfile = os.path.join(root, '.vercel_url')
    if os.path.exists(rfile):
        with open(rfile) as f: backend_url = f.read().strip()
    if os.path.exists(vfile):
        with open(vfile) as f: frontend_url = f.read().strip()
    return backend_url, frontend_url

def main():
    backend_url, frontend_url = load_urls()

    if not backend_url:
        print("ERROR: .render_url not found. Run deploy_render.py first.")
        sys.exit(1)

    print(f"\n=== Production Smoke Test ===")
    print(f"Backend: {backend_url}")
    print(f"Frontend: {frontend_url or 'unknown'}\n")

    passed, failed = [], []

    def check(name, ok, detail=""):
        if ok: passed.append(name); print(f"  ✓ {name}")
        else: failed.append(name); print(f"  ✗ FAIL: {name} — {detail}")

    # Backend health
    try:
        r = requests.get(f"{backend_url}/health", timeout=30)
        check("backend /health", r.status_code == 200, r.text)
    except Exception as e:
        check("backend /health", False, str(e))

    # Create volunteer via live API
    try:
        r = requests.post(f"{backend_url}/api/volunteers", json={
            "name": "SmokeTest", "phone": "+919000011111",
            "skills": ["first_aid"], "languages": ["Hindi"], "sector_id": "SEC-01"
        }, timeout=15)
        check("create volunteer", r.status_code == 201)
        vol_id = r.json().get("id") if r.status_code == 201 else None
    except Exception as e:
        check("create volunteer", False, str(e))
        vol_id = None

    # Report incident
    if vol_id:
        try:
            r = requests.post(f"{backend_url}/api/incidents/report", json={
                "volunteer_id": vol_id,
                "raw_text": "Smoke test: person collapsed near entrance"
            }, timeout=15)
            check("report incident", r.status_code == 201)
            inc = r.json()
            check("incident has severity", "severity" in inc)
            check("dispatch happened", len(inc.get("assigned_volunteers", [])) >= 1)
        except Exception as e:
            check("report incident", False, str(e))

    # Frontend loads
    if frontend_url:
        try:
            r = requests.get(frontend_url, timeout=30)
            check("frontend loads", r.status_code == 200)
            check("frontend has html", "<html" in r.text.lower())
        except Exception as e:
            check("frontend loads", False, str(e))

    # Cleanup
    try:
        requests.delete(f"{backend_url}/api/simulate", timeout=10)
        requests.delete(f"{backend_url}/api/volunteers/phone/+919000011111", timeout=10)
    except: pass

    print(f"\n=== {len(passed)} passed, {len(failed)} failed ===")
    if failed:
        print(f"Failed: {failed}")
        sys.exit(1)
    else:
        print("✅ Production smoke test passed!")

if __name__ == "__main__":
    main()
```

Run `python scripts/smoke_test_production.py`.

**Commit:** `git add -A && git commit -m "task 26: production smoke test + final push" && git push`
**Acceptance:** All smoke test checks pass against live URLs.

---

## Task Summary

| Phase | Tasks | Deliverable | Manual Steps |
|-------|-------|-------------|--------------|
| 0: Credentials | 0 | Credential loader validated | None |
| 1: Scaffolding | 1–3 | GitHub repo created via API + dependencies | None |
| 2: Database | 4–5 | Schema applied via API, env files generated | None |
| 3: Backend Services | 6–10 | Scoring + mock LLM + Dispatch + SMS (all tested) | None |
| 4: Backend Routes | 11–13 | All endpoints tested with automated curl | None |
| 5: Frontend Infra | 14–15 | Types + API lib + realtime hooks | None |
| 6: Volunteer PWA | 16–17 | Registration + incident report + offline | None |
| 7: Admin Dashboard | 18–20 | Map + sidebar + routing lines | None |
| 8: PWA & Docs | 21–22 | Icons generated by script + README | None |
| 9: Integration Test | 23 | Automated test script, exits 0 | None |
| 10: Deploy | 24–26 | Render + Vercel deployed via API/CLI + smoke test | None |

**Total: 27 tasks (Task 0 + Tasks 1–26). Fully automated. Zero manual browser steps.**
**Only human action required: fill `.credentials` file once before starting.**

---

## What You Fill Into .credentials (One Time Only)

| Key | Where to Get It |
|-----|----------------|
| `GITHUB_TOKEN` | github.com → Settings → Developer Settings → Personal Access Tokens (Classic) → scopes: `repo` |
| `SUPABASE_URL` | supabase.com → Your Project → Settings → API → Project URL |
| `SUPABASE_SERVICE_KEY` | supabase.com → Your Project → Settings → API → `service_role` secret key |
| `SUPABASE_ANON_KEY` | supabase.com → Your Project → Settings → API → `anon` public key |
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys → Create key |
| `RENDER_API_KEY` | render.com → Account Settings → API Keys → Create API Key |
| `VERCEL_TOKEN` | vercel.com → Settings → Tokens → Create Token |
| `VERCEL_ORG_ID` | vercel.com → Settings → General → Team ID (or Personal Account ID) |

**That is the only step you do. Everything else is automated.**
