.. _ratings_lifecycle:

=========================
The lifecycle of ratings
=========================

A :class:`~snapcheck.snap.rating.Rating` is both a question (its definition: name, description,
scale...) and the answer of the reviewer (its ``value`` and ``comment``). It is referenced at two
places:

- :attr:`Snap.ratings <snapcheck.snap.snap.Snap>`: all the ratings of the snap;
- the ``intended_ratings`` of the elements: the ratings an element is made to evaluate.

The answer must be stored only once, so these two places must share the **same Python instances**.
This page explains how this is kept true when a snap is created, modified, saved, loaded and edited
in the GUI, and the cases where it is not automatic.

.. code-block:: text

   snap.ratings ─────────────────► Rating "registration" (value, comment)
                                    ▲                  ▲
   board 1 ── element A ── intended_ratings            │
   board 2 ── row ── element B ── intended_ratings ────┘

:attr:`Snap.ratings <snapcheck.snap.snap.Snap>` is the reference: the methods of the snap
(:meth:`~snapcheck.snap.snap.Snap.update_rating`), the backend and the GUI read and write the answers
there.


Linking the ratings
===================

:meth:`Snap.link_ratings <snapcheck.snap.snap.Snap.link_ratings>` makes the elements use the ratings
of the snap. The ratings are identified by their ``id`` (generated from the name when it is not
given):

1. the duplicates of :attr:`Snap.ratings <snapcheck.snap.snap.Snap>` (same id) are removed;
2. for each element of each board, including the elements in rows and in the content of other
   elements, each intended rating is replaced by the rating of the snap with the same id;
3. the intended ratings that are not in the snap are added to :attr:`Snap.ratings
   <snapcheck.snap.snap.Snap>`.

When several ratings have the same id, the first one is kept: the ratings of the snap, then the
ratings of the elements in the order of the boards. If their definitions are different (anything
but ``value`` and ``comment``), a ``UserWarning`` is emitted: it is probably a mistake, for example
two ratings named "Quality" for two different views. A rating without id (neither id nor name)
raises a ``ValueError``.

So the ratings intended by the elements do not have to be given to the snap:

.. code-block:: python

   rating = Rating(name="Registration", scale=scale)
   board = Board(elements=[ImageElement(src="axial.png", intended_ratings=[rating])])

   # Only the ratings that are not intended by an element have to be given
   snap = Snap(boards=[board], ratings=[Rating(name="Global quality", scale=scale)])
   assert snap.ratings[1] is rating


When are they linked?
=====================

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Step
     - What happens
   * - Creation (``Snap(...)``)
     - ``__post_init__`` calls :meth:`~snapcheck.snap.snap.Snap.link_ratings`.
   * - Modification of the structure
     - **Nothing**: see :ref:`below <ratings_not_linked>`.
   * - Save (:meth:`~snapcheck.snap.snap.Snap.save`)
     - :meth:`~snapcheck.snap.snap.Snap.link_ratings` is called, then the snap is serialized: each
       rating is written once.
   * - Load (:func:`~snapcheck.snap.snap.load_snap`)
     - The references of the file are resolved to the same instances, then ``__post_init__`` links
       the ratings again.
   * - Undo, redo and failed changes
     - The snap is rebuilt from a backup, then ``__post_init__`` links the ratings again.
   * - Edition in the GUI
     - The answers are modified in place, the ratings stay linked.


Save and load
-------------

The serialization of ``lepton_common`` stores the objects used several times only once: the
ratings are written in the ``_refs`` table of the JSON file, and :attr:`Snap.ratings
<snapcheck.snap.snap.Snap>` and the ``intended_ratings`` contain references to them (see
:ref:`the .snpk files <snapcheck_package>`). When the file is loaded, each reference is resolved to
the same instance, so the identity of the ratings is kept.

If two different instances were saved (a snap modified without calling
:meth:`~snapcheck.snap.snap.Snap.link_ratings`, or a file written by an older version), they are
written twice in the file. The call to :meth:`~snapcheck.snap.snap.Snap.link_ratings` in
``__post_init__`` then keeps the rating of :attr:`Snap.ratings <snapcheck.snap.snap.Snap>`, which
holds the answer.


Changes, undo and redo
----------------------

:class:`~snapcheck.snap.snap.Snap` is a ``LObject`` of ``lepton_common``: before each change made
with ``changing()`` (ex: :meth:`~snapcheck.snap.snap.Snap.update_rating`), the state of the snap is
serialized in a backup. ``revert_changes()`` (undo) and ``restore_changes()`` (redo) rebuild the
snap from these backups, and so does ``changing()`` when an exception is raised after a change.

The backups are serialized like the files (with the ``_refs`` table), so the ratings are still
shared after a restoration, and ``__post_init__`` links them again anyway.

.. warning::

   A restoration **recreates all the objects** of the snap: the boards, the elements and the
   ratings. The references kept outside the snap (in a variable of a script, for example) are not
   used by the snap anymore after an undo or a redo:

   .. code-block:: python

      rating = snap.ratings[0]
      snap.update_rating(rating.id, 1)
      snap.revert_changes()
      rating.value              # 1: this object is not in the snap anymore
      snap.ratings[0].value     # None

   Get the objects from the snap again after a restoration. ``changing()`` only restores the snap
   if something has been changed before the exception: an invalid change detected before modifying
   anything (ex: :meth:`~snapcheck.snap.snap.Snap.update_rating` with an unknown id) keeps the
   objects.


In the GUI
----------

The backend (:doc:`snapserve`) keeps the snap opened in memory, and the GUI modifies the answers
with ``PATCH`` requests on the field ``ratings.{id:<rating id>}.value`` (or ``comment``): the rating
is found in :attr:`Snap.ratings <snapcheck.snap.snap.Snap>` and modified in place, so the elements
see the new answer.

The snap is sent to the GUI without the ``_refs`` table: in the JSON received by the frontend, each
intended rating is a separate copy. In the frontend, **read and write the answers in**
``snap.ratings`` and only use the ``id`` of the ``intended_ratings`` (to know the ratings of a board
or of an element). ``getBoardIntendedRatings()`` and ``boardHasRating()``
(``snapcheck-front/src/lepton/utils/ratings.ts``) list the ratings of a board, including the
elements in rows.


.. _ratings_not_linked:

When are they not linked?
=========================

The ratings are not linked again when the structure of an existing snap is modified:

- a board or an element is added, with a rating that is not in the snap, or with a copy of a
  rating of the snap;
- a rating of :attr:`Snap.ratings <snapcheck.snap.snap.Snap>` is replaced (``snap.ratings[0] =
  ...``), or the list itself.

Until the next save, the new ratings cannot be answered
(:meth:`~snapcheck.snap.snap.Snap.update_rating` raises a ``ValueError``), and the answers are not
shared with the copies. Call :meth:`~snapcheck.snap.snap.Snap.link_ratings` after such a
modification:

.. code-block:: python

   snap.boards.append(Board(elements=[ImageElement(src="coronal.png", intended_ratings=[rating2])]))
   snap.link_ratings()
   snap.update_rating(rating2.id, 1)

The ratings of the removed elements stay in :attr:`Snap.ratings <snapcheck.snap.snap.Snap>`: their
answers are kept, and they can still be answered in the GUI.


Summary
=======

- :attr:`Snap.ratings <snapcheck.snap.snap.Snap>` holds the answers, the ``intended_ratings`` of the
  elements are the same instances.
- The ratings are identified by their ``id``: give different names (or ids) to different ratings.
- Call :meth:`~snapcheck.snap.snap.Snap.link_ratings` after adding boards or elements, or after
  replacing ratings, in an existing snap.
- Get the objects from the snap again after an undo or a redo.
- In the frontend, read and write the answers in ``snap.ratings``.
