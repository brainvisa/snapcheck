"""Graphical annotations drawn over an element (ex: an arrow pointing to an area of an image).

Annotations are added to :attr:`snapcheck.snap.elements.AbstractElement.annotations`.

.. note:: The annotations are saved in the snaps, but not displayed by the GUI yet.
"""

import uuid

from pydantic import BaseModel, ConfigDict


class Annotation(BaseModel):
    """Base class of the annotations."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    id: str = ""
    """Identifier of the annotation."""

    x: float = 0.0
    """Horizontal position of the annotation, in pixels from the left of the element."""
    y: float = 0.0
    """Vertical position of the annotation, in pixels from the top of the element."""
    rotation: float = 0.0
    """Rotation of the annotation, in degrees."""

    color: str = "red"
    """CSS color of the annotation."""

    text: str = ""
    """Text displayed with the annotation."""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


class CircleAnnotation(Annotation):
    """A circle centered on (x, y)."""

    radius: float = 10.0
    """Radius of the circle, in pixels."""


class RectangleAnnotation(Annotation):
    """A rectangle whose top left corner is (x, y)."""

    width: float = 10.0
    """Width of the rectangle, in pixels."""
    height: float = 10.0
    """Height of the rectangle, in pixels."""


class ArrowAnnotation(Annotation):
    """An arrow pointing to (x, y)."""

    length: float = 10.0
    """Length of the arrow, in pixels."""
    width: float = 2.0
    """Width of the arrow line, in pixels."""
