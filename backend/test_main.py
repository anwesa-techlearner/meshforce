import sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('SUPABASE_URL', 'http://placeholder')
os.environ.setdefault('SUPABASE_KEY', 'placeholder')

results = []
try:
    import main
    routes = [r.path for r in main.app.routes]
    results.append("Routes:")
    for r in routes:
        results.append(f"  {r}")
except Exception as e:
    import traceback
    results.append(f"ERROR: {e}")
    results.append(traceback.format_exc())

with open("test_main_out.txt", "w") as f:
    f.write("\n".join(results))
