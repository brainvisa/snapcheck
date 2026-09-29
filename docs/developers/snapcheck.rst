.. _snapcheck_package:

=========================
The snapcheck package
=========================

The :mod:`snapcheck` python package creates, reads and exports the snap files. It does not depend
on the GUI: use it in the scripts of your processing pipelines to generate the snaps to review, and
to read the ratings once reviewed.

The :ref:`examples <general_examples>` show how to use it.


The data model
==============

The classes are available in :mod:`snapcheck.snap`:

.. code-block:: text

   Snap                          title, description, metadata, global_comment
   ├── ratings: [Rating]         all the ratings of the snap
   │     └── scale: RatingScale  └── ratings: [RatingScaleItem]  (name, value, color)
   └── boards: [Board]           title, description (instructions), style
         └── elements: [Element]
               ├── ImageElement  src  (a FileElement)
               ├── Element       content: a text, HTML or other elements
               └── RowElement    content: elements displayed side by side
               each one: title, style, intended_ratings: [Rating], annotations

- :class:`~snapcheck.snap.snap.Snap`: the document, saved in a ``.snpk`` file.
- :class:`~snapcheck.snap.board.Board`: a page of the snap, with the elements to display together.
- The elements (:mod:`snapcheck.snap.elements`): :class:`~snapcheck.snap.elements.ImageElement`,
  :class:`~snapcheck.snap.elements.Element` (a text or HTML content),
  :class:`~snapcheck.snap.elements.RowElement` (elements side by side)...
- :class:`~snapcheck.snap.rating.Rating`: a question to answer, with a
  :class:`~snapcheck.snap.rating.RatingScale` of possible values
  (:class:`~snapcheck.snap.rating.RatingScaleItem`) and a comment.
- The annotations (:mod:`snapcheck.snap.annotation`): arrows, circles and rectangles to draw over
  an element. They are saved in the snaps, but not displayed by the GUI yet.

The elements indicate the ratings they are made to evaluate (``intended_ratings``): the GUI
highlights the ratings of the current board and proposes them in the context menu of the elements.
These ratings must also be in :attr:`Snap.ratings <snapcheck.snap.snap.Snap>`, the list of all the
ratings of the snap. A rating can be shared by several elements, and a scale by several ratings.

A minimal snap:

.. code-block:: python

   from snapcheck.snap import Board, ImageElement, Snap
   from snapcheck.snap.rating import Rating, RatingScale, RatingScaleItem

   scale = RatingScale(
       description="Quality",
       ratings=[
           RatingScaleItem(name="Bad", value=0, color="#b71c1c"),
           RatingScaleItem(name="Good", value=1, color="#2e7d32"),
       ],
   )
   rating = Rating(name="Registration", description="Is the registration correct?", scale=scale)

   board = Board(
       title="Registration",
       description="Check the alignment of the image on the template.",
       elements=[ImageElement(title="Axial view", src="axial.png", intended_ratings=[rating])],
   )
   snap = Snap(title="QC of subject S01", ratings=[rating], boards=[board], metadata={"subject": "S01"})
   snap.save("S01.snpk")

Once reviewed, read the ratings:

.. code-block:: python

   from snapcheck.snap import load_snap

   snap = load_snap("S01.snpk")
   for rating in snap.ratings:
       print(rating.id, rating.value, rating.comment)
   snap.close()


The .snpk files
===============

A ``.snpk`` file is a zip archive containing:

- ``<name>.json``: the snap serialized in JSON;
- ``content/``: a copy of the files displayed by the elements. Each file is copied once, even if
  it is used by several elements.

When a snap is saved (:meth:`Snap.save <snapcheck.snap.snap.Snap.save>`), the files of the
elements are copied in the archive and their paths (``src``) become relative to it: a snap file can
be moved or shared without its source images. When it is loaded
(:func:`~snapcheck.snap.snap.load_snap`), the archive is extracted in a temporary directory, removed
by :meth:`Snap.close <snapcheck.snap.snap.Snap.close>`.

The JSON file is written by the serialization of ``lepton_common``: each object has a ``__cls__``
field giving its class, and the objects used several times (ratings, scales...) are stored once in
the ``_refs`` table, and referenced by ``"$@<class>#<index>"`` strings:

.. code-block:: json

   {
     "title": "QC of subject S01",
     "ratings": ["$@snapcheck.snap.rating.Rating#0"],
     "boards": ["$@snapcheck.snap.board.Board#0"],
     "__cls__": "snapcheck.snap.snap.Snap",
     "_refs": {
       "snapcheck.snap.rating.Rating": [
         {"id": "registration", "name": "Registration", "value": 1, "comment": null, "...": "..."}
       ],
       "...": "..."
     }
   }

Use :func:`~snapcheck.snap.snap.load_snap` rather than reading the JSON file directly.


Export
======

A snap loaded from a file (:func:`~snapcheck.snap.snap.load_snap`) can be exported:

- as a static website, with :meth:`Snap.export_to_html <snapcheck.snap.snap.Snap.export_to_html>`:
  a home page (``00_INDEX.html``) and a page per board, showing its elements and its ratings;
- as a PDF file, with :meth:`Snap.export_to_pdf <snapcheck.snap.snap.Snap.export_to_pdf>`: the
  home page, then a page per board.

See the :ref:`examples <general_examples>` and the :doc:`API reference <../api/index>`.
