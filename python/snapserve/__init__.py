"""The SnapCheck backend: a REST API serving the snaps to the GUI.

It is a Lepton application (see :mod:`snapserve.app`). Run it with ``python -m snapserve``.
"""

from .app import app, config

__all__ = ["app", "config"]
