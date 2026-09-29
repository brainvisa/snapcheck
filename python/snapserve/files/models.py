"""API models of the file browser."""

from pydantic import BaseModel, ConfigDict


class DirectoryItemModel(BaseModel):
    """A file or a sub-directory of a directory."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    path: str
    """Absolute path of the item."""
    filename: str
    """Name of the item."""
    isdir: bool
    """True if the item is a directory."""


class DirectoryModel(BaseModel):
    """The content of a directory."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    path: str
    """Absolute path of the directory."""
    content: list[DirectoryItemModel]
    """The sub-directories, then the files of the directory."""
    parent: str | None = None
    """Absolute path of the parent directory, None for the root directory."""


# class FileModel(BaseModel):
#     description: str
#     notes: List[NoteScaleItem]
