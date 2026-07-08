# MeshForce — AI-Powered Volunteer Dispatch for Mahakumbh 2025

> Real-time volunteer coordination system with AI incident parsing, scoring engine, and live map dashboard.

**Live Demo:**
- Frontend (Vercel): https://meshforce-kiro.vercel.app
- Backend API (Render): https://meshforce-api.onrender.com/docs
- LOOM DEMO VIDEO: https://www.loom.com/share/d6f718f99ca74f8e9816a1bdd21a7d7a

---

## Architecture

```
Volunteer PWA (Next.js 14)  ←→  FastAPI Backend  ←→  Supabase (Postgres + Realtime)
                                      ↓
                               Claude AI (mock by default)
```

- **Volunteer PWA** — mobile web app at `/volunteer` for registration, status, incident reporting
- **Admin Command Center** — Next.js dashboard at `/admin` with live Leaflet map (PIN: `1234`)
- **FastAPI Backend** — scoring engine, mock LLM parser, REST API
- **Supabase** — Postgres database + Realtime subscriptions

---

## Quick Start

### 1. Fill in credentials

Create `.credentials` in repo root (never committed):
```
GITHUB_TOKEN=ghp_...
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_ANON_KEY=eyJ...
ANTHROPIC_API_KEY=sk-ant-...   (optional — mock LLM used by default)
RENDER_API_KEY=rnd_...
VERCEL_TOKEN=...
VERCEL_ORG_ID=team_...
```

### 2. Apply database schema

Open Supabase SQL Editor and run `backend/db/schema.sql`.

### 3. Run backend locally

```bash
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --port 8000
# API docs: http://localhost:8000/docs
```

### 4. Run frontend locally

```bash
cd frontend
npm install
npm run dev
# Volunteer PWA: http://localhost:3000/volunteer
# Admin dashboard: http://localhost:3000/admin  (PIN: 1234)
```

---

## Scoring Engine

```
P(v,i) = 0.4*(1 - d/d_max) + 0.3*S(v,i) + 0.1*L(v,i) - 0.2*E(v)
```

- `d` = geodesic distance (meters), `d_max` = 3000m
- `S(v,i)` = skill overlap ratio
- `L(v,i)` = language match (0 or 1)
- `E(v)` = exhaustion = min(hours_worked / 8, 1)
- Returns `-1.0` if out of range

Dispatch count: CRITICAL→3, HIGH→2, MEDIUM/LOW→1

---

## Mock LLM (Default)

`USE_MOCK_LLM=true` everywhere — zero Anthropic API cost during development and simulation.
The mock parser uses keyword matching. Set `USE_MOCK_LLM=false` to enable real Claude API.

---

## Mahakumbh Sectors

| ID | Name | Coordinates |
|----|------|-------------|
| SEC-01 | Sangam Nose | 25.4244, 81.8846 |
| SEC-02 | Triveni Ghat | 25.4358, 81.8836 |
| SEC-03 | Parade Ground | 25.4484, 81.8661 |
| SEC-04 | Jhunsi | 25.4512, 81.8340 |
| SEC-05 | Arail | 25.4125, 81.9012 |
| SEC-06 | Medical Zone | 25.4390, 81.8750 |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/volunteers` | Register volunteer |
| PATCH | `/api/volunteers/{id}/status` | Update status |
| POST | `/api/incidents/report` | Report incident (auto-dispatches) |
| GET | `/api/incidents` | List incidents |
| POST | `/api/simulate/run` | Run mass simulation (50 vols + 15 incidents) |
| DELETE | `/api/simulate/clear` | Clear all mock data |
| POST | `/api/sms/inbound` | Africa's Talking SMS webhook |
| GET | `/health` | Health check |

---

## SMS Format

```
SEC03_MED_CRIT_person collapsed at gate 3
```

Format: `SECXX_CATEGORY_SEVERITY_description`

Category codes: `MED` `CRD` `LST` `INF` `GEN`
Severity codes: `CRIT` `HIGH` `MED` `LOW`

---

## Deployment

```bash
# Deploy backend to Render
python scripts/deploy_render.py

# Deploy frontend to Vercel
python scripts/deploy_vercel.py
```

Both scripts are idempotent and fully automated via API.

---

## Project Structure

```
meshforce/
├── backend/
│   ├── main.py              FastAPI app
│   ├── routers/             API route handlers
│   ├── services/            scoring, dispatch, llm_parser, sms_parser
│   ├── models/              Pydantic models
│   ├── db/                  Supabase client + schema.sql
│   └── constants/           sector data, enums
├── frontend/
│   ├── src/app/             Next.js pages (volunteer, admin)
│   ├── src/components/      map, sidebar, ui components
│   ├── src/hooks/           realtime + offline queue hooks
│   └── src/lib/             api client, supabase client, sectors
└── scripts/
    ├── load_credentials.py
    ├── setup_github.py
    ├── setup_supabase.py
    ├── deploy_render.py
    ├── deploy_vercel.py
    └── integration_test.py
```
