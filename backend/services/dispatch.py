"""
Dispatch service: finds best volunteers for an incident and assigns them.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from db.supabase_client import get_supabase
from services.scoring import calculate_priority_score, get_dispatch_count
from constants.sectors import SECTOR_BY_ID


def dispatch_volunteers(incident_id: str) -> list[dict]:
    """
    Find and assign best available volunteers for an incident.
    Returns list of dispatched volunteer dicts.
    """
    db = get_supabase()

    # Fetch incident
    inc_resp = db.table("incidents").select("*").eq("id", incident_id).execute()
    if not inc_resp.data:
        raise ValueError(f"Incident {incident_id} not found")
    incident = inc_resp.data[0]

    inc_lat = incident["location_lat"]
    inc_lng = incident["location_lng"]
    required_skills = incident.get("required_skills") or []
    severity = incident["severity"]

    # Fetch all active_idle volunteers
    vols_resp = db.table("volunteers").select("*").eq("status", "active_idle").execute()
    volunteers = vols_resp.data or []

    if not volunteers:
        return []

    # Score each volunteer
    scored = []
    for v in volunteers:
        # Get volunteer location from their sector
        sector = SECTOR_BY_ID.get(v.get("sector_id", ""), None)
        if sector:
            v_lat, v_lng = sector["lat"], sector["lng"]
        else:
            continue  # skip volunteers with unknown sector

        score = calculate_priority_score(
            v_lat, v_lng,
            v.get("skills") or [],
            v.get("languages") or [],
            v.get("hours_worked", 0.0),
            inc_lat, inc_lng,
            required_skills,
        )
        if score >= 0:
            scored.append((score, v))

    if not scored:
        return []

    # Sort by score descending, take top N
    scored.sort(key=lambda x: x[0], reverse=True)
    n = get_dispatch_count(severity)
    top = scored[:n]

    dispatched = []
    vol_ids = []
    for score, vol in top:
        vol_ids.append(vol["id"])
        dispatched.append({**vol, "dispatch_score": score})

        # Log dispatch
        db.table("dispatch_log").insert({
            "incident_id": incident_id,
            "volunteer_id": vol["id"],
            "score": score,
        }).execute()

    # Update volunteer statuses to on_mission
    for vid in vol_ids:
        db.table("volunteers").update({
            "status": "on_mission",
            "active_mission_id": incident_id,
        }).eq("id", vid).execute()

    # Update incident to dispatched
    db.table("incidents").update({
        "status": "dispatched",
        "assigned_volunteer_ids": vol_ids,
    }).eq("id", incident_id).execute()

    return dispatched


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from db.supabase_client import get_supabase
    db = get_supabase()

    # Cleanup any leftover test data first
    db.table("dispatch_log").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    db.table("incidents").delete().eq("is_mock", True).execute()
    db.table("volunteers").delete().eq("is_mock", True).execute()

    # Create test volunteer in SEC-01
    vol = db.table("volunteers").insert({
        "name": "Test Vol",
        "phone": "+919000000099",
        "skills": ["first_aid"],
        "languages": ["Hindi"],
        "sector_id": "SEC-01",
        "status": "active_idle",
        "hours_worked": 0.0,
        "is_mock": True,
    }).execute().data[0]

    # Create test incident in SEC-01
    inc = db.table("incidents").insert({
        "raw_text": "test collapse",
        "severity": "HIGH",
        "category": "medical",
        "required_skills": ["first_aid"],
        "summary": "test",
        "sector_id": "SEC-01",
        "location_lat": 25.4244,
        "location_lng": 81.8846,
        "is_mock": True,
    }).execute().data[0]

    # Dispatch
    result = dispatch_volunteers(inc["id"])
    assert len(result) > 0, "No volunteers dispatched"
    print(f"✓ Dispatched {len(result)} volunteer(s): {[r['name'] for r in result]}")

    # Verify volunteer status updated
    updated = db.table("volunteers").select("status").eq("id", vol["id"]).execute().data[0]
    assert updated["status"] == "on_mission", f"Expected on_mission, got {updated['status']}"
    print("✓ Volunteer status is on_mission")

    # Cleanup
    db.table("dispatch_log").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    db.table("incidents").delete().eq("is_mock", True).execute()
    db.table("volunteers").delete().eq("is_mock", True).execute()
    print("✓ Test data cleaned up. Dispatch service OK.")
