"""SMS inbound webhook router (Africa's Talking compatible)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fastapi import APIRouter, Form
from db.supabase_client import get_supabase
from services.sms_parser import parse_sms
from services.llm_parser import parse_incident
from services.dispatch import dispatch_volunteers
from constants.sectors import SECTOR_BY_ID

router = APIRouter(prefix="/api/sms", tags=["sms"])


@router.post("/inbound")
async def sms_inbound(
    from_: str = Form(alias="from", default=""),
    text: str = Form(default=""),
):
    """
    Africa's Talking inbound SMS webhook.
    Tries structured format first, falls back to mock LLM parser.
    """
    db = get_supabase()

    # Try structured parse first
    parsed_sms = parse_sms(text)

    if parsed_sms:
        inc_data = {
            "raw_text": text,
            "severity": parsed_sms["severity"],
            "category": parsed_sms["category"],
            "required_skills": parsed_sms["required_skills"],
            "summary": parsed_sms["summary"],
            "sector_id": parsed_sms["sector_id"],
            "location_lat": parsed_sms["location_lat"],
            "location_lng": parsed_sms["location_lng"],
            "status": "reported",
            "source": "sms",
            "is_mock": False,
        }
    else:
        # Fall back to mock LLM parser
        parsed = parse_incident(text)
        sector = SECTOR_BY_ID.get("SEC-01")
        inc_data = {
            "raw_text": text,
            "severity": parsed["severity"],
            "category": parsed["category"],
            "required_skills": parsed["required_skills"],
            "summary": parsed["summary"],
            "sector_id": "SEC-01",
            "location_lat": sector["lat"],
            "location_lng": sector["lng"],
            "status": "reported",
            "source": "sms",
            "is_mock": False,
        }

    result = db.table("incidents").insert(inc_data).execute()
    incident = result.data[0]

    try:
        dispatched = dispatch_volunteers(incident["id"])
    except Exception:
        dispatched = []

    return {
        "incident_id": incident["id"],
        "dispatched": len(dispatched),
        "message": "SMS processed",
    }
