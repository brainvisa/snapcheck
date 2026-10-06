.. _rest_api:

==================
REST API reference
==================

The routes of the :doc:`snapserve backend <snapserve>`, generated from its OpenAPI schema at each
build of this documentation. While the backend runs, the same reference can also be browsed at its
``/docs`` (to try the routes) and ``/redoc`` pages.

All the routes, except ``POST /session/``, require the ``Authorization: Bearer <token>`` header
(see :ref:`the authentication <snapserve>`).

.. openapi:: ../generated/openapi.json
   :group:
