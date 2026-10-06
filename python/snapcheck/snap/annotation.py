"""Graphical annotations drawn over an element (ex: an arrow pointing to an area of an image).

Annotations are added to :attr:`AbstractElement.annotations <snapcheck.snap.elements.AbstractElement>`.

.. note:: The annotations are saved in the snaps, but not displayed by the GUI yet.
"""

import uuid

from pydantic import BaseModel


class Annotation(BaseModel):
    """Base class of the annotations.

    Attributes
    ----------
    id : str
        Identifier of the annotation.
    x : float
        Horizontal position of the annotation, in pixels from the left of the element.
    y : float
        Vertical position of the annotation, in pixels from the top of the element.
    rotation : float
        Rotation of the annotation, in degrees.
    color : str
        CSS color of the annotation.
    text : str
        Text displayed with the annotation.
    """

    id: str = ""

    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0

    color: str = "red"

    text: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


class CircleAnnotation(Annotation):
    """A circle centered on (x, y).

    Attributes
    ----------
    radius : float
        Radius of the circle, in pixels.
    """

    radius: float = 10.0


class RectangleAnnotation(Annotation):
    """A rectangle whose top left corner is (x, y).

    Attributes
    ----------
    width : float
        Width of the rectangle, in pixels.
    height : float
        Height of the rectangle, in pixels.
    """

    width: float = 10.0
    height: float = 10.0


class ArrowAnnotation(Annotation):
    """An arrow pointing to (x, y).

    Attributes
    ----------
    length : float
        Length of the arrow, in pixels.
    width : float
        Width of the arrow line, in pixels.
    """

    length: float = 10.0
    width: float = 2.0
