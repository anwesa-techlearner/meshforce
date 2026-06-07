"""
Deploy MeshForce backend to Render via Render API.
Creates web service if it doesn't exist, triggers deploy if it does.
Idempotent — safe to re-run.
"""
import requests, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from load_credentials import load

SERVICE_NAME = "meshforce-api"
RENDER_API = "https://api.render.com/v1"
OWNER_ID = "tea-d8iks57lk1mc7389lii0"

def main():
    creds = load()
    token = creds["RENDER_API_KEY"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Check existing services
    print("Checking existing Render services...")
    r = requests.get(f"{RENDER_API}/services?limit=20", headers=headers)
    if r.status_code != 200:
        print(f"ERROR listing services: {r.status_code} {r.text[:200]}")
        sys.exit(1)

    existing = None
    for item in r.json():
        s = item.get("service", item)
        if s.get("name") == SERVICE_NAME:
            existing = s
            break

    if existing:
        service_id = existing["id"]
        url = existing.get("serviceDetails", {}).get("url") or f"https://{SERVICE_NAME}.onrender.com"
        print(f"✓ Service already exists: {url}")
        # Trigger redeploy
        r2 = requests.post(f"{RENDER_API}/services/{service_id}/deploys",
                           headers=headers, json={"clearCache": "do_not_clear"})
        if r2.status_code in (200, 201):
            print(f"✓ Redeploy triggered")
        else:
            print(f"  Deploy trigger: {r2.status_code} {r2.text[:100]}")
    else:
        print("Creating new Render web service...")
        payload = {
            "autoDeploy": "yes",
            "branch": "main",
            "name": SERVICE_NAME,
            "ownerId": OWNER_ID,
            "repo": "https://github.com/anwesa-techlearner/meshforce",
            "rootDir": ".",
            "serviceDetails": {
                "buildCommand": "pip install -r backend/requirements.txt",
                "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
                "plan": "free",
                "region": "singapore",
                "runtime": "python",
                "numInstances": 1,
                "envSpecificDetails": {
                    "buildCommand": "pip install -r backend/requirements.txt",
                    "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
                }
            },
            "envVars": [
                {"key": "SUPABASE_URL", "value": creds["SUPABASE_URL"]},
                {"key": "SUPABASE_SERVICE_KEY", "value": creds["SUPABASE_SERVICE_KEY"]},
                {"key": "ANTHROPIC_API_KEY", "value": creds["ANTHROPIC_API_KEY"]},
                {"key": "USE_MOCK_LLM", "value": "true"},
                {"key": "AFRICASTALKING_USERNAME", "value": "sandbox"},
                {"key": "AFRICASTALKING_API_KEY", "value": ""},
                {"key": "PYTHON_VERSION", "value": "3.11.0"},
            ],
            "type": "web_service",
        }

        r = requests.post(f"{RENDER_API}/services", json=payload, headers=headers)
        if r.status_code in (200, 201):
            svc = r.json().get("service", r.json())
            print(f"✓ Service created: {svc.get('id')}")
            print(f"  Will be live at: https://{SERVICE_NAME}.onrender.com")
            print("  First deploy takes 2-3 minutes — check Render dashboard.")
        else:
            print(f"ERROR: {r.status_code}")
            print(r.text[:500])
            sys.exit(1)

    print("\n✓ Render deployment script complete.")
    print(f"  API docs: https://{SERVICE_NAME}.onrender.com/docs")

if __name__ == "__main__":
    main()
