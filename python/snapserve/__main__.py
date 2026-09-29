"""Run the backend: ``python -m snapserve [--host HOST] [--port PORT] [--secret SECRET] [--session ID]``."""

import argparse
import os

from lepton.app import DEFAULT_HOST, DEFAULT_PORT
from snapserve.app import app


def main():
    """Parse the command line and serve the API with uvicorn."""
    parser = argparse.ArgumentParser(
        description="Run the SnapServe server",
        epilog="Additional origins allowed to call the API (CORS) can be given with $SNAP_ALLOW_ORIGINS "
        "(comma separated), ex: SNAP_ALLOW_ORIGINS=http://127.0.0.1:3050",
    )
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help="The host to bind the server to")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="The port to bind the server to")
    parser.add_argument(
        "--secret",
        type=str,
        default=os.environ.get("SNAP_SECRET"),
        help="Secret key used to sign the JWT tokens (default: $SNAP_SECRET, or a random key)",
    )
    parser.add_argument("--session", type=str, default=None, help="Initialize the first session with this id")
    args = parser.parse_args()

    if args.secret:
        app.auth.secret = args.secret
    if args.session is not None:
        app.store.new_session(sess_id=args.session)

    app.start_uvicorn(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
