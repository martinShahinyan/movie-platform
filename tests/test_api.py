def test_api_list_and_filter(client, movies):
    data = client.get("/api/movies").json()
    assert data["total"] == 25 and len(data["items"]) == 20 and data["pages"] == 2
    assert data["items"][0]["slug"] == "interstellar"
    sf = client.get("/api/movies", params={"genre": "sci-fi"}).json()
    assert sf["total"] == 1


def test_api_movie_detail(client, movies):
    d = client.get("/api/movies/interstellar").json()
    assert d["title"] == "Interstellar" and d["runtime"] == 169
    assert d["poster_url"].endswith("/w342/p.jpg") and d["backdrop_url"].endswith("/w1280/b.jpg")
    r = client.get("/api/movies/nope")
    assert r.status_code == 404 and r.json()["detail"] == "Movie not found"


def test_api_validation_stays_json(client, movies):
    assert client.get("/api/movies?page=0").status_code == 422


def test_api_search(client, movies):
    hits = client.get("/api/search", params={"q": "inter"}).json()
    assert [h["slug"] for h in hits] == ["interstellar"]
    assert client.get("/api/search", params={"q": "i"}).json() == []
    assert client.get("/api/search", params={"q": "x" * 101}).status_code == 422
