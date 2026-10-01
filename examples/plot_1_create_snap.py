"""
.. _example_create_snap:

=============
Create a snap
=============

Create a snap to check views of the MNI template: a rating scale, the ratings to fill in, two
boards displaying the images, then save it in a ``.snpk`` file to review it in the application.
"""

# %%
# The images to review
# --------------------
# In a real pipeline, the images are the figures produced by the processing. This example uses
# the images of the ``test_data`` directory, next to the examples.

import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.image import imread
from snapcheck.snap import Board, ImageElement, Snap
from snapcheck.snap.rating import Rating, RatingScale, RatingScaleItem

try:
    DATA_DIR = Path(__file__).parent / "test_data"
except NameError:  # The documentation build runs the examples from their directory
    DATA_DIR = Path("test_data")

images = {view: DATA_DIR / f"mni_{view}.png" for view in ("axial", "coronal", "lightbox")}

fig, axes = plt.subplots(1, 3, figsize=(12, 3.5), width_ratios=[1, 1, 1.7])
for ax, (view, path) in zip(axes, images.items(), strict=True):
    ax.imshow(imread(path))
    ax.set_title(view)
    ax.axis("off")
plt.show()

# %%
# The rating scale
# ----------------
# A scale lists the levels the reviewer chooses from. Each level has a name, a value (stored in
# the rating once chosen) and a color, used to display it in the application.

scale = RatingScale(
    description="Quality",
    ratings=[
        RatingScaleItem(name="Too bad", value=0, description="Unusable", color="#330C00"),
        RatingScaleItem(name="Bad", value=1, description="Usable with care", color="#5f3c00"),
        RatingScaleItem(name="Good", value=2, description="Minor defects", color="#5A5400"),
        RatingScaleItem(name="Perfect", value=3, description="No defect", color="#364900"),
    ],
)
scale.check()  # Raises an error if two levels have the same name or value

# %%
# The ratings
# -----------
# A rating is a question to answer. Its ``id`` is generated from its name when it is not given.
# A rating without scale only collects a comment.

axial = Rating(name="Axial view", description="Quality of the axial view", scale=scale)
coronal = Rating(name="Coronal view", description="Quality of the coronal view", scale=scale)
lightbox = Rating(name="Lightbox", description="Quality of the slices of the lightbox", scale=scale)
observations = Rating(name="Observations", description="General observations")

print(axial.id, coronal.id, lightbox.id, observations.id)

# %%
# The boards
# ----------
# A board is a page of the snap. Each element indicates the ratings to fill in by looking at it
# (``intended_ratings``): the application highlights them when the board is displayed.

views_board = Board(
    title="Axial & coronal views",
    description="Check the contrast and the orientation of the views.",
    elements=[
        ImageElement(title="Axial view", src=str(images["axial"]), intended_ratings=[axial]),
        ImageElement(title="Coronal view", src=str(images["coronal"]), intended_ratings=[coronal]),
    ],
)
lightbox_board = Board(
    title="Lightbox",
    description="Check all the slices.",
    elements=[ImageElement(title="Lightbox", src=str(images["lightbox"]), intended_ratings=[lightbox])],
)

# %%
# The snap
# --------
# The snap gathers all the ratings and the boards. The ratings intended by the elements must be
# in the ratings of the snap. The metadata are free.

snap = Snap(
    title="MNI template QC",
    description="Visual check of the MNI template",
    metadata={"template": "MNI152", "version": "1.0"},
    boards=[views_board, lightbox_board],
)

output_dir = Path(tempfile.mkdtemp())
snap_file = output_dir / "mni_qc.snpk"
snap.save(str(snap_file))
print(f"Snap saved in {snap_file}")

# %%
# Open it in the SnapCheck application to review it (see the :ref:`user guide <user_guide>`), or
# read it with python (see :ref:`sphx_glr_auto_examples_plot_2_read_ratings.py`).
