"""Add NEXT_PUBLIC_SUPABASE_SERVICE_KEY to Vercel project."""
import requests, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from load_credentials import load

TEAM_ID = 'team_hc8Ffex7brIdiUDJwP957Zgm'
PROJ_ID = 'prj_CQfEV3vvWPv5SpyuvtfPaF8ZKatu'

def main():
    creds = load()
    token = creds['VERCEL_TOKEN']
    h = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    p = {'teamId': TEAM_ID}

    # Remove existing if any
    r = requests.get(f'https://api.vercel.com/v9/projects/{PROJ_ID}/env', headers=h, params=p)
    for e in r.json().get('envs', []):
        if e['key'] == 'NEXT_PUBLIC_SUPABASE_SERVICE_KEY':
            requests.delete(f'https://api.vercel.com/v9/projects/{PROJ_ID}/env/{e["id"]}',
                            headers=h, params=p)
            print(f'  removed old {e["id"]}')

    # Add new
    rc = requests.post(
        f'https://api.vercel.com/v10/projects/{PROJ_ID}/env',
        headers=h, params=p,
        json={
            'key': 'NEXT_PUBLIC_SUPABASE_SERVICE_KEY',
            'value': creds['SUPABASE_SERVICE_KEY'],
            'type': 'plain',
            'target': ['production', 'preview', 'development'],
        },
    )
    if rc.status_code in (200, 201):
        print('  NEXT_PUBLIC_SUPABASE_SERVICE_KEY set on Vercel')
    else:
        print(f'  ERROR {rc.status_code}: {rc.text[:200]}')
        sys.exit(1)

if __name__ == '__main__':
    main()
