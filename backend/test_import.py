import sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('SUPABASE_URL', 'http://placeholder')
os.environ.setdefault('SUPABASE_KEY', 'placeholder')

results = []
try:
    from routers import simulate, sms
    results.append(f"simulate prefix: {simulate.router.prefix}")
    results.append(f"sms prefix: {sms.router.prefix}")
    results.append("OK")
except Exception as e:
    import traceback
    results.append(f"ERROR: {e}")
    results.append(traceback.format_exc())

with open("test_out.txt", "w") as f:
    f.write("\n".join(results))
