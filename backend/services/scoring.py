"""
Volunteer priority scoring engine.
P(v,i) = 0.4*(1 - d/d_max) + 0.3*S(v,i) + 0.1*L(v,i) - 0.2*E(v)

d      = geodesic distance (meters), d_max = 3000
S(v,i) = |skills_v ∩ skills_i| / |skills_i|   (0 if no skills required → 1.0)
L(v,i) = 1 if languages overlap, else 0
E(v)   = min(hours_worked / 8.0, 1.0)
Returns -1.0 if d > d_max (out of range)
Dispatch count: CRITICAL→3, HIGH→2, MEDIUM→1, LOW→1
"""
from geopy.distance import geodesic

D_MAX = 3000.0  # meters

DISPATCH_COUNT = {
    "CRITICAL": 3,
    "HIGH": 2,
    "MEDIUM": 1,
    "LOW": 1,
}

def calculate_priority_score(
    vol_lat: float, vol_lng: float,
    vol_skills: list[str], vol_languages: list[str],
    hours_worked: float,
    inc_lat: float, inc_lng: float,
    required_skills: list[str],
    incident_languages: list[str] | None = None,
) -> float:
    """
    Returns priority score in [0.0, 1.0] or -1.0 if out of range.
    """
    # Distance component
    d = geodesic((vol_lat, vol_lng), (inc_lat, inc_lng)).meters
    if d > D_MAX:
        return -1.0

    dist_score = 1.0 - (d / D_MAX)

    # Skill match component
    if not required_skills:
        skill_score = 1.0
    else:
        matched = len(set(vol_skills) & set(required_skills))
        skill_score = matched / len(required_skills)

    # Language match component
    if incident_languages:
        lang_score = 1.0 if set(vol_languages) & set(incident_languages) else 0.0
    else:
        lang_score = 0.0

    # Exhaustion component
    exhaustion = min(hours_worked / 8.0, 1.0)

    score = (0.4 * dist_score) + (0.3 * skill_score) + (0.1 * lang_score) - (0.2 * exhaustion)
    return round(score, 4)


def get_dispatch_count(severity: str) -> int:
    return DISPATCH_COUNT.get(severity, 1)


if __name__ == "__main__":
    # Test 1: ideal volunteer — same location, perfect skills, fresh
    score = calculate_priority_score(
        25.4244, 81.8846, ["first_aid", "crowd_management"], ["Hindi"], 0.0,
        25.4250, 81.8850, ["first_aid", "crowd_management"]
    )
    assert score > 0.65, f"Expected > 0.65, got {score}"
    print(f"✓ ideal score: {score}")

    # Test 2: out of range
    score2 = calculate_priority_score(
        25.4244, 81.8846, ["first_aid"], ["Hindi"], 4.0,
        25.4600, 81.9100, ["first_aid"]
    )
    assert score2 == -1.0, f"Expected -1.0, got {score2}"
    print("✓ out-of-range: -1.0")

    # Test 3: exhausted volunteer
    score3 = calculate_priority_score(
        25.4244, 81.8846, ["first_aid"], ["Hindi"], 8.0,
        25.4250, 81.8850, ["first_aid"]
    )
    assert score3 < score, f"Exhausted should score less than fresh, got {score3} vs {score}"
    print(f"✓ exhausted score lower: {score3}")

    # Test 4: dispatch counts
    assert get_dispatch_count("CRITICAL") == 3
    assert get_dispatch_count("HIGH") == 2
    assert get_dispatch_count("LOW") == 1
    print("✓ dispatch counts correct")

    print("All scoring tests passed.")
