ASGI-Prometheus
###############

.. _description:

**asgi-prometheus** -- Support Prometheus metrics for ASGI applications (Asyncio_ / Trio_, / Curio_)

.. _badges:

.. image:: https://github.com/klen/asgi-prometheus/workflows/tests/badge.svg
    :target: https://github.com/klen/asgi-prometheus/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/asgi-prometheus
    :target: https://pypi.org/project/asgi-prometheus/
    :alt: PYPI Version

.. image:: https://img.shields.io/pypi/pyversions/asgi-prometheus
    :target: https://pypi.org/project/asgi-prometheus/
    :alt: Python Versions

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python >= 3.7

.. _installation:

Installation
=============

**asgi-prometheus** should be installed using pip: ::

    pip install asgi-prometheus

Usage
=====

Common ASGI applications:

.. code:: python

    from asgi_prometheus import PrometheusMiddleware


    async def my_app(scope, receive, send):
        """Read session and get the current user data from it or from request query."""
        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": b"Hello World!"})

    app = PrometheusMiddleware(my_app, metrics_url="/metrics", group_paths=['/'])

    # http GET / -> OK
    # http GET /metrics -> [Prometheus metrics]


As `ASGI-Tools`_ Internal middleware

.. code:: python

    from asgi_tools import App
    from asgi_prometheus import PrometheusMiddleware

    app = App()
    app.middleware(PrometheusMiddleware.setup(group_paths=['/views', '/api']))

    @app.route('/')
    async def index(request):
        return 'Hello World!'

    # http GET / -> OK
    # http GET /metrics -> [Prometheus metrics]


Options
========

.. code:: python

   from asgi_sessions import PrometheusMiddleware

   app = PrometheusMiddleware(

        # Your ASGI application
        app,

        # Metrics URL for Prometheus
        metrics_url='/prometheus',

        # List of path's prefixes to group. A path which starts from the prefix will be grouped.
        # For example: group_paths=['/api/users'], "/api/users/1", "/api/users/2" will be grouped into "/api/users*"
        group_paths=[],

   )

.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/asgi-prometheus/issues

.. _contributing:

Contributing
============

Development of the project happens at: https://github.com/klen/asgi-prometheus

.. _license:

License
========

Licensed under a `MIT license`_.


.. _links:

.. _MIT license: http://opensource.org/licenses/MIT
.. _Asyncio: https://docs.python.org/3/library/asyncio.html
.. _klen: https://github.com/klen
.. _Trio: https://trio.readthedocs.io/en/stable/
.. _Curio: https://curio.readthedocs.io/en/latest/
.. _ASGI-Tools: https://github.com/klen/asgi-tools

