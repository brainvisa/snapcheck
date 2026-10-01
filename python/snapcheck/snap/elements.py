"""Elements: the graphical items displayed in the boards (images, texts, rows...).

The elements are pydantic models, discriminated by their ``type`` field. :data:`ElementUnion`
lists the types that can be used in a board.
"""

import os.path as op
import shutil
from collections.abc import Iterable
from dataclasses import field
from typing import Literal, Union
from warnings import warn

from pydantic import BaseModel
from snapcheck.core.renderable import HTMLRenderable
from snapcheck.snap.annotation import Annotation
from snapcheck.snap.rating import Rating


class AbstractElement(BaseModel, HTMLRenderable):
    """Base class of the elements.

    Attributes
    ----------
    type : str
        Type of the element, used to deserialize it and to choose how the GUI displays it.
    title : str or None
        Title of the element (alternative text of the images in the HTML export).
    style : dict
        CSS style of the element.
    intended_ratings : list of Rating
        The ratings to fill in by looking at this element. They must also be in the ratings of the
        snap.
    annotations : list of Annotation
        Annotations drawn over the element.
    """

    type: Literal["unknown"] = "unknown"
    title: str | None = None
    style: dict[str, str] = field(default_factory=dict)
    intended_ratings: list[Rating] = field(default_factory=list)
    annotations: list[Annotation] = field(default_factory=list)

    def get_html_content(self):
        """Return the HTML of the element content."""
        return "?"

    def to_html(self):
        """Render the element as HTML."""
        return super().to_html(_style=self.style)


class Element(AbstractElement):
    """A generic element displaying a content: a text, HTML or other elements.

    Attributes
    ----------
    content : str, element, list or None
        The content to display: a text, an element or a list of them. The application displays the
        texts as is, the HTML export inserts them in the page (they can contain HTML).
    """

    type: Literal["default"] = "default"
    content: Union[str, "ElementUnion", None, list[Union["ElementUnion", str, None]]] = None

    def get_html_content(self) -> str:
        """Return the content of the element."""
        return self.content


class RowElement(Element):
    """Display several elements side by side.

    A row behaves like a list of its content: it can be iterated, indexed and modified with
    ``append``, ``extend``, ``insert``, ``remove``, ``pop``...

    Attributes
    ----------
    style : dict
        CSS style of the row, ``{"display": "flex"}`` by default.
    content : list
        The elements of the row, displayed from left to right.
    """

    type: Literal["row"] = "row"
    style: dict = field(default_factory=lambda: {"display": "flex"})
    content: list[Union[str, "ElementUnion", None, list[Union["ElementUnion", str, None]]]] = field(
        default_factory=list
    )

    def __len__(self):
        return len(self.content)

    def __getitem__(self, index):
        return self.content[index]

    def __setitem__(self, index, value):
        self.content[index] = value

    def __delitem__(self, index):
        del self.content[index]

    def __iter__(self):
        return iter(self.content)

    def append(self, item):
        self.content.append(item)

    def extend(self, items):
        self.content.extend(items)

    def insert(self, index, item):
        self.content.insert(index, item)

    def remove(self, item):
        self.content.remove(item)

    def pop(self, index=-1):
        return self.content.pop(index)

    def clear(self):
        self.content.clear()

    def index(self, item, *args):
        return self.content.index(item, *args)

    def count(self, item):
        return self.content.count(item)

    def sort(self, *args, **kwargs):
        self.content.sort(*args, **kwargs)

    def reverse(self):
        self.content.reverse()

    def copy(self):
        return self.content.copy()


class FileElement(AbstractElement):
    """An element displaying a file.

    When the snap is saved, the file is copied in the snap archive and :attr:`src` becomes
    relative to the archive (:attr:`is_local` is then True).

    Attributes
    ----------
    is_local : bool
        True when the source path is relative to the snap archive.
    src : str
        Path of the file. Relative paths are relative to the current directory when the snap is
        saved.
    """

    type: Literal["file"] = "file"
    is_local: bool = False
    src: str = ""

    def __post_init__(self):
        if not self.is_local:
            # Need to get the full path when initializing the element
            # When the element is alreayd local, keep the relative path
            self.src = op.abspath(self.src)

    def export_to_local(self, root_dir, subdir: str, source_tracker: dict | None = None):
        """Copy the file in a directory and make :attr:`src` relative to it.

        Used when saving a snap. If the file does not exist, :attr:`src` is emptied and a warning
        is emitted.

        Parameters
        ----------
        root_dir : str
            Root directory, :attr:`src` becomes relative to it.
        subdir : str
            Sub-directory of ``root_dir`` where the file is copied. It is created if needed. If a
            file with the same name already exists, a numeric suffix is added.
        source_tracker : dict or None
            Files already copied (source path: new relative path), to copy each file only once.
            It is updated with the copied file.
        """

        if not op.isfile(self.src):
            warn(f"'{self.src}' doest not exist. Cannot export it then replacing with an empty source.")
            self.src = ""

        if self.src != "":
            if source_tracker is not None and self.src in source_tracker:
                self.src = source_tracker[self.src]
            else:
                # Ensure target directory exists
                target_dir = op.join(root_dir, subdir)
                if not op.exists(target_dir):
                    from os import makedirs

                    makedirs(target_dir, exist_ok=True)

                fname = op.basename(self.src)
                abs_target = op.join(root_dir, subdir, fname)
                i = 1
                pfx, ext = op.splitext(fname)
                while op.isfile(abs_target):
                    sub_fname = f"{pfx}_{i}{ext}"
                    abs_target = op.join(root_dir, subdir, sub_fname)
                    i += 1
                rel_target = op.relpath(abs_target, root_dir)
                shutil.copy(self.src, abs_target)
                if source_tracker is not None:
                    source_tracker[self.src] = rel_target
                self.src = rel_target
        self.is_local = True


class ImageElement(FileElement):
    """An image (PNG, JPEG, GIF, SVG...)."""

    type: Literal["image"] = "image"

    def get_html_content(self) -> str:
        """Return an ``<img>`` tag displaying the image."""
        return f"<img src='{self.src}' alt='{self.title or ''}' />"


# Union of all element types
ElementUnion = ImageElement | FileElement | RowElement | Element
"""The element types that can be used in a board."""


def list_elements(item: list | ElementUnion) -> list[ElementUnion]:
    """List recursively the elements of an element or of a list of elements.

    Parameters
    ----------
    item : list or element
        An element (its content is also listed, for example the elements of a row) or a list of
        elements.

    Returns
    -------
    list of element
        A flat list of the elements.
    """
    elements = []

    if isinstance(item, AbstractElement):
        elements.append(item)

    if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
        for el in item:
            elements.extend(list_elements(el))
    return elements
