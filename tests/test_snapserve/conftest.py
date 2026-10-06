import os
import sys

# snapserve / lepton live under source trees that are not pip-installed in the
# dev env; make them importable for the API tests.
_HERE = os.path.dirname(__file__)
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
for _p in (
    os.path.join(_ROOT, "python"),
    os.path.abspath(os.path.join(_ROOT, "..", "lepton", "backend")),
    os.path.abspath(os.path.join(_ROOT, "..", "lepton-common")),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)
