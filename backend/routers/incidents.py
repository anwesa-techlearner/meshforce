"""Incident reporting and management routes."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fastapi import APIRouter, HTTPException
from db.supabase_client import get_supabase
from models.incident import IncidentReport, DispatchResult
from services.llm_parser import parse_incident
from services.dispatch import dispatch_volunteers
from constants.sectors import SECTOR_BY_ID

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.post("/report")
async def report_incident(body: IncidentReport):
    """
    Accept raw incident text, parse it (mock by default), save to DB, dispatch volunteers.
    """
    db = get_supabase()

    # Parse incident using mock LLM (or real if USE_MOCK_LLM=false)
    parsed = parse_incident(body.raw_text)

    # Determine location from sector
    sector_id = body.sector_id or "SEC-01"
    sector = SECTOR_BY_ID.get(sector_id, SECTOR_BY_ID["SEC-01"])

    # Save to incidents table
    inc_data = {
        "raw_text": body.raw_text,
        "severity": parsed["severity"],
        "category": parsed["category"],
        "required_skills": parsed["required_skills"],
        "summary": parsed["summary"],
        "sector_id": sector_id,
        "location_lat": sector["lat"],
        "location_lng": sector["lng"],
        "status": "reported",
        "source": "app",
        "is_mock": False,
    }
    if body.reported_by:
        inc_data["reported_by"] = body.reported_by

    result = db.table("incidents").insert(inc_data).execute()
    incident = result.data[0]

    # Dispatch volunteers
    try:
        dispatched = dispatch_volunteers(incident["id"])
    except Exception as e:
        dispatched = []

    return {
        "incident": incident,
        "parsed": parsed,
        "dispatched_volunteers": dispatched,
        "message": f"Incident reported. {len(dispatched)} volunteer(s) dispatched.",
    }


@router.get("")
async def list_incidents(status: str | None = None, sector_id: str | None = None):
    db = get_supabase()
    q = db.table("incidents").select("*").order("created_at", desc=True)
    if status:
        q = q.eq("status", status)
    if sector_id:
        q = q.eq("sector_id", sector_id)
    result = q.execute()
    return result.data


@router.get("/{incident_id}")
async def get_incident(incident_id: str):
    db = get_supabase()
    result = db.table("incidents").select("*").eq("id", incident_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Incident not found")
    return result.data[0]


@router.patch("/{incident_id}/resolve")
async def resolve_incident(incident_id: str):
    from datetime import datetime, timezone
    db = get_supabase()
    result = db.table("incidents").update({
        "status": "resolved",
        "resolved_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", incident_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Incident not found")
    # Free up assigned volunteers
    incident = result.data[0]
    for vid in incident.get("assigned_volunteer_ids") or []:
        db.table("volunteers").update({"status": "active_idle", "active_mission_id": None}).eq("id", vid).execute()
    return result.data[0]
