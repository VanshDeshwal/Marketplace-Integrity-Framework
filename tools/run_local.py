import os
import sys
import time
import shutil
import subprocess
import threading
from pathlib import Path

# One-command local runner for:
# - Backend API (FastAPI) on http://localhost:8000
# - Frontend React app on http://localhost:3000
#
# Usage (PowerShell):
#   python tools/run_local.py
#
# Stop: Ctrl+C (will attempt to terminate all child processes)

REPO = Path(__file__).resolve().parents[1]
BACKEND_APP = 'app.main:app'
BACKEND_PORT = os.environ.get('BACKEND_PORT', '8000')
FRONTEND_PORT = os.environ.get('FRONTEND_PORT', '3000')

PYEXE = sys.executable or 'python'

PROCS = []  # list of (name, Popen)

def run(name, cmd, cwd=None):
    print(f"→ Starting [{name}]: {' '.join(cmd)} (cwd={cwd or REPO})")
    p = subprocess.Popen(
        cmd,
        cwd=str(cwd or REPO),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    PROCS.append((name, p))
    # background tail
    t = threading.Thread(target=tail, args=(name, p), daemon=True)
    t.start()
    return p


def tail(name, proc):
    try:
        for line in proc.stdout:
            if not line:
                break
            print(f"[{name}] {line}", end='')
    except Exception:
        pass


def main():
    # Pre-flight checks
    if not (REPO / 'frontend' / 'package.json').exists():
        print("[warn] frontend/package.json not found. React app may not start.")
    if not (REPO / 'backend' / 'app' / 'main.py').exists():
        print("[error] backend app not found.")
        sys.exit(1)

    # Backend
    backend_cmd = [PYEXE, '-m', 'uvicorn', BACKEND_APP, '--reload', '--port', BACKEND_PORT]
    p_backend = run('backend', backend_cmd, cwd=REPO / 'backend')

    # Frontend React app
    if shutil.which('npm'):
        front_cmd = ['npm', 'start']
        p_front = run('frontend', front_cmd, cwd=REPO / 'frontend')
    else:
        print('[error] npm not found. Please install Node.js to run the React frontend.')
        cleanup()
        sys.exit(1)

    print('\nAll services launching...')
    print(f"  API     → http://localhost:{BACKEND_PORT} (docs at /docs)")
    print(f"  Frontend→ http://localhost:{FRONTEND_PORT}")
    print('\nNote: The backend serves images directly at /images/ endpoint with CORS enabled.')

    # Monitor processes & report exit codes
    try:
        last_codes = {}
        while True:
            alive = False
            for name, p in PROCS:
                code = p.poll()
                if code is None:
                    alive = True
                else:
                    if name not in last_codes:
                        last_codes[name] = code
                        print(f"\n[{name}] exited with code {code}")
            if not alive:
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nStopping services...')
    finally:
        cleanup()


def cleanup():
    for _, p in PROCS:
        if p.poll() is None:
            try:
                p.terminate()
            except Exception:
                pass
    # Give some time then kill if needed
    time.sleep(1)
    for _, p in PROCS:
        if p.poll() is None:
            try:
                p.kill()
            except Exception:
                pass


if __name__ == '__main__':
    main()
