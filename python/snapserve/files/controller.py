"""Route to browse the directories of the server (used by the file browser of the GUI)."""

import os.path as op
from os import listdir
from os.path import realpath

from fastapi import APIRouter, Depends, HTTPException
from lepton.session.controller import get_session_from_token
from lepton.utils import get_lepton_app
from snapserve.files.models import DirectoryItemModel, DirectoryModel

router = APIRouter()


@router.get("/{path:path}", response_model=DirectoryModel)
@router.get("/", response_model=DirectoryModel, name="list_root_directory")
def list_directory(
    path: str = None,  # noqa: RUF013 - kept as is, it defines the API schema
    extensions: list[str] | None = None,
    session=Depends(get_session_from_token),
    app=Depends(get_lepton_app),
):
    """List a directory of the server: its sub-directories, then its files.

    Without `path`, the directory set in the `files.default_path` setting is listed. If
    `extensions` is given, only the files with one of these extensions are listed.
    """
    if path is None:
        path = app.settings.get("files.default_path").value

    try:
        path_real = realpath(path)
    except (ValueError, OSError):
        raise HTTPException(status_code=403, detail="Access denied")

    if not op.isdir(path_real):
        raise HTTPException(status_code=404, detail="Directory not found")

    dirs = []
    files = []
    for item in sorted(listdir(path_real)):
        item_path = op.join(path_real, item)
        if op.isdir(item_path):
            dirs.append(item)
        elif extensions is not None:
            _, ext = op.split(item)
            if ext in extensions:
                files.append(item)
        else:
            files.append(item)

    content = [
        DirectoryItemModel(path=op.join(path_real, item), filename=item, isdir=op.isdir(op.join(path_real, item)))
        for item in dirs + files
    ]

    directory = DirectoryModel(
        path=path_real, content=content, parent=realpath(op.join(path_real, "..")) if path_real != "/" else None
    )

    return directory
