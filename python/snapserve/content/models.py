"""API model of the static content."""

from pydantic import BaseModel


class ContentModel(BaseModel):
    """A static page.

    Attributes
    ----------
    path : str
        Path of the page.
    content : str
        HTML content of the page.
    """

    path: str
    content: str
