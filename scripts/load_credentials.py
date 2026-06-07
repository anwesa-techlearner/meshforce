"""
Reads .credentials from repo root and returns a dict.
Call this at the start of every other script.
"""
import os, sys

REQUIRED_KEYS = [
    "GITHUB_TOKEN", "SUPABASE_URL", "SUPABASE_SERVICE_KEY",
    "SUPABASE_ANON_KEY", "ANTHROPIC_API_KEY",
    "RENDER_API_KEY", "VERCEL_TOKEN", "VERCEL_ORG_ID"
]

def load():
    creds_path = os.path.join(os.path.dirname(__file__), '..', '.credentials')
    if not os.path.exists(creds_path):
        print("ERROR: .credentials file not found in repo root.")
        print("Create it with these keys:")
        for k in REQUIRED_KEYS:
            print(f"  {k}=your_value_here")
        sys.exit(1)
    creds = {}
    with open(creds_path) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                creds[k.strip()] = v.strip()
    missing = [k for k in REQUIRED_KEYS if not creds.get(k)]
    if missing:
        print(f"ERROR: Missing keys in .credentials: {missing}")
        sys.exit(1)
    print("✓ All credentials loaded")
    return creds

if __name__ == "__main__":
    creds = load()
    for k in REQUIRED_KEYS:
        masked = creds[k][:8] + "..." if len(creds[k]) > 8 else "***"
        print(f"  {k} = {masked}")
