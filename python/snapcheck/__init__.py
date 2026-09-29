"""Create, read and export snap files (``.snpk``).

The :mod:`snapcheck.snap` subpackage contains the data model of a snap: the snap itself,
its boards, their elements and the ratings.
"""

from .snap.snap import Snap

__all__ = ["Snap"]
