from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class IncidentReport(BaseModel):
    raw_text: str
    sector_id: Optional[str] = None
    reported_by: Optional[str] = None

class IncidentParsed(BaseModel):
    severity: str
    category: str
    required_skills: list[str]
    summary: str

class IncidentRead(BaseModel):
    id: str
    reported_by: Optional[str]
    raw_text: str
    severity: str
    category: str
    required_skills: list[str]
    summary: str
    sector_id: Optional[str]
    location_lat: float
    location_lng: float
    status: str
    assigned_volunteer_ids: list[str]
    source: str
    is_mock: bool
    created_at: datetime
    resolved_at: Optional[datetime]

class DispatchResult(BaseModel):
    incident_id: str
    dispatched_volunteers: list[dict]
    message: str

if __name__ == "__main__":
    r = IncidentReport(raw_text="Someone collapsed")
    assert r.raw_text == "Someone collapsed"
    print("✓ incident models OK")
