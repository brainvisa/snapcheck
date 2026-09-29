from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import os.path as op
import mimetypes
from lepton.session.controller import CRUDRouter, SessionStore, get_session_from_token
from tempfile import mkdtemp
import shutil
from starlette.background import BackgroundTask

from snapcheck.snap.snap import Snap


class SnapRouter(CRUDRouter):
    def __init__(self, store: SessionStore):
        super().__init__(store)
        self.add_api_route("/{snap_id}/image/{src:path}", self.get_image, methods=["GET"])
        self.add_api_route("/{snap_id}/html/{path:path}", self.export_as_html, methods=["POST"])
        self.add_api_route("/{snap_id}/pdf/{path:path}", self.export_as_pdf, methods=["POST"])
        self.add_api_route("/{snap_id}/html/{path:path}", self.download_as_html, methods=["GET"], response_class=FileResponse)
        self.add_api_route("/{snap_id}/pdf/{path:path}", self.download_as_pdf, methods=["GET"], response_class=FileResponse)


    def get_image(self, snap_id: str, src: str, session=Depends(get_session_from_token)):
        from os.path import realpath, commonpath

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
        item = self.store.get_by_id(snap_id)
        if not item:
            raise HTTPException(status_code=404, detail="Snap not found")
        item.object.export_to_html(Path(path))

    def export_as_pdf(self, snap_id: str, path: str):
        item = self.store.get_by_id(snap_id)
        if not item:
            raise HTTPException(status_code=404, detail="Snap not found")
        item.object.export_to_pdf(Path(path))

    def download_as_html(self, snap_id: str, session=Depends(get_session_from_token)):
        """ Export as HTML in a temporary directory, zip it and stream the zip. """
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
        """ Export as PDF in a temporary directory and stream the PDF. """
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