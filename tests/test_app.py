def test_home_renders(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "What do you want to watch tonight?" in r.text


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
