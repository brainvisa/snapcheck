"""Ratings and rating scales.

A :class:`Rating` is what the reviewer fills in: a value chosen in a :class:`RatingScale` and/or a
free comment. The boards elements refer to the ratings they are made to evaluate
(see :attr:`snapcheck.snap.elements.AbstractElement.intended_ratings`).
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RatingScaleItem(BaseModel):
    """One level of a rating scale."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    name: str = ""
    """Short label of the level, displayed in the GUI (ex: "Good")."""
    value: int = 0
    """Value stored in the rating when this level is chosen. Must be unique in the scale."""
    description: str = ""
    """Longer explanation of the level, to help the reviewer."""
    color: str | None = None
    """CSS color used to display the level (ex: "green" or "#364900")."""


class RatingScale(BaseModel):
    """An ordered list of levels to choose from when rating.

    A scale is usually shared by several ratings.

    Examples
    --------
    >>> scale = RatingScale(
    ...     description="Quality",
    ...     ratings=[
    ...         RatingScaleItem(name="Bad", value=0, color="red"),
    ...         RatingScaleItem(name="Good", value=1, color="green"),
    ...     ],
    ... )
    >>> scale.check()
    """

    model_config = ConfigDict(use_attribute_docstrings=True)

    description: str = ""
    """Description of the scale."""
    ratings: list[RatingScaleItem] = Field(default_factory=list)
    """The levels of the scale.

    Their names and values must be unique (see :meth:`~snapcheck.snap.rating.RatingScale.check`).
    """

    def check(self):
        """Check the integrity of the scale.

        Raises
        ------
        ValueError
            If two levels have the same name or the same value.
        """
        names = []
        values = []
        for rating in self.ratings:
            if rating.name in names:
                raise ValueError(f"Duplicate rating name: {rating.name}")
            names.append(rating.name)
            if rating.value in values:
                raise ValueError(f"Duplicate rating value: {rating.value}")
            values.append(rating.value)


class Rating(BaseModel):
    """A rating to fill in during the quality control.

    The reviewer chooses a level of the :attr:`scale` and/or writes a :attr:`comment`.

    Examples
    --------
    >>> rating = Rating(name="Axial view", description="Quality of the axial view")
    >>> rating.id
    'axial_view'
    """

    model_config = ConfigDict(use_attribute_docstrings=True)

    id: str | None = None
    """Unique identifier of the rating in the snap. If not given, it is generated from the name
    (lower case, spaces replaced by underscores)."""
    name: str = ""
    """Name of the rating, displayed in the GUI."""
    description: str = ""
    """What has to be evaluated."""
    scale: RatingScale | None = None
    """Scale of the possible values. Leave it to None for a comment only rating."""

    is_boolean: bool = False
    """If True, the rating is a boolean (pass / fail)."""
    allow_comment: bool = True
    """If True, the reviewer can add a comment."""

    value: int | None = None
    """The chosen value: the value of a level of the scale, or None while the rating is not filled
    in."""
    comment: str | None = None
    """Comment of the reviewer."""

    @model_validator(mode="after")
    def generate_id(self):
        """Generate the id from the name when it is not given."""
        if self.id is None and self.name:
            # If not provided, generate an ID from the name
            self.id = self.name.lower().replace(" ", "_")
        return self
