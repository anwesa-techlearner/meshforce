"""
Sets Vercel project-level env vars for MeshForce frontend.
Reads credentials from .credentials file — never hardcodes secrets.
Run once after initial Vercel project creation.
"""
import requests, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from load_credentials import load

TEAM_ID = 'team_hc8Ffex7brIdiUDJwP957Zgm'

def main():
    creds = load()
    token = creds['VERCEL_TOKEN']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    r = requests.get('https://api.vercel.com/v9/projects/frontend',
                     headers=headers, params={'teamId': TEAM_ID})
    proj_id = r.json().get('id')
    print(f'Project ID: {proj_id}')

    env_vars = [
        {'key': 'NEXT_PUBLIC_SUPABASE_URL',      'value': creds['SUPABASE_URL'],      'type': 'plain', 'target': ['production', 'preview', 'development']},
        {'key': 'NEXT_PUBLIC_SUPABASE_ANON_KEY', 'value': creds['SUPABASE_ANON_KEY'], 'type': 'plain', 'target': ['production', 'preview', 'development']},
        {'key': 'NEXT_PUBLIC_BACKEND_URL',        'value': 'https://meshforce-api.onrender.com', 'type': 'plain', 'target': ['production', 'preview', 'development']},
    ]

    for ev in env_vars:
        r2 = requests.post(
            f'https://api.vercel.com/v10/projects/{proj_id}/env',
            headers=headers, params={'teamId': TEAM_ID}, json=ev,
        )
        status = 'OK' if r2.status_code in (200, 201) else r2.text[:100]
        print(f'  {ev["key"]}: {r2.status_code} {status}')

    print('Done.')

if __name__ == '__main__':
    main()
