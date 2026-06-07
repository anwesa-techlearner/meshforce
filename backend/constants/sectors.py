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
