"""
LLM incident parser with mock/real toggle.
USE_MOCK_LLM=true (default) → keyword-based mock, zero API cost.
USE_MOCK_LLM=false → calls Claude claude-sonnet-4-20250514, max_tokens=256.
NEVER call real API in loops or simulation.
"""
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


def _parse_incident_mock(raw_text: str) -> dict:
    """Keyword-based mock parser — zero API calls."""
    text_lower = raw_text.lower()
    if any(w in text_lower for w in ["collapse", "faint", "heart", "injur", "fell",
                                      "drown", "unconscious", "stampede"]):
        return {
            "severity": "CRITICAL",
            "category": "medical",
            "required_skills": ["first_aid"],
            "summary": "Medical emergency reported",
        }
    elif any(w in text_lower for w in ["crowd", "rush", "block", "push", "surge", "bottleneck"]):
        return {
            "severity": "HIGH",
            "category": "crowd_control",
            "required_skills": ["crowd_management"],
            "summary": "Crowd control needed",
        }
    elif any(w in text_lower for w in ["lost", "missing", "child", "find", "wallet", "group"]):
        return {
            "severity": "LOW",
            "category": "lost_found",
            "required_skills": ["info_desk"],
            "summary": "Lost person or item",
        }
    elif any(w in text_lower for w in ["fire", "smoke", "barricade", "bag", "unattended"]):
        return {
            "severity": "MEDIUM",
            "category": "infrastructure",
            "required_skills": ["fire_safety"],
            "summary": "Infrastructure issue reported",
        }
    else:
        return {
            "severity": "LOW",
            "category": "general",
            "required_skills": [],
            "summary": "General assistance needed",
        }


def _parse_incident_real(raw_text: str) -> dict:
    """Real Claude API call — only when USE_MOCK_LLM=false. max_tokens=256."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = f"""Parse this incident report into JSON with keys: severity (CRITICAL/HIGH/MEDIUM/LOW), category (medical/crowd_control/lost_found/infrastructure/general), required_skills (array from: first_aid,crowd_management,translation,info_desk,fire_safety), summary (one sentence).

Incident: {raw_text}

Respond with JSON only, no explanation."""
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )
    import json
    text = msg.content[0].text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def parse_incident(raw_text: str) -> dict:
    """Routes to mock or real parser based on USE_MOCK_LLM env var."""
    use_mock = os.environ.get("USE_MOCK_LLM", "true").lower() != "false"
    if use_mock:
        return _parse_incident_mock(raw_text)
    else:
        return _parse_incident_real(raw_text)


if __name__ == "__main__":
    os.environ["USE_MOCK_LLM"] = "true"

    r = parse_incident("Elderly man collapsed near gate 4, unresponsive")
    assert r["severity"] == "CRITICAL" and r["category"] == "medical", f"got {r}"
    print(f"✓ medical: {r}")

    r2 = parse_incident("Crowd blocking the exit corridor")
    assert r2["category"] == "crowd_control", f"got {r2}"
    print(f"✓ crowd: {r2}")

    r3 = parse_incident("Lost child near info desk")
    assert r3["category"] == "lost_found", f"got {r3}"
    print(f"✓ lost_found: {r3}")

    r4 = parse_incident("Suspicious unattended bag near checkpoint")
    assert r4["category"] == "infrastructure", f"got {r4}"
    print(f"✓ infrastructure: {r4}")

    r5 = parse_incident("Please help with general assistance")
    assert r5["category"] == "general", f"got {r5}"
    print(f"✓ general: {r5}")

    print("All mock LLM tests passed. Zero API credits used.")
