"""
Automated end-to-end integration test.
Starts the FastAPI server, runs all checks via HTTP, stops server.
No browser required.

Usage: python scripts/integration_test.py
All checks must pass (exit 0).
"""
import sys, os, time, subprocess, signal
import requests

sys.path.insert(0, os.path.dirname(__file__))

BASE = "http://localhost:8899"
TIMEOUT = 10

def wait_for_server(url: str, retries: int = 20) -> bool:
    for _ in range(retries):
        try:
            r = requests.get(url, timeout=2)
            if r.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def check(label: str, condition: bool, detail: str = ""):
    if condition:
        print(f"  ✓ {label}")
    else:
        print(f"  ✗ FAIL: {label}" + (f" — {detail}" if detail else ""))
        sys.exit(1)

def main():
    # Start backend server on port 8899
    backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
    env = os.environ.copy()
    env["PORT"] = "8899"

    print("Starting backend server on port 8899...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8899"],
        cwd=backend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        if not wait_for_server(f"{BASE}/health"):
            print("ERROR: Server failed to start in time")
            proc.terminate()
            sys.exit(1)
        print("Server ready.\n")

        # 1. Health check
        r = requests.get(f"{BASE}/health", timeout=TIMEOUT)
        check("Health endpoint", r.status_code == 200)
        check("Health returns ok", r.json().get("status") == "ok")

        # 2. Volunteer creation
        vol_payload = {
            "name": "Integration TestVol",
            "phone": f"+9188{int(time.time()) % 10000000:07d}",
            "skills": ["first_aid"],
            "languages": ["Hindi"],
            "sector_id": "SEC-01",
        }
        r = requests.post(f"{BASE}/api/volunteers", json=vol_payload, timeout=TIMEOUT)
        check("POST /api/volunteers returns 201", r.status_code == 201, str(r.text[:100]))
        vol = r.json()
        vol_id = vol.get("id")
        check("Volunteer has UUID id", bool(vol_id))
        check("Volunteer status is active_idle", vol.get("status") == "active_idle")

        # 3. Volunteer list
        r = requests.get(f"{BASE}/api/volunteers", timeout=TIMEOUT)
        check("GET /api/volunteers returns 200", r.status_code == 200)
        check("Volunteer list is a list", isinstance(r.json(), list))

        # 4. Volunteer status update
        r = requests.patch(
            f"{BASE}/api/volunteers/{vol_id}/status",
            json={"status": "resting"},
            timeout=TIMEOUT,
        )
        check("PATCH volunteer status returns 200", r.status_code == 200)
        check("Status updated to resting", r.json().get("status") == "resting")

        # Reset to active_idle for dispatch test
        requests.patch(
            f"{BASE}/api/volunteers/{vol_id}/status",
            json={"status": "active_idle"},
            timeout=TIMEOUT,
        )

        # 5. Incident report (uses mock LLM)
        inc_payload = {"raw_text": "Elderly man collapsed near gate 4, unresponsive", "sector_id": "SEC-01"}
        r = requests.post(f"{BASE}/api/incidents/report", json=inc_payload, timeout=TIMEOUT)
        check("POST /api/incidents/report returns 200", r.status_code == 200, str(r.text[:200]))
        inc_resp = r.json()
        check("Incident has id", bool(inc_resp.get("incident", {}).get("id")))
        check("Parsed severity is CRITICAL", inc_resp.get("parsed", {}).get("severity") == "CRITICAL")
        check("Parsed category is medical", inc_resp.get("parsed", {}).get("category") == "medical")

        # 6. Incident list
        r = requests.get(f"{BASE}/api/incidents", timeout=TIMEOUT)
        check("GET /api/incidents returns 200", r.status_code == 200)
        check("Incident list is a list", isinstance(r.json(), list))

        # 7. Simulation run
        r = requests.post(f"{BASE}/api/simulate/run", timeout=60)
        check("POST /api/simulate/run returns 200", r.status_code == 200, str(r.text[:200]))
        sim = r.json()
        check("Simulation created 50 volunteers", sim.get("volunteers_created") == 50)
        check("Simulation created 15 incidents", sim.get("incidents_created") == 15)

        # 8. Simulation clear
        r = requests.delete(f"{BASE}/api/simulate/clear", timeout=TIMEOUT)
        check("DELETE /api/simulate/clear returns 200", r.status_code == 200)

        # 9. SMS inbound (form data)
        r = requests.post(
            f"{BASE}/api/sms/inbound",
            data={"from": "+911234567890", "text": "SEC03_MED_CRIT_person collapsed"},
            timeout=TIMEOUT,
        )
        check("POST /api/sms/inbound returns 200", r.status_code == 200, str(r.text[:200]))
        check("SMS response has incident_id", bool(r.json().get("incident_id")))

        # 10. Cleanup: delete test volunteer
        r = requests.delete(f"{BASE}/api/volunteers/{vol_id}", timeout=TIMEOUT)
        # 204 or 404 both acceptable

        print("\n✅ All integration tests passed.")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    main()
