"""
SMS incident parser.
Expected format: SEC03_MED_CRIT_description text here
Components: SECXX_CATEGORY_SEVERITY_free text
Category codes: MED=medical, CRD=crowd_control, LST=lost_found, INF=infrastructure, GEN=general
Severity codes: CRIT=CRITICAL, HIGH=HIGH, MED=MEDIUM, LOW=LOW
Returns None if format doesn't match.
"""
import os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from constants.sectors import SECTOR_BY_ID, SMS_CATEGORY_MAP, SMS_SEVERITY_MAP
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Pattern: SEC01_CAT_SEV_text  OR  SEC-01_CAT_SEV_text
SMS_PATTERN = re.compile(
    r'^(SEC[-]?\d{2})[_\s]([A-Z]{2,3})[_\s]([A-Z]{2,4})[_\s](.+)$',
    re.IGNORECASE
)


def parse_sms(raw_text: str) -> dict | None:
    """
    Parse SMS-format incident text.
    Returns structured dict or None if format invalid.
    """
    if not raw_text:
        return None

    m = SMS_PATTERN.match(raw_text.strip())
    if not m:
        return None

    sector_raw, cat_code, sev_code, description = m.groups()

    # Normalize sector ID: SEC01 → SEC-01
    sector_id = sector_raw.upper()
    if not sector_id.startswith("SEC-"):
        sector_id = "SEC-" + sector_id[3:]

    if sector_id not in SECTOR_BY_ID:
        return None

    category = SMS_CATEGORY_MAP.get(cat_code.upper())
    severity = SMS_SEVERITY_MAP.get(sev_code.upper())

    if not category or not severity:
        return None

    sector = SECTOR_BY_ID[sector_id]

    # Determine required skills based on category
    skill_map = {
        "medical": ["first_aid"],
        "crowd_control": ["crowd_management"],
        "lost_found": ["info_desk"],
        "infrastructure": ["fire_safety"],
        "general": [],
    }

    return {
        "sector_id": sector_id,
        "location_lat": sector["lat"],
        "location_lng": sector["lng"],
        "category": category,
        "severity": severity,
        "required_skills": skill_map.get(category, []),
        "raw_text": raw_text,
        "summary": description.strip(),
        "source": "sms",
    }


if __name__ == "__main__":
    # Test 1: valid structured SMS
    r = parse_sms("SEC03_MED_CRIT_person collapsed gate 3")
    assert r is not None, "Expected parsed result, got None"
    assert r["severity"] == "CRITICAL", f"Expected CRITICAL, got {r['severity']}"
    assert r["sector_id"] == "SEC-03", f"Expected SEC-03, got {r['sector_id']}"
    assert r["category"] == "medical", f"Expected medical, got {r['category']}"
    print(f"✓ parsed structured SMS: {r}")

    # Test 2: invalid format returns None
    assert parse_sms("invalid text") is None
    print("✓ invalid format returns None")

    # Test 3: another valid format
    r2 = parse_sms("SEC-01_CRD_HIGH_crowd blocking main gate")
    assert r2 is not None
    assert r2["category"] == "crowd_control"
    assert r2["severity"] == "HIGH"
    print(f"✓ crowd control SMS: {r2}")

    # Test 4: empty string
    assert parse_sms("") is None
    print("✓ empty string returns None")

    print("SMS parser tests passed.")
