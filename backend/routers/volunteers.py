"""Volunteer CRUD and status management routes."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fastapi import APIRouter, HTTPException
from db.supabase_client import get_supabase
from models.volunteer import VolunteerCreate, VolunteerStatusPatch
from constants.sectors import SECTOR_BY_ID

router = APIRouter(prefix="/volunteers", tags=["volunteers"])


@router.post("", status_code=201)
async def create_volunteer(body: VolunteerCreate):
    db = get_supabase()
    try:
        result = db.table("volunteers").insert({
            "name": body.name,
            "phone": body.phone,
            "skills": body.skills,
            "languages": body.languages,
            "sector_id": body.sector_id,
            "status": "active_idle",
            "hours_worked": 0.0,
            "is_mock": False,
        }).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_volunteers(status: str | None = None, sector_id: str | None = None):
    db = get_supabase()
    q = db.table("volunteers").select("*")
    if status:
        q = q.eq("status", status)
    if sector_id:
        q = q.eq("sector_id", sector_id)
    result = q.execute()
    return result.data


@router.get("/{volunteer_id}")
async def get_volunteer(volunteer_id: str):
    db = get_supabase()
    result = db.table("volunteers").select("*").eq("id", volunteer_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    return result.data[0]


@router.patch("/{volunteer_id}/status")
async def update_status(volunteer_id: str, body: VolunteerStatusPatch):
    valid_statuses = ["active_idle", "on_mission", "resting", "offline"]
    if body.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    db = get_supabase()
    result = db.table("volunteers").update({"status": body.status}).eq("id", volunteer_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    return result.data[0]


@router.delete("/{volunteer_id}", status_code=204)
async def delete_volunteer(volunteer_id: str):
    db = get_supabase()
    db.table("volunteers").delete().eq("id", volunteer_id).execute()
    return None
