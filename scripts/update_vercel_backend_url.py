"""Update NEXT_PUBLIC_BACKEND_URL on Vercel project to live Render URL."""
import requests, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from load_credentials import load

TEAM_ID  = 'team_hc8Ffex7brIdiUDJwP957Zgm'
PROJ_ID  = 'prj_CQfEV3vvWPv5SpyuvtfPaF8ZKatu'
NEW_URL  = 'https://meshforce-api.onrender.com'
KEY      = 'NEXT_PUBLIC_BACKEND_URL'

def main():
    creds = load()
    token = creds['VERCEL_TOKEN']
    h = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    p = {'teamId': TEAM_ID}

    # List existing env vars for this key
    r = requests.get(f'https://api.vercel.com/v9/projects/{PROJ_ID}/env',
                     headers=h, params=p)
    envs = r.json().get('envs', [])
    existing = [e for e in envs if e['key'] == KEY]

    # Delete all existing copies
    for e in existing:
        rd = requests.delete(f'https://api.vercel.com/v9/projects/{PROJ_ID}/env/{e["id"]}',
                             headers=h, params=p)
        print(f'  deleted {e["id"]} ({e.get("target")}): {rd.status_code}')

    # Create one entry covering all targets
    payload = {
        'key': KEY,
        'value': NEW_URL,
        'type': 'plain',
        'target': ['production', 'preview', 'development'],
    }
    rc = requests.post(f'https://api.vercel.com/v10/projects/{PROJ_ID}/env',
                       headers=h, params=p, json=payload)
    if rc.status_code in (200, 201):
        print(f'  ✓ {KEY} = {NEW_URL}')
    else:
        print(f'  ERROR {rc.status_code}: {rc.text[:200]}')
        sys.exit(1)

if __name__ == '__main__':
    main()
