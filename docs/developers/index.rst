.. _developers:

=======================
Developer documentation
=======================

.. toctree::
   :hidden:
   :maxdepth: 2

   snapcheck
   snapserve
   rest_api
   frontend

SnapCheck is made of four parts:

======================================== ============================================================
Part                                     Role
======================================== ============================================================
:doc:`snapcheck <snapcheck>` (python)    The data model and the snap files: create, read, rate and
                                         export snaps. It does not depend on the GUI, use it in your
                                         scripts.
:doc:`snapserve <snapserve>` (python)    The backend: a REST API, built with
                                         `FastAPI <https://fastapi.tiangolo.com>`_ and the Lepton
                                         framework, which opens, edits and saves the snaps for the
                                         GUI.
:doc:`frontend <frontend>` (TypeScript)  The GUI: a `React <https://react.dev>`_ application calling
                                         the REST API.
``snapclient`` (python)                  The desktop application: a Qt window displaying the
                                         frontend, and the ``snapcheck`` command starting the
                                         backend and the window.
======================================== ============================================================

.. code-block:: text

   snapclient (Qt window)
     └─ frontend (React) ── REST API ──► snapserve (FastAPI, Lepton) ──► snapcheck ──► .snpk files

The snaps are created with python scripts using the :mod:`snapcheck` package, then reviewed in the
application.

- :doc:`snapcheck`: the python package, and the :ref:`examples <general_examples>`.
- :doc:`snapserve`: the backend, and the :doc:`REST API reference <rest_api>`.
- :doc:`frontend`: the GUI.
- :doc:`../api/index`: the reference of the python packages.


Development environment
=======================

SnapCheck is developed with the Lepton framework in the ``lepton-dev-env`` environment, which
contains the three projects (``lepton-common``, ``lepton`` and ``snapcheck``) and manages their
dependencies with `pixi <https://pixi.sh>`_. See its README to set it up, then:

.. code-block:: shell

   pixi shell                 # from lepton-dev-env
   cd snapcheck
   npm install
   npm run sass               # compile the SASS files of the frontend
   npm run build_api          # generate the API client of the frontend, see snapserve

The frontend uses the ``@lepton/core`` library, built in ``../lepton/dist`` (``npm install`` and
``npm run build`` in the lepton project).

Run the application from the sources with ``pixi run snapcheck`` (in the snapcheck directory): the
frontend is then served by the Vite development server, and reloaded when its code changes.


Tests and code quality
======================

.. code-block:: shell

   pytest tests                # tests of snapcheck and snapserve
   pixi run lint               # from lepton-dev-env: ruff (python) and Biome (TypeScript)
   pixi run format             # fix and format the code


Build this documentation
========================

.. code-block:: shell

   pixi run docs-snapcheck     # from lepton-dev-env, or "make html" in snapcheck/docs

The website is in ``docs/_build/html``. The build imports the python packages (to generate the API
reference and the REST API documentation) and runs the examples: use the ``lepton-dev-env``
environment. ``make html-noplot`` builds it without running the examples, ``make clean`` removes
the generated files.

The screenshots of the application (``docs/_static/screenshots``) are taken by
``docs/_scripts/make_screenshots.py``: run it after a change of the GUI (the frontend must be built
with ``npm run build``).


Build and publish the packages
==============================

Two conda packages are built with `rattler-build <https://rattler.build>`_ (``recipe/recipe.yaml``):
``snapcheck`` (the python package, without GUI) and ``snapclient`` (the application). They depend on
the ``lepton-common`` and ``lepton-app`` packages, published in the same forge.

.. code-block:: shell

   pixi run build-conda [FORGE]    # packages in ./output/noarch
   pixi run publish-conda FORGE    # build, then publish in the forge
   pixi run build-wheel FORGE      # wheel (pip / uv) in ./output/wheels

See ``BUILD.md`` in ``lepton-dev-env`` to build and publish all the projects at once.
