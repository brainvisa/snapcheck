"""API models of the file browser."""

from pydantic import BaseModel


class DirectoryItemModel(BaseModel):
    """A file or a sub-directory of a directory.

    Attributes
    ----------
    path : str
        Absolute path of the item.
    filename : str
        Name of the item.
    isdir : bool
        True if the item is a directory.
    """

    path: str
    filename: str
    isdir: bool


class DirectoryModel(BaseModel):
    """The content of a directory.

    Attributes
    ----------
    path : str
        Absolute path of the directory.
    content : list of DirectoryItemModel
        The sub-directories, then the files of the directory.
    parent : str or None
        Absolute path of the parent directory, None for the root directory.
    """

    path: str
    content: list[DirectoryItemModel]
    parent: str | None = None


# class FileModel(BaseModel):
#     description: str
#     notes: List[NoteScaleItem]
