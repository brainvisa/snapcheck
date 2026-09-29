"""API models of the snaps."""

from pydantic import BaseModel, ConfigDict
from snapcheck.snap.elements import ElementUnion
from snapcheck.snap.rating import Rating


class BoardModel(BaseModel):
    """A board of a snap."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    title: str
    """Title of the board."""
    description: str
    """Instructions for the reviewer."""
    # all_intended_ratings: List[RatingModel] # TODO add this or not ? (already in elements)
    style: dict[str, str]
    """CSS style of the board."""
    elements: list[ElementUnion]  # Use the union instead of AbstractElement
    """The elements of the board."""


class SnapModel(BaseModel):
    """A snap opened in the backend, with its content and its editing state."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    title: str | None = None
    """Title of the snap."""
    description: str | None = None
    """Description of the snap."""
    metadata: dict
    """Free metadata of the snap."""
    ratings: list[Rating] = []
    """The ratings of the snap, with their values and comments."""
    boards: list[BoardModel] = []
    """The boards of the snap."""

    id: str | None = None
    """Identifier of the opened snap in the backend, used in the routes."""
    version: int = 0
    """Version of the snap, incremented at each modification."""
    has_changed: bool = False
    """True if the snap has unsaved modifications."""
    filename: str | None = None
    """Path of the snap file."""
    is_cancellable: bool = False
    """True if a modification can be undone."""
    is_redoable: bool = False
    """True if an undone modification can be redone."""


class SnapShortModel(BaseModel):
    """Summary of an opened snap, without its content."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    title: str | None = None
    """Title of the snap."""
    description: str | None = None
    """Description of the snap."""
    id: str | None = None
    """Identifier of the opened snap in the backend."""
    has_changed: bool = False
    """True if the snap has unsaved modifications."""
    filename: str | None = None
    """Path of the snap file."""


class SnapCheckSessionModel(BaseModel):
    """A GUI session and the snaps it has opened."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    id: str
    """Identifier of the session."""
    last_access: float
    """Time of the last access (seconds since the epoch)."""
    items: list[SnapShortModel] = []
    """The snaps opened in the session."""
