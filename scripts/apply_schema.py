"""
Reads backend/db/schema.sql and applies each statement to Supabase
via the Management API.
"""
import os, sys, time, requests

sys.path.insert(0, os.path.dirname(__file__))
from load_credentials import load

def main():
    creds = load()
    supabase_url = creds["SUPABASE_URL"]
    service_key  = creds["SUPABASE_SERVICE_KEY"]

    project_ref = supabase_url.replace("https://", "").split(".supabase.co")[0]
    mgmt_url    = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"
    headers     = {
        "Authorization": f"Bearer {service_key}",
        "Content-Type":  "application/json",
    }

    schema_path = os.path.join(os.path.dirname(__file__), "..", "backend", "db", "schema.sql")
    if not os.path.exists(schema_path):
        print(f"ERROR: {schema_path} not found.")
        sys.exit(1)

    with open(schema_path) as f:
        sql_text = f.read()

    statements = [s.strip() for s in sql_text.split(";") if s.strip()]
    print(f"Applying {len(statements)} SQL statements to {project_ref}...")

    for i, stmt in enumerate(statements, 1):
        full_stmt = stmt + ";"
        print(f"  [{i}/{len(statements)}] {full_stmt[:60].replace(chr(10),' ')}...")
        r = requests.post(mgmt_url, json={"query": full_stmt}, headers=headers)
        if r.status_code in (200, 201):
            print(f"    ✓ OK")
        else:
            print(f"    ✗ {r.status_code}: {r.text[:200]}")
        time.sleep(0.2)

    print("\nDone.")

if __name__ == "__main__":
    main()
