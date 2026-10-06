.. _snapserve:

=====================
The snapserve backend
=====================

:mod:`snapserve` is the backend of the application: a REST API which opens, edits and saves the
snaps for the GUI. It is built with `FastAPI <https://fastapi.tiangolo.com>`_ and the 
`Lepton <https://github.com/cati-neuroimaging/lepton>` framework, which provides the generic parts 
of a document editor: the sessions, the authentication, the opened objects (the snaps) with their 
modification history, the settings...

The application is defined in :mod:`snapserve.app`: a :class:`lepton.app.LeptonApp` managing
:class:`~snapcheck.snap.snap.Snap` objects, to which snapserve adds its own routes:

- :class:`~snapserve.snap.controller.SnapRouter`: the images of the snaps and their exports, added
  to the Lepton ``/objects`` routes;
- :mod:`snapserve.files.controller`: ``/files``, to browse the files of the server;
- :mod:`snapserve.content.controller`: ``/content``, the static pages of the GUI (like *About*).


Run the backend
===============

The ``snapcheck`` command starts the backend with the GUI. To start the backend alone:

.. code-block:: shell

   python -m snapserve [--host 127.0.0.1] [--port 8050] [--secret SECRET] [--session ID]

``--secret`` (or ``$SNAP_SECRET``) is the key signing the authentication tokens; a random key is
used by default. ``--session`` creates a first session with this id.

While it runs, FastAPI serves an interactive documentation of the API at
http://127.0.0.1:8050/docs (Swagger UI, to try the routes) and http://127.0.0.1:8050/redoc.


Authentication
==============

All the routes, except the creation of a session, require a JWT token in the ``Authorization``
header:

.. code-block:: text

   Authorization: Bearer <token>

The token is signed with the secret of the backend and contains the id of a session: the snaps
opened by a session are isolated from the other sessions.

``POST /session/`` creates a session and returns its token. If the ``LAUNCH_SECRET`` environment
variable is set, the request must give it in the ``launch_secret`` parameter. The frontend creates
its session this way when it starts.

The ``snapcheck`` command (:mod:`snapclient.launcher`) also prepares a session: it generates the
secret, starts the backend with a first session (``--secret`` and ``--session``) and gives the
token of this session to the Qt client, which passes it to the frontend (``getJWT`` slot of
:class:`snapclient.__main__.Bridge`).


CORS and ports
==============

The frontend and the backend are served on different ports, so the backend only accepts the
requests of the allowed origins (CORS). By default, the frontend ports 3000 and 5173 of
``127.0.0.1`` and ``localhost`` are allowed. Add other origins, comma separated, with the
``SNAP_ALLOW_ORIGINS`` environment variable:

.. code-block:: shell

   SNAP_ALLOW_ORIGINS=http://127.0.0.1:3050 python -m snapserve --port 8060

The frontend reads the URL of the backend from the ``api`` parameter of its URL (ex:
``http://127.0.0.1:3050/?api=http://127.0.0.1:8060``), else from the ``VITE_API_URL`` variable of
the Vite server, else it uses ``http://localhost:8050``. The ``snapcheck`` command sets all of this
from its ``--host``, ``--backend-port`` and ``--frontend-port`` options.


The routes
==========

============== ====================================================================================
Routes         Role
============== ====================================================================================
``/session``   Create, get and close a session (Lepton).
``/objects``   Open, create, save and close the snaps, and edit them (``PATCH .../field``) (Lepton),
               plus the images and the exports of the snaps (snapserve).
``/settings``  Read the settings of the application (Lepton).
``/files``     Browse the directories of the server.
``/content``   Get the static pages of the GUI.
============== ====================================================================================

The complete reference, generated from the code, is in :doc:`rest_api`.

The descriptions of the routes are the docstrings of their python functions, and the descriptions
of the fields are the docstrings of the attributes of the pydantic models: document them there.


The API client of the frontend
==============================

The frontend calls the API through a typed client generated from its OpenAPI schema, with
`Hey API <https://heyapi.dev>`_. After each change of the API (routes, parameters or models),
regenerate it:

.. code-block:: shell

   npm run build_api

It exports the OpenAPI schema in ``openapi.json`` (``scripts/export_openapi.py``), then generates the
client in ``src/api/generated/`` (TypeScript types, functions and TanStack Query options). The
generated files are not versioned.
