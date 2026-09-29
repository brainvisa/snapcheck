"""The Lepton application of the backend.

:data:`app` is a :class:`lepton.app.LeptonApp` managing snaps, with the Lepton routes (sessions,
objects, settings...), the snap specific routes of :class:`snapserve.snap.controller.SnapRouter`
and the ``/files`` and ``/content`` routes.

Environment variables:

- ``SNAP_ALLOW_ORIGINS``: additional origins allowed to call the API (CORS), comma separated.
- ``LAUNCH_SECRET``: secret required to create the first session, see Lepton.
"""

import os
from pathlib import Path

import snapserve.content.controller as content
import snapserve.files.controller as files
import snapserve.snap.controller as snap
from lepton.app import LeptonApp, LeptonConfig
from lepton_common.objects import IOHelper
from snapcheck.snap import load_snap, new_snap, save_snap
from snapserve.snap.models import SnapModel

launch_secret = os.getenv("LAUNCH_SECRET")

#: Configuration of the Lepton application.
config = LeptonConfig(
    app_name="SnapCheck",
    frontend_path=Path(__file__).parent.parent.parent / "snapcheck-front",
    config_dir=Path.home() / ".config/snapcheck",
    launch_secret=launch_secret,
)

# Additional origins allowed to call the API (CORS), comma separated (ex: http://127.0.0.1:3050)
extra_origins = [o.strip() for o in os.getenv("SNAP_ALLOW_ORIGINS", "").split(",") if o.strip()]
config.allow_origins = config.allow_origins + extra_origins

#: The Lepton application. The FastAPI application is ``app.app``.
app = LeptonApp(config, IOHelper(SnapModel, load_snap, save_snap, new_snap), crud_router_cls=snap.SnapRouter)
app.include_router(files.router, tags=["files"], prefix="/files")
app.include_router(content.router, tags=["content"], prefix="/content")

# Title and description of the OpenAPI schema, displayed by the interactive documentation of the
# API (/docs and /redoc) and in the SnapCheck documentation
app.app.title = "SnapCheck API"
app.app.description = """REST API of the SnapCheck backend, used by the GUI to open, edit and save snaps.

Create a session with `POST /session/`: it returns a JWT token. Give it to the other routes in the
`Authorization: Bearer <token>` header.
"""
