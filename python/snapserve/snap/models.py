"""API models of the snaps."""

from pydantic import BaseModel
from snapcheck.snap.elements import ElementUnion
from snapcheck.snap.rating import Rating


class BoardModel(BaseModel):
    """A board of a snap.

    Attributes
    ----------
    title : str
        Title of the board.
    description : str
        Instructions for the reviewer.
    style : dict
        CSS style of the board.
    elements : list of element
        The elements of the board.
    """

    title: str
    description: str
    # all_intended_ratings: List[RatingModel] # TODO add this or not ? (already in elements)
    style: dict[str, str]
    elements: list[ElementUnion]  # Use the union instead of AbstractElement


class SnapModel(BaseModel):
    """A snap opened in the backend, with its content and its editing state.

    Attributes
    ----------
    title : str or None
        Title of the snap.
    description : str or None
        Description of the snap.
    metadata : dict
        Free metadata of the snap.
    ratings : list of Rating
        The ratings of the snap, with their values and comments.
    boards : list of BoardModel
        The boards of the snap.
    id : str or None
        Identifier of the opened snap in the backend, used in the routes.
    version : int
        Version of the snap, incremented at each modification.
    has_changed : bool
        True if the snap has unsaved modifications.
    filename : str or None
        Path of the snap file.
    is_cancellable : bool
        True if a modification can be undone.
    is_redoable : bool
        True if an undone modification can be redone.
    """

    title: str | None = None
    description: str | None = None
    metadata: dict
    ratings: list[Rating] = []
    boards: list[BoardModel] = []

    id: str | None = None
    version: int = 0
    has_changed: bool = False
    filename: str | None = None
    is_cancellable: bool = False
    is_redoable: bool = False


class SnapShortModel(BaseModel):
    """Summary of an opened snap, without its content.

    Attributes
    ----------
    title : str or None
        Title of the snap.
    description : str or None
        Description of the snap.
    id : str or None
        Identifier of the opened snap in the backend.
    has_changed : bool
        True if the snap has unsaved modifications.
    filename : str or None
        Path of the snap file.
    """

    title: str | None = None
    description: str | None = None
    id: str | None = None
    has_changed: bool = False
    filename: str | None = None


class SnapCheckSessionModel(BaseModel):
    """A GUI session and the snaps it has opened.

    Attributes
    ----------
    id : str
        Identifier of the session.
    last_access : float
        Time of the last access (seconds since the epoch).
    items : list of SnapShortModel
        The snaps opened in the session.
    """

    id: str
    last_access: float
    items: list[SnapShortModel] = []
