from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VolunteerCreate(BaseModel):
    name: str
    phone: str
    skills: list[str] = []
    languages: list[str] = []
    sector_id: str

class VolunteerUpdate(BaseModel):
    status: str

class VolunteerRead(BaseModel):
    id: str
    name: str
    phone: str
    skills: list[str]
    languages: list[str]
    sector_id: Optional[str]
    status: str
    active_mission_id: Optional[str]
    hours_worked: float
    shift_start: datetime
    is_mock: bool
    created_at: datetime

class VolunteerStatusPatch(BaseModel):
    status: str

if __name__ == "__main__":
    v = VolunteerCreate(name="Test", phone="+91999", skills=["first_aid"], languages=["Hindi"], sector_id="SEC-01")
    assert v.name == "Test"
    assert v.skills == ["first_aid"]
    print("✓ volunteer models OK")
