import os.path as op
from os.path import commonpath, realpath

from fastapi import APIRouter, Depends, HTTPException
from lepton.session.controller import get_session_from_token
from snapserve.content.models import ContentModel

CONTENT_DIR = op.abspath(op.join(op.dirname(__file__), "static"))

router = APIRouter()


@router.get("/{path:path}", response_model=ContentModel)
def get_static_content(path: str, session=Depends(get_session_from_token)) -> ContentModel:
    try:
        f = realpath(op.join(CONTENT_DIR, path))
        content_dir_real = realpath(CONTENT_DIR)

        if commonpath([f, content_dir_real]) != content_dir_real:
            raise HTTPException(status_code=403, detail="Access denied")

        if not op.isfile(f):
            raise HTTPException(status_code=404, detail="File not found")

        with open(f, "r") as file:
            content = file.read()

        return ContentModel(path=path, content=content)
    except (ValueError, OSError):
        raise HTTPException(status_code=403, detail="Access denied")
