"""Creates the meshforce repo under anwesa-techlearner via GitHub API."""
import requests, subprocess, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from load_credentials import load

def main():
    creds = load()
    token = creds["GITHUB_TOKEN"]
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    # Check if repo already exists
    r = requests.get("https://api.github.com/repos/anwesa-techlearner/meshforce", headers=headers)
    if r.status_code == 200:
        print("✓ Repo already exists — skipping creation")
        return

    # Create repo
    payload = {
        "name": "meshforce",
        "description": "AI-Powered Volunteer Dispatch for Mahakumbh 2025",
        "private": False,
        "auto_init": False
    }
    r = requests.post("https://api.github.com/user/repos", json=payload, headers=headers)
    if r.status_code not in (200, 201):
        print(f"ERROR creating repo: {r.status_code} {r.text}")
        sys.exit(1)
    print("✓ GitHub repo created: https://github.com/anwesa-techlearner/meshforce")

if __name__ == "__main__":
    main()
