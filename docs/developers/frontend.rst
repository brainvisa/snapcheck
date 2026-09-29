.. _frontend:

============
The frontend
============

The GUI is a `React <https://react.dev>`_ application written in TypeScript, built with
`Vite <https://vite.dev>`_. It displays the snaps opened in the :doc:`backend <snapserve>` and
sends the modifications to it through the REST API.

It is built on the ``@lepton/core`` library of the Lepton framework, which provides the bootstrap
of the application, the session (opened snaps, current snap, settings of each snap), the HTTP
client with the authentication and the modal windows.


Organization of the code
========================

========================================= ===========================================================
Directory                                 Content
========================================= ===========================================================
``snapcheck-front/src/main.tsx``          Entry point: configures the API client and starts the
                                          application.
``snapcheck-front/src/Snapcheck.tsx``     The application: top bar, side panel and board area.
``snapcheck-front/src/lepton/pages``      The main page (boards list and board view, side panel,
                                          top bar) and the dialogs (HTML export...).
``snapcheck-front/src/lepton/components`` The components: display of the elements (``elements``),
                                          file browser (``files``), rating input (``specials``) and
                                          generic components (``lib``: menus, tabs, layouts...).
``snapcheck-front/src/contexts``          State of the interface (ex: side panel shown or hidden).
``src/api``                               Access to the API: the generated client (``generated``)
                                          and the hooks using it (``snap.ts``: ``useSnap``,
                                          ``usePatchField``, ``useSaveSnap``...).
``snapcheck-front/public``                Static files (icon, ``qwebchannel.js`` for the Qt client).
========================================= ===========================================================

The state of the snaps comes from the backend: the hooks of ``src/api/snap.ts`` read it with
`TanStack Query <https://tanstack.com/query>`_, which caches the answers of the API, and send the
modifications (ex: ``usePatchField`` to set the value of a rating). The API client is generated
from the OpenAPI schema of the backend: see :ref:`the API client <snapserve>`.

The styles are written in SASS (``.sass`` files next to the components) and compiled to CSS with
``npm run sass``.


Commands
========

.. code-block:: shell

   npm run dev          # development server (started by pixi run snapcheck)
   npm run build_api    # generate the API client
   npm run build        # compile the SASS files, check the types, build in dist/
   npm run typecheck    # check the types
   npm run lint         # check the code with Biome (npm run format to fix it)

In the installed application, the built frontend (``dist/``) is embedded in the ``snapclient``
package and served by the Qt client.
