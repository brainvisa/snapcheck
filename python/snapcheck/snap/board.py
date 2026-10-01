"""Boards: the pages of a snap."""

from dataclasses import dataclass, field

from lepton_common.objects import Serializable
from snapcheck.core.renderable import HTMLRenderable
from snapcheck.snap.elements import AbstractElement, list_elements
from snapcheck.snap.rating import Rating


@dataclass
class Board(Serializable, HTMLRenderable):
    """A page of a snap: a set of elements displayed together.

    The reviewer goes through the boards one by one and fills in the ratings intended by their
    elements.

    Parameters
    ----------
    title : str
        Title of the board, displayed in the list of the boards.
    description : str
        Instructions for the reviewer.
    style : dict of str
        CSS style of the board (ex: ``{"gap": "8px"}``).
    elements : list of AbstractElement
        The graphical elements of the board, displayed in this order.
    """

    title: str = "Untitled Board"
    description: str = ""

    style: dict[str, str] = field(default_factory=dict)  # Board CSS style

    elements: list[AbstractElement] = field(default_factory=list)  # Graphical elements of the board

    @property
    def all_intended_ratings(self) -> list[Rating]:
        """The ratings intended by the elements of the board (including the elements in rows), without
        duplicates (same id)."""
        ratings = {}
        for el in self.get_all_elements():
            for r in el.intended_ratings:
                ratings.setdefault(r.id, r)
        return list(ratings.values())

    def get_all_elements(self) -> list[AbstractElement]:
        """Return a flat list of all elements in the board, including those in rows."""
        return list_elements(self.elements)

    # HTML Rendering
    def _generate_board_html_sidebar(self) -> str:
        sidebar = """<div class='snap-sidebar'>
            <h3>Ratings</h3>
            <table class="snap-sidebar-table">"""
        for rating in self.all_intended_ratings:
            sidebar += f"<tr><th>{rating.name} </th><td>{rating.value}</td></tr>"
        sidebar += "</table></div>"
        return sidebar

    def get_html_content(self) -> str:
        """Return the HTML of the board content: a sidebar with the ratings and the elements."""
        content_html = "".join(
            item.to_html() if isinstance(item, HTMLRenderable) else str(item) for item in self.elements
        )
        html = f"""
            <div class="snap-board">
                {self._generate_board_html_sidebar()}
                <div class="snap-board-content">
                    {content_html}
                </div>
            </div>
        """
        return html

    def to_html(self, save_path: str | None = None) -> str:
        """Render the board as HTML.

        Parameters
        ----------
        save_path : str or None
            If given, the HTML is also written in this file.

        Returns
        -------
        str
            The HTML of the board.
        """
        # Forward additional rendering options (e.g., fill_missing) and ensure title
        html = super().to_html(title=self.title, _style=self.style)

        if save_path is not None:
            with open(save_path, "w") as f:
                f.write(html)
        return html
