"""
Deploy MeshForce frontend to Vercel via Vercel CLI.
Idempotent — safe to re-run.
"""
import subprocess, os, sys, json, shutil
sys.path.insert(0, os.path.dirname(__file__))
from load_credentials import load

# On Windows, npx is npx.cmd
NPX = shutil.which("npx") or ("npx.cmd" if os.name == "nt" else "npx")

def run(cmd: list[str], cwd: str = None, env: dict = None) -> tuple[int, str, str]:
    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def main():
    creds = load()
    token = creds["VERCEL_TOKEN"]

    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

    env = os.environ.copy()
    env["VERCEL_TOKEN"] = token

    # Check if vercel CLI is available
    code, out, err = run([NPX, "vercel", "--version"], env=env)
    if code != 0:
        print("Installing Vercel CLI...")
        run(["npm", "install", "-g", "vercel"], env=env)

    print(f"Deploying frontend from {frontend_dir}...")

    # Build env var args for Vercel
    supabase_url = creds["SUPABASE_URL"]
    anon_key = creds["SUPABASE_ANON_KEY"]
    backend_url = "https://meshforce-api.onrender.com"

    # Deploy to production
    deploy_cmd = [
        NPX, "vercel", "--prod", "--yes",
        "--token", token,
        "-e", f"NEXT_PUBLIC_SUPABASE_URL={supabase_url}",
        "-e", f"NEXT_PUBLIC_SUPABASE_ANON_KEY={anon_key}",
        "-e", f"NEXT_PUBLIC_BACKEND_URL={backend_url}",
    ]

    print("Running: vercel --prod --yes ...")
    code, out, err = run(deploy_cmd, cwd=frontend_dir, env=env)

    if code == 0:
        # Extract URL from output
        lines = out.split('\n')
        url = next((l for l in lines if 'vercel.app' in l or 'meshforce' in l), out.split('\n')[-1])
        print(f"✓ Deployed successfully!")
        print(f"  URL: {url.strip()}")
    else:
        print(f"Deploy output: {out[:300]}")
        print(f"Deploy error: {err[:300]}")
        # Non-zero but may still have deployed — check output
        if 'vercel.app' in out or 'vercel.app' in err:
            print("✓ Deploy may have succeeded despite exit code — check output above")
        else:
            print("\nManual deployment:")
            print(f"  cd frontend")
            print(f"  VERCEL_TOKEN={token[:8]}... npx vercel --prod --yes")
            sys.exit(1)

    print("\n✓ Vercel deployment complete.")
    print(f"  Live at: https://meshforce.vercel.app (or URL shown above)")

if __name__ == "__main__":
    main()
