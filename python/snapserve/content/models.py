"""API model of the static content."""

from pydantic import BaseModel, ConfigDict


class ContentModel(BaseModel):
    """A static page."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    path: str
    """Path of the page."""
    content: str
    """HTML content of the page."""
