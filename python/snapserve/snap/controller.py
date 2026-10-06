"""Snap specific routes, added to the Lepton object routes (``/objects``)."""

import mimetypes
import os.path as op
import shutil
import time
from pathlib import Path
from tempfile import mkdtemp

from fastapi import Depends, HTTPException
from fastapi.responses import FileResponse
from lepton.session.controller import (
    CRUDRouter,
    FieldUpdateRequest,
    LightweightResponse,
    SessionStore,
    get_session_from_token,
)
from lepton.utils import get_lepton_app
from snapcheck.snap.snap import Snap
from starlette.background import BackgroundTask


class SnapRouter(CRUDRouter):
    """Router of the snaps: the Lepton object routes plus the images and the exports."""

    def __init__(self, store: SessionStore):
        super().__init__(store)
        self.add_api_route("/{snap_id}/image/{src:path}", self.get_image, methods=["GET"])
        self.add_api_route("/{snap_id}/html/{path:path}", self.export_as_html, methods=["POST"])
        self.add_api_route("/{snap_id}/pdf/{path:path}", self.export_as_pdf, methods=["POST"])
        self.add_api_route(
            "/{snap_id}/html/{path:path}", self.download_as_html, methods=["GET"], response_class=FileResponse
        )
        self.add_api_route(
            "/{snap_id}/pdf/{path:path}", self.download_as_pdf, methods=["GET"], response_class=FileResponse
        )
        self.add_api_route(
            "/{snap_id}/ratings/{rating_id}/reset",
            self.reset_rating_value,
            methods=["POST"],
            name="reset_rating",
            response_model=LightweightResponse,
        )

    def get_image(self, snap_id: str, src: str, session=Depends(get_session_from_token)):
        """Get a file displayed by an element of an opened snap.

        `src` is the path of the file in the snap archive (the `src` of the element). The files
        outside of the archive can not be accessed.
        """
        from os.path import commonpath, realpath

        item = self.store.get_by_id(snap_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Snap not found")

        normalized_src = src.lstrip("/")
        if not normalized_src:
            raise HTTPException(status_code=404, detail="Image not found")

        if item.object._dir:
            image_path = op.join(item.object._dir.name, normalized_src)
        else:
            image_path = src

        try:
            image_path_real = realpath(image_path)
            if item.object._dir:
                base_path_real = realpath(item.object._dir.name)
                if commonpath([image_path_real, base_path_real]) != base_path_real:
                    raise HTTPException(status_code=403, detail="Access denied")
        except (ValueError, OSError):
            raise HTTPException(status_code=403, detail="Access denied")

        if not op.isfile(image_path_real):
            raise HTTPException(status_code=404, detail="Image not found")

        mime_type, _ = mimetypes.guess_type(image_path_real)
        if mime_type is None:
            mime_type = "application/octet-stream"
        return FileResponse(
            image_path_real,
            media_type=mime_type,
            headers={"Content-Disposition": f'inline; filename="{op.basename(image_path_real)}"'},
        )

    def export_as_html(self, snap_id: str, path: str):
        """Export an opened snap as a static website, in the `path` directory of the server."""
        item = self.store.get_by_id(snap_id)
        if not item:
            raise HTTPException(status_code=404, detail="Snap not found")
        item.object.export_to_html(Path(path))

    def export_as_pdf(self, snap_id: str, path: str):
        """Export an opened snap as a PDF file, in `path` on the server."""
        item = self.store.get_by_id(snap_id)
        if not item:
            raise HTTPException(status_code=404, detail="Snap not found")
        item.object.export_to_pdf(Path(path))

    def download_as_html(self, snap_id: str, session=Depends(get_session_from_token)):
        """Download an opened snap exported as a static website, in a zip file."""
        item = self.store.get_by_id(snap_id)
        if not item:
            raise HTTPException(status_code=404, detail="Snap not found")
        snap: Snap = item.object
        # Keep the directory until the response has been fully sent, then remove it.
        temp_dir = mkdtemp(prefix="snapserve_export_")
        export_path = Path(temp_dir) / Path(snap._filepath).stem
        zip_path = snap.export_to_html(export_path, compress=True)
        return FileResponse(
            zip_path,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{op.basename(zip_path)}"'},
            background=BackgroundTask(shutil.rmtree, temp_dir, ignore_errors=True),
        )

    def download_as_pdf(self, snap_id: str, session=Depends(get_session_from_token)):
        """Download an opened snap exported as a PDF file."""
        item = self.store.get_by_id(snap_id)
        if not item:
            raise HTTPException(status_code=404, detail="Snap not found")
        snap: Snap = item.object
        temp_dir = mkdtemp(prefix="snapserve_export_")
        export_path = Path(temp_dir) / f"{Path(snap._filepath).stem}.pdf"
        snap.export_to_pdf(export_path)
        return FileResponse(
            export_path,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{op.basename(export_path)}"'},
            background=BackgroundTask(shutil.rmtree, temp_dir, ignore_errors=True),
        )

    def reset_rating_value(
        self, snap_id: str, rating_id: str, session=Depends(get_session_from_token), lepton=Depends(get_lepton_app)
    ):
        """Reset a rating of a snap to its default state (default value, no comment)."""
        item = self.store.get_by_id(snap_id)
        if not item:
            raise HTTPException(status_code=404, detail="Snap not found")
        snap: Snap = item.object
        rating = next((r for r in snap.ratings or [] if r.id == rating_id), None)
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")

        # Only bump the version when the rating was actually modified
        if not rating.is_default:
            rating.reset()
            snap._has_changed = True
            item.increment_version()
            self.autosave(snap_id, lepton)

        return LightweightResponse(ok=True, version=item.version, has_changed=snap._has_changed, timestamp=time.time())

    def update_field(
        self,
        snap_id: str,
        update: FieldUpdateRequest,
        session=Depends(get_session_from_token),
        lepton=Depends(get_lepton_app),
    ):
        """Update a field of a snap, then save it if the auto save is enabled."""
        resp = super().update_field(snap_id, update, session)
        if self.autosave(snap_id, lepton):
            resp.has_changed = False
        return resp

    def autosave(self, snap_id: str, lepton) -> bool:
        """Save the snap if it has unsaved changes and the ``snap.autosave`` setting is enabled.

        A failing save is logged but does not fail the modification. Returns True if the snap has been saved.
        """
        item = self.store.get_by_id(snap_id)
        if not item or not item.object._has_changed or not lepton.settings.get("snap.autosave").value:
            return False
        try:
            self.store.save(snap_id)
        except Exception:
            self.store.logger.exception(f"Auto save of {snap_id} failed")
            return False
        return True

    def on_field_update(self, snap_id, session, update, did_change):
        """Mark a rating as not default anymore when its value or comment is modified."""
        parts = update.field_path.split(".")
        if not did_change or len(parts) != 3 or parts[0] != "ratings" or parts[2] not in ("value", "comment"):
            return
        item = self.store.get_by_id(snap_id)
        if not item:
            return
        ratings = item.object.ratings or []
        selector = parts[1]
        if selector.startswith("{id:") and selector.endswith("}"):
            rating = next((r for r in ratings if r.id == selector[4:-1]), None)
        elif selector.isdigit() and int(selector) < len(ratings):
            rating = ratings[int(selector)]
        else:
            rating = None
        if rating:
            rating.is_default = False
