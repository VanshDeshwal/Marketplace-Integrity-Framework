import os
import sys
import time
import shutil
import subprocess
import threading
from pathlib import Path

# One-command local runner for:
# - Backend API (FastAPI) on http://localhost:8000
# - Media server (images) on http://localhost:9000
# - Frontend static site on http://localhost:5500 (serves frontend/)
#
# Usage (PowerShell):
#   python tools/run_local.py
#
# Stop: Ctrl+C (will attempt to terminate all child processes)

REPO = Path(__file__).resolve().parents[1]
BACKEND_APP = 'app.main:app'
MEDIA_APP = 'media_server.server:app'
BACKEND_PORT = os.environ.get('BACKEND_PORT', '8000')
MEDIA_PORT = os.environ.get('MEDIA_PORT', '9000')
FRONTEND_PORT = os.environ.get('FRONTEND_PORT', '5500')

# Ensure MEDIA_BASE_URL so backend returns image_url fields
os.environ.setdefault('MEDIA_BASE_URL', f'http://localhost:{MEDIA_PORT}')

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
    if not (REPO / 'frontend' / 'index.html').exists():
        print("[warn] frontend/index.html not found. Serving folder anyway.")
    if not (REPO / 'backend' / 'app' / 'main.py').exists():
        print("[error] backend app not found.")
        sys.exit(1)

    # Backend
    backend_cmd = [PYEXE, '-m', 'uvicorn', BACKEND_APP, '--reload', '--port', BACKEND_PORT]
    p_backend = run('backend', backend_cmd, cwd=REPO / 'backend')

    # Media server
    media_cmd = [PYEXE, '-m', 'uvicorn', MEDIA_APP, '--reload', '--port', MEDIA_PORT]
    p_media = run('media', media_cmd, cwd=REPO)

    # Frontend static server
    # Prefer Python http.server; fallback to Node npx serve if desired
    if shutil.which(PYEXE):
        front_cmd = [PYEXE, '-m', 'http.server', FRONTEND_PORT]
        p_front = run('frontend', front_cmd, cwd=REPO / 'frontend')
    else:
        # Should not happen; Python is required
        print('[error] Python not found for frontend server')
        cleanup()
        sys.exit(1)

    print('\nAll services launching...')
    print(f"  API     → http://localhost:{BACKEND_PORT} (docs at /docs)")
    print(f"  Media   → http://localhost:{MEDIA_PORT}")
    print(f"  Frontend→ http://localhost:{FRONTEND_PORT}")
    print('\nTip: The backend is configured with MEDIA_BASE_URL, so results include image_url pointing to the media server.')

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
