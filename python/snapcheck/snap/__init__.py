"""Data model of a snap: the snap, its boards, their elements and the ratings.

The most used classes and functions are available from this package, for example
``from snapcheck.snap import Snap, Board, ImageElement``.
"""

from snapcheck.snap.board import Board
from snapcheck.snap.elements import AbstractElement, Element, FileElement, ImageElement, RowElement
from snapcheck.snap.rating import Rating, RatingScale
from snapcheck.snap.snap import Snap, load_snap, new_snap, save_snap

__all__ = [
    "AbstractElement",
    "Board",
    "Element",
    "FileElement",
    "ImageElement",
    "Rating",
    "RatingScale",
    "RowElement",
    "Snap",
    "load_snap",
    "new_snap",
    "save_snap",
]
