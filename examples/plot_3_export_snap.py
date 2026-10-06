"""
.. _example_export_snap:

=============
Export a snap
=============

Export a snap as a static website (HTML), to share the results of a review with people who do not
use SnapCheck.
"""

# %%
# Create and load a snap
# ----------------------
# The snap must be loaded from a file with :func:`~snapcheck.snap.snap.load_snap` to be exported:
# the images are copied from the snap file. Here, a snap is created and saved first, as in
# :ref:`sphx_glr_auto_examples_plot_1_create_snap.py`.

import tempfile
from pathlib import Path

from snapcheck.snap import Board, ImageElement, Snap, load_snap
from snapcheck.snap.rating import Rating, RatingScale, RatingScaleItem

try:
    DATA_DIR = Path(__file__).parent / "test_data"
except NameError:  # The documentation build runs the examples from their directory
    DATA_DIR = Path("test_data")

scale = RatingScale(
    description="Quality",
    ratings=[
        RatingScaleItem(name="Bad", value=0, color="#5f3c00"),
        RatingScaleItem(name="Good", value=1, color="#364900"),
    ],
)
axial = Rating(name="Axial view", scale=scale, value=1)
lightbox = Rating(name="Lightbox", scale=scale, value=0, comment="Missing slices")
boards = [
    Board(title="Axial view", elements=[ImageElement(src=str(DATA_DIR / "mni_axial.png"), intended_ratings=[axial])]),
    Board(
        title="Lightbox", elements=[ImageElement(src=str(DATA_DIR / "mni_lightbox.png"), intended_ratings=[lightbox])]
    ),
]

output_dir = Path(tempfile.mkdtemp())
Snap(title="MNI template QC", boards=boards).save(str(output_dir / "mni_qc.snpk"))

snap = load_snap(str(output_dir / "mni_qc.snpk"))

# %%
# Export as a website
# -------------------
# :meth:`~snapcheck.snap.snap.Snap.export_to_html` writes a home page (``00_INDEX.html``) and a
# page per board, showing its elements and its ratings, in a directory. With ``compress=True``,
# the directory is also compressed in a zip file. Open ``00_INDEX.html`` in a web browser.

website_dir = output_dir / "website"
snap.export_to_html(str(website_dir))

for path in sorted(website_dir.rglob("*")):
    print(path.relative_to(website_dir))

snap.close()
