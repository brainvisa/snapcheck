"""
Start SnapCheck locally (the "snapcheck" command): the backend (snapserve) then the Qt client (snapclient).
The backend is stopped when the client exits.
"""

import argparse
import os
import secrets
import subprocess
import sys
import time
import uuid

try:
    import requests
    from lepton.app import DEFAULT_PORT as DEFAULT_BACKEND_PORT
    from lepton.auth import Authenticator, TokenData
    from snapclient.__main__ import main as client_main
    from snapclient.constants import DEFAULT_PORT, DEFAULT_URL
except ImportError as e:
    # The GUI dependencies are optional with pip (snapcheck[client] extra)
    sys.exit(f'The SnapCheck client is not installed ({e}).\nInstall it with: pip install "snapcheck[client]"')


def wait_for_backend(process: subprocess.Popen, url: str, tries: int = 100, delay: float = 0.2):
    """Wait for the backend to answer before loading the frontend."""
    for _ in range(tries):
        if process.poll() is not None:
            sys.exit("Backend failed to start")
        try:
            requests.get(f"{url}/docs")
            return
        except requests.exceptions.ConnectionError:
            time.sleep(delay)
    sys.exit("Backend didn't start in time")


def main():
    parser = argparse.ArgumentParser(description="Start the SnapCheck backend and GUI")
    parser.add_argument("--host", type=str, default=DEFAULT_URL, help="Host of the backend and frontend servers")
    parser.add_argument("--backend-port", type=int, default=DEFAULT_BACKEND_PORT, help="Port of the backend server")
    parser.add_argument("--frontend-port", type=int, default=DEFAULT_PORT, help="Port of the frontend server")
    parser.add_argument(
        "--secret",
        type=str,
        default=os.environ.get("SNAP_SECRET"),
        help="Secret key used to sign the JWT tokens (default: $SNAP_SECRET, or a random key)",
    )
    args = parser.parse_args()

    secret = args.secret or secrets.token_urlsafe(32)
    # The client is authenticated on the session created at the backend startup
    session_id = uuid.uuid4().hex
    jwt = Authenticator(secret=secret).create_access_token(TokenData(sid=session_id))

    # The secret is given through the environment to hide it from ps
    env = os.environ.copy()
    env["SNAP_SECRET"] = secret
    # Allow the frontend to call the backend (CORS)
    frontend_origin = f"http://{args.host}:{args.frontend_port}"
    env["SNAP_ALLOW_ORIGINS"] = ",".join(o for o in [env.get("SNAP_ALLOW_ORIGINS"), frontend_origin] if o)
    api_url = f"http://{args.host}:{args.backend_port}"
    backend = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "snapserve",
            "--host",
            args.host,
            "--port",
            str(args.backend_port),
            "--session",
            session_id,
        ],
        env=env,
    )
    try:
        wait_for_backend(backend, api_url)
        client_main(["--host", args.host, "--port", str(args.frontend_port), "--api-url", api_url, "--jwt", jwt])
    finally:
        backend.terminate()
        backend.wait()


if __name__ == "__main__":
    main()
