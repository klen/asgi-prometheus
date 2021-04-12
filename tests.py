from asgi_tools.tests import ASGITestClient
from asgi_tools.app import App


async def test_base():
    from asgi_prometheus import PrometheusMiddleware

    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": 200})
        await send({"type": "http.response.body", "body": b"OK", "more_body": False})

    app = PrometheusMiddleware(app, metrics_url='/metrics')
    client = ASGITestClient(app)

    res = await client.get('/')
    assert res.status_code == 200
    assert await res.text() == 'OK'

    res = await client.get('/metrics')
    assert res.status_code == 200
    text = await res.text()
    assert text
    assert 'requests_count_total' in text
    assert 'requests_time' in text


async def test_group_path():
    from asgi_prometheus import PrometheusMiddleware

    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": 200})
        await send({"type": "http.response.body", "body": b"OK", "more_body": False})

    app = PrometheusMiddleware(app, group_paths={'/api', '/api/v1/users'})
    client = ASGITestClient(app)

    res = await client.get('/')
    assert res.status_code == 200
    assert await res.text() == 'OK'

    res = await client.get('/api/v1/users')
    assert res.status_code == 200

    res = await client.get('/api/v1/messages')
    assert res.status_code == 200

    res = await client.get('/unknown')
    assert res.status_code == 200

    res = await client.get('/prometheus')
    assert res.status_code == 200
    text = await res.text()
    assert 'requests_count_total{method="GET",path="/api*"}' in text
    assert 'requests_count_total{method="GET",path="/api/v1/users*"}' in text


async def test_asgi_tools_internal():
    from asgi_prometheus import PrometheusMiddleware

    app = App()
    app.middleware(PrometheusMiddleware)
    client = ASGITestClient(app)

    res = await client.get('/')
    assert res.status_code == 404

    res = await client.get('/prometheus')
    assert res.status_code == 200
    text = await res.text()
    assert text
    assert 'requests_count_total' in text


async def test_asgi_tools_external():
    from asgi_prometheus import PrometheusMiddleware

    app = App()
    app = PrometheusMiddleware(app)
    client = ASGITestClient(app)

    res = await client.get('/')
    assert res.status_code == 404

    res = await client.get('/prometheus')
    assert res.status_code == 200
    text = await res.text()
    assert text
    assert 'requests_count_total' in text
