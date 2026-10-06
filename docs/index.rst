.. _snapcheck:

=========
SnapCheck
=========

**SnapCheck is a desktop application to review and rate figures**, for the visual quality
control of data.

Processing pipelines produce figures that someone has to look at: views of an image, overlays of
a registration or of a segmentation, tractography renderings... SnapCheck gathers these figures
and the questions to answer about them in a single file, a *snap*. The reviewer opens it in the
application, goes through its pages, rates each figure on a predefined scale, writes comments and
saves the result in the same file.

.. figure:: _static/screenshots/main_window.png
   :alt: The SnapCheck window
   :width: 100%

   A snap opened in SnapCheck: the boards of the snap at the top, the files and the ratings on the
   left, the board to review in the middle.


Main concepts
=============

Snap
   A quality control document, saved in a ``.snpk`` file. It contains the boards to review, the
   ratings to fill in and free metadata (study, subject...). The figures are embedded in the file,
   which can be moved or shared as is.

Board
   A page of the snap: a set of elements displayed together, with instructions for the reviewer.

Element
   A graphical item of a board: an image, a text, a row of elements...

Rating
   A question to answer: a value to choose in a *rating scale* (for example *Bad*, *Good*,
   *Perfect*), and/or a comment. Each element indicates the ratings to fill in by looking at it.


Features
========

- Open several snaps at once, in tabs. An image can also be opened directly.
- Browse the files to find the snaps.
- Go through the boards with the list of the boards or the :kbd:`Tab` key, and zoom in the boards.
- Rate from the side panel, or with a right click on an element. Add a comment to each rating.
- See at a glance which ratings concern the current board.
- Save the snap (the modified snaps are marked with a ``*``), or save it under another name.
- Export the snap as a static website (HTML), to share the results.
- Create the snaps, read the ratings and export the snaps from your own python scripts, with the
  ``snapcheck`` package.


Getting started
===============

Install the application with `pixi <https://pixi.sh>`_ from the conda channel (forge) where it is
published:

.. code-block:: shell

   pixi global install -c <forge> -c https://prefix.dev/conda-forge snapclient

Then start it:

.. code-block:: shell

   snapcheck

Read the :doc:`user guide <user_guide>` to learn how to use it. To create your own snaps, see the
:doc:`developers documentation <developers/index>` and the :ref:`examples <general_examples>`.


.. toctree::
   :hidden:
   :maxdepth: 2

   user_guide
   developers/index
   auto_examples/index
   api/index
