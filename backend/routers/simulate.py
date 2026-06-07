"""
Simulation router — creates 50 mock volunteers + 15 pre-written incidents.
NO LLM calls. All incident data is pre-written.
"""
import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fastapi import APIRouter
from db.supabase_client import get_supabase
from services.dispatch import dispatch_volunteers
from constants.sectors import SECTORS, SKILLS, LANGUAGES

router = APIRouter(prefix="/api/simulate", tags=["simulate"])

MOCK_INCIDENTS = [
    {"raw_text": "Elderly man collapsed at Sangam Nose, unconscious", "severity": "CRITICAL",
     "category": "medical", "required_skills": ["first_aid"], "summary": "Elderly man collapsed unconscious", "sector_id": "SEC-01"},
    {"raw_text": "Child drowning near Triveni Ghat riverbank", "severity": "CRITICAL",
     "category": "medical", "required_skills": ["first_aid"], "summary": "Child drowning riverbank", "sector_id": "SEC-02"},
    {"raw_text": "Stampede at Parade Ground main gate, multiple injuries", "severity": "CRITICAL",
     "category": "medical", "required_skills": ["first_aid", "crowd_management"], "summary": "Stampede multiple injuries gate", "sector_id": "SEC-03"},
    {"raw_text": "Massive crowd surge blocking exit at Jhunsi", "severity": "HIGH",
     "category": "crowd_control", "required_skills": ["crowd_management"], "summary": "Crowd surge blocking exit", "sector_id": "SEC-04"},
    {"raw_text": "Aggressive crowd at Arail food distribution point", "severity": "HIGH",
     "category": "crowd_control", "required_skills": ["crowd_management"], "summary": "Aggressive crowd food point", "sector_id": "SEC-05"},
    {"raw_text": "Pilgrims stuck in bottleneck near Medical Zone entry", "severity": "HIGH",
     "category": "crowd_control", "required_skills": ["crowd_management"], "summary": "Pilgrims stuck entry bottleneck", "sector_id": "SEC-06"},
    {"raw_text": "Large crowd blocking ambulance route at Sector 1", "severity": "HIGH",
     "category": "crowd_control", "required_skills": ["crowd_management"], "summary": "Crowd blocking ambulance route", "sector_id": "SEC-01"},
    {"raw_text": "Minor slip and fall near Triveni Ghat steps", "severity": "MEDIUM",
     "category": "general", "required_skills": ["first_aid"], "summary": "Slip and fall Triveni steps", "sector_id": "SEC-02"},
    {"raw_text": "Temporary barricade collapsed at Parade Ground", "severity": "MEDIUM",
     "category": "infrastructure", "required_skills": ["fire_safety"], "summary": "Barricade collapsed parade ground", "sector_id": "SEC-03"},
    {"raw_text": "Toilet block overflowing near Jhunsi camp", "severity": "MEDIUM",
     "category": "infrastructure", "required_skills": [], "summary": "Toilet block overflowing Jhunsi", "sector_id": "SEC-04"},
    {"raw_text": "Elderly pilgrim needs translation assistance at Arail", "severity": "MEDIUM",
     "category": "general", "required_skills": ["translation"], "summary": "Elderly pilgrim needs translation", "sector_id": "SEC-05"},
    {"raw_text": "Suspicious unattended bag at Medical Zone checkpoint", "severity": "MEDIUM",
     "category": "infrastructure", "required_skills": ["fire_safety"], "summary": "Unattended bag at checkpoint", "sector_id": "SEC-06"},
    {"raw_text": "Lost child approximately 8 years old near Sangam Nose info desk", "severity": "LOW",
     "category": "lost_found", "required_skills": ["info_desk"], "summary": "Lost child near info desk", "sector_id": "SEC-01"},
    {"raw_text": "Pilgrim lost their group at Triveni Ghat, speaking Tamil only", "severity": "LOW",
     "category": "lost_found", "required_skills": ["info_desk", "translation"], "summary": "Lost pilgrim Tamil speaker", "sector_id": "SEC-02"},
    {"raw_text": "Devotee lost wallet and ID near Parade Ground entrance", "severity": "LOW",
     "category": "lost_found", "required_skills": ["info_desk"], "summary": "Lost wallet and ID", "sector_id": "SEC-03"},
]


@router.post("/run")
async def run_simulation():
    """Create 50 mock volunteers + 15 incidents, dispatch all. NO LLM calls."""
    db = get_supabase()
    from constants.sectors import SECTOR_BY_ID

    # Create 50 mock volunteers spread across sectors
    volunteers = []
    for i in range(50):
        sector = SECTORS[i % len(SECTORS)]
        skills_sample = random.sample(SKILLS, k=random.randint(1, 3))
        langs_sample = random.sample(LANGUAGES, k=random.randint(1, 3))
        volunteers.append({
            "name": f"MockVol-{i+1:02d}",
            "phone": f"+9190000{i+1:05d}",
            "skills": skills_sample,
            "languages": langs_sample,
            "sector_id": sector["id"],
            "status": "active_idle",
            "hours_worked": round(random.uniform(0, 6), 1),
            "is_mock": True,
        })

    vol_result = db.table("volunteers").insert(volunteers).execute()
    created_vols = len(vol_result.data)

    # Create 15 mock incidents from pre-written data (NO LLM)
    incidents = []
    for inc in MOCK_INCIDENTS:
        sector = SECTOR_BY_ID[inc["sector_id"]]
        incidents.append({
            "raw_text": inc["raw_text"],
            "severity": inc["severity"],
            "category": inc["category"],
            "required_skills": inc["required_skills"],
            "summary": inc["summary"],
            "sector_id": inc["sector_id"],
            "location_lat": sector["lat"],
            "location_lng": sector["lng"],
            "status": "reported",
            "source": "app",
            "is_mock": True,
        })

    inc_result = db.table("incidents").insert(incidents).execute()
    created_incidents = inc_result.data

    # Dispatch all incidents
    total_dispatched = 0
    for inc in created_incidents:
        try:
            dispatched = dispatch_volunteers(inc["id"])
            total_dispatched += len(dispatched)
        except Exception:
            pass

    return {
        "volunteers_created": created_vols,
        "incidents_created": len(created_incidents),
        "volunteers_dispatched": total_dispatched,
        "message": f"Simulation complete: {created_vols} volunteers, {len(created_incidents)} incidents, {total_dispatched} dispatches",
    }


@router.delete("/clear")
async def clear_simulation():
    """Remove all is_mock=true records."""
    db = get_supabase()
    db.table("dispatch_log").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    db.table("incidents").delete().eq("is_mock", True).execute()
    db.table("volunteers").delete().eq("is_mock", True).execute()
    return {"message": "All mock data cleared"}


@router.get("/stats")
async def simulation_stats():
    """Return current simulation statistics."""
    db = get_supabase()
    vols = db.table("volunteers").select("status", count="exact").execute()
    incs = db.table("incidents").select("status", count="exact").execute()
    return {
        "total_volunteers": len(vols.data),
        "total_incidents": len(incs.data),
    }
