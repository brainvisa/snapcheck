"""HTML rendering, used to export the snaps as HTML and PDF."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


@dataclass
class HTMLRenderable:
    """Mixin class to render an object as HTML.

    The subclasses define the content with :meth:`get_html_content`, :meth:`to_html` wraps it in a
    ``<div>``.
    """

    def get_html_content(self) -> Any:
        """Provide the content to be rendered inside the HTML element."""
        return ""

    def to_html(self, _style=None, _classes=None, _id=None, _template=None, **kwargs) -> str:
        """Render the object as HTML.

        Returns
        -------
        str
            The content of :meth:`get_html_content` in a ``<div>``. The content can be a string,
            an HTMLRenderable or a list of them.
        """
        html = "<div"
        if _id:
            html += f" id='{self.html_id}'"
        if _classes:
            html += f' class="{" ".join(self.html_classes)}"'
        if _style:
            style_str = "; ".join(f"{k}: {v}" for k, v in self.html_style.items())
            html += f' style="{style_str}"'
        html += ">"
        content = self.get_html_content()
        if isinstance(content, HTMLRenderable):
            content = content.to_html()
        elif isinstance(content, Iterable) and not isinstance(content, str):
            content = "".join(item.to_html() if isinstance(item, HTMLRenderable) else str(item) for item in content)

        return html + content + "</div>"
