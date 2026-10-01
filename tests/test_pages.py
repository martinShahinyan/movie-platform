def test_movie_page(client, movies):
    r = client.get("/movie/interstellar")
    assert r.status_code == 200
    assert "<h1" in r.text and "Interstellar" in r.text
    assert "2h 49m" in r.text and "8.4" in r.text
    assert '<link rel="canonical" href="http://localhost:8000/movie/interstellar">' in r.text
    assert 'property="og:title"' in r.text and 'name="twitter:card"' in r.text
    assert 'loading="lazy"' in r.text or "fetchpriority" in r.text


def test_unknown_movie_gives_404_page(client, movies):
    r = client.get("/movie/does-not-exist")
    assert r.status_code == 404
    assert "Lost between movies?" in r.text


def test_movies_listing_pagination(client, movies):
    p1 = client.get("/movies")
    assert p1.status_code == 200 and 'rel="next"' in p1.text
    p2 = client.get("/movies?page=2")
    assert p2.status_code == 200 and 'rel="prev"' in p2.text
    assert client.get("/movies?page=99").status_code == 404


def test_movies_filters(client, movies):
    r = client.get("/movies?genre=sci-fi&mood=sad")  # combined filters stay a (noindex) list
    assert r.status_code == 200 and "Interstellar" in r.text and "Filler 1" not in r.text
    assert 'content="noindex,follow"' in r.text
    assert client.get("/movies?genre=nope").status_code == 404
    assert client.get("/movies?year=abc").status_code == 404


def test_search_page_and_escaping(client, movies):
    r = client.get("/search?q=interstellar")
    assert r.status_code == 200 and "Interstellar" in r.text
    assert 'content="noindex,follow"' in r.text
    evil = client.get("/search", params={"q": "<script>alert(1)</script>"})
    assert "<script>alert(1)</script>" not in evil.text
    assert "&lt;script&gt;" in evil.text
