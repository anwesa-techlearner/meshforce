"""
Task 26: Final production smoke test.
Verifies the deployed system end-to-end using live URLs.
"""
import requests, sys, time

BACKEND  = "https://meshforce-api.onrender.com"
FRONTEND = "https://frontend-dl4l9vlwo-anwesa-s-projects.vercel.app"

results = []

def check(label, ok, detail=""):
    results.append((ok, label))
    mark = "\u2713" if ok else "\u2717"
    print(f"  {mark} {label}" + (f" \u2014 {detail}" if detail else ""))
    if not ok:
        print(f"    DETAIL: {detail}")

print("=" * 50)
print("  MeshForce Production Smoke Test")
print("=" * 50)

# --- Backend ---
print("\n[Backend: Render]")

r = requests.get(f"{BACKEND}/health", timeout=30)
check("/health", r.status_code == 200, str(r.status_code))
if r.status_code == 200:
    check("status=ok", r.json().get("status") == "ok")

r = requests.get(f"{BACKEND}/docs", timeout=15)
check("/docs accessible", r.status_code == 200, str(r.status_code))

r = requests.get(f"{BACKEND}/openapi.json", timeout=15)
if r.status_code == 200:
    paths = list(r.json().get("paths", {}).keys())
    check("/api/volunteers route", "/api/volunteers" in paths)
    check("/api/incidents/report route", "/api/incidents/report" in paths)
    check("/api/simulate/run route", "/api/simulate/run" in paths)
    check("/api/sms/inbound route", "/api/sms/inbound" in paths)
else:
    check("OpenAPI schema", False, str(r.status_code))

# Live volunteer create
phone = f"+9199{int(time.time()) % 10000000:07d}"
r = requests.post(f"{BACKEND}/api/volunteers", json={
    "name": "SmokeTestVol",
    "phone": phone,
    "skills": ["first_aid"],
    "languages": ["Hindi"],
    "sector_id": "SEC-01",
}, timeout=15)
check("POST /api/volunteers", r.status_code == 201, str(r.status_code))
vol_id = r.json().get("id") if r.status_code == 201 else None

# Live incident report (mock LLM)
r = requests.post(f"{BACKEND}/api/incidents/report", json={
    "raw_text": "crowd surge blocking exit near Sangam Nose",
    "sector_id": "SEC-01",
}, timeout=15)
check("POST /api/incidents/report", r.status_code == 200, str(r.status_code))
if r.status_code == 200:
    parsed = r.json().get("parsed", {})
    check("Mock LLM: crowd_control category", parsed.get("category") == "crowd_control", str(parsed))
    check("Mock LLM: HIGH severity", parsed.get("severity") == "HIGH", str(parsed))

# SMS endpoint
r = requests.post(f"{BACKEND}/api/sms/inbound",
    data={"from": "+911234567890", "text": "SEC01_MED_CRIT_person collapsed"},
    timeout=15)
check("POST /api/sms/inbound", r.status_code == 200, str(r.status_code))

# --- Frontend ---
print("\n[Frontend: Vercel]")
r = requests.get(FRONTEND, timeout=20)
check("Frontend responds", r.status_code in (200, 307, 308), str(r.status_code))

# Cleanup test data
if vol_id:
    requests.delete(f"{BACKEND}/api/volunteers/{vol_id}", timeout=10)
requests.delete(f"{BACKEND}/api/simulate/clear", timeout=15)

# Summary
print()
passed = sum(1 for ok, _ in results if ok)
failed = sum(1 for ok, _ in results if not ok)
print("=" * 50)
print(f"  {passed}/{len(results)} checks passed")
if failed == 0:
    print("  ALL PRODUCTION SMOKE TESTS PASSED")
else:
    for ok, label in results:
        if not ok:
            print(f"  FAILED: {label}")
print("=" * 50)
sys.exit(0 if failed == 0 else 1)
