"""Elements for tractography data."""

from typing import Literal

from snapcheck.snap.elements import FileElement


class TractElement(FileElement):
    """A tractography file (``.tck``), to display in a 3D viewer."""

    type: Literal["tract"] = "tract"

    def get_html_content(self) -> str:
        """Return the container of the 3D viewer."""
        return "<div class='viewer-3d' />"
