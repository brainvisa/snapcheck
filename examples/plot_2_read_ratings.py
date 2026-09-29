"""
.. _example_read_ratings:

==================================
Read the ratings of reviewed snaps
==================================

Once the snaps have been reviewed in the application, their ratings are saved in the snap files.
This example reads them, then gathers the ratings of a whole study.
"""

# %%
# Create the snaps of a study
# ---------------------------
# First, create a snap per subject, as in :ref:`sphx_glr_auto_examples_plot_1_create_snap.py`.

import random
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
from snapcheck.snap import Board, ImageElement, Snap, load_snap
from snapcheck.snap.rating import Rating, RatingScale, RatingScaleItem

try:
    DATA_DIR = Path(__file__).parent / "test_data"
except NameError:  # The documentation build runs the examples from their directory
    DATA_DIR = Path("test_data")

scale = RatingScale(
    description="Quality",
    ratings=[
        RatingScaleItem(name="Too bad", value=0, color="#330C00"),
        RatingScaleItem(name="Bad", value=1, color="#5f3c00"),
        RatingScaleItem(name="Good", value=2, color="#5A5400"),
        RatingScaleItem(name="Perfect", value=3, color="#364900"),
    ],
)


def create_snap(subject: str) -> Snap:
    """Create the snap of a subject."""
    axial = Rating(name="Axial view", scale=scale)
    coronal = Rating(name="Coronal view", scale=scale)
    board = Board(
        title="Views",
        elements=[
            ImageElement(title="Axial", src=str(DATA_DIR / "mni_axial.png"), intended_ratings=[axial]),
            ImageElement(title="Coronal", src=str(DATA_DIR / "mni_coronal.png"), intended_ratings=[coronal]),
        ],
    )
    return Snap(title=f"QC of {subject}", metadata={"subject": subject}, ratings=[axial, coronal], boards=[board])


study_dir = Path(tempfile.mkdtemp())
subjects = [f"S{i:02d}" for i in range(1, 9)]
for subject in subjects:
    create_snap(subject).save(str(study_dir / f"{subject}.snpk"))

# %%
# Simulate the review
# -------------------
# The reviewer rates the snaps in the application. Here, random values are set with
# :meth:`~snapcheck.snap.snap.Snap.update_rating` instead, and a comment is written on the bad
# ratings.

random.seed(0)
for subject in subjects:
    snap = load_snap(str(study_dir / f"{subject}.snpk"))
    for rating in snap.ratings:
        snap.update_rating(rating.id, random.choices([0, 1, 2, 3], weights=[1, 2, 4, 4])[0])
        if rating.value < 2:
            rating.comment = "Low contrast"
    snap.save()
    snap.close()

# %%
# Read the ratings of a snap
# --------------------------
# Load the snap with :func:`~snapcheck.snap.snap.load_snap` and read its ratings. The chosen level
# is found in the scale of the rating from its value. Close the snap to remove the temporary
# directory where the snap file has been extracted.

snap = load_snap(str(study_dir / "S01.snpk"))
print(snap.title, snap.metadata)
for rating in snap.ratings:
    level = next(item for item in rating.scale.ratings if item.value == rating.value)
    print(f"  {rating.name}: {rating.value} ({level.name}) - comment: {rating.comment}")
snap.close()

# %%
# Gather the ratings of the study
# -------------------------------
# Read all the snaps of the study in a table: a row per subject, a column per rating.

results = {}
for snap_file in sorted(study_dir.glob("*.snpk")):
    snap = load_snap(str(snap_file))
    results[snap.metadata["subject"]] = {rating.id: rating.value for rating in snap.ratings}
    snap.close()

rating_ids = ["axial_view", "coronal_view"]
print("subject", *rating_ids, sep="\t")
for subject, values in results.items():
    print(subject, *(values[r] for r in rating_ids), sep="\t\t")

# %%
# And count the subjects at each level of the scale, for each rating:

fig, ax = plt.subplots(figsize=(7, 3.5))
left = [0] * len(rating_ids)
for level in scale.ratings:
    counts = [sum(values[r] == level.value for values in results.values()) for r in rating_ids]
    ax.barh(rating_ids, counts, left=left, color=level.color, label=level.name)
    left = [a + b for a, b in zip(left, counts, strict=True)]
ax.set_xlabel("Number of subjects")
ax.legend(ncols=4, loc="upper center", bbox_to_anchor=(0.5, -0.2))
fig.tight_layout()
plt.show()
