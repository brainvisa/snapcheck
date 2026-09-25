from typing import List
from fastapi import APIRouter, Depends, HTTPException
from lepton.utils import get_lepton_app
from lepton.session.controller import get_session_from_token
from snapserve.files.models import DirectoryItemModel, DirectoryModel
import os.path as op
from os.path import realpath, commonpath
from os import listdir

router = APIRouter()


@router.get("/{path:path}", response_model=DirectoryModel)
@router.get("/", response_model=DirectoryModel)
def list_directory(path: str = None, extensions: List[str]|None = None, session=Depends(get_session_from_token), app=Depends(get_lepton_app)):
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

    content = list(DirectoryItemModel(
        path=op.join(path_real, item),
        filename=item,
        isdir=op.isdir(op.join(path_real, item))
    ) for item in dirs + files)

    directory = DirectoryModel(
        path=path_real,
        content=content,
        parent=realpath(op.join(path_real, '..')) if path_real != '/' else None
    )

    return directory

