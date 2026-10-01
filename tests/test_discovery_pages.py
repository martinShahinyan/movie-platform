def test_mood_page(client, movies):
    r = client.get("/mood/sad")
    assert r.status_code == 200
    assert "<h1" in r.text and "Sad movies" in r.text
    assert "Best Sad Movies to Watch Tonight | Moodreel" in r.text
    assert "Questions people ask" in r.text and "feeling sad?" in r.text
    assert "Interstellar" in r.text
    assert '<link rel="canonical" href="http://localhost:8000/mood/sad">' in r.text
    assert 'content="index,follow"' in r.text


def test_mood_page_2_has_no_duplicate_intro_and_own_canonical(client, movies):
    r = client.get("/mood/sad?page=2")
    assert r.status_code == 200
    assert "Questions people ask" not in r.text and "Page 2" in r.text
    assert 'href="http://localhost:8000/mood/sad?page=2"' in r.text
    assert client.get("/mood/sad?page=9").status_code == 404


def test_unknown_mood_and_genre_404(client, movies):
    assert client.get("/mood/nope").status_code == 404
    assert client.get("/genre/nope").status_code == 404


def test_empty_mood_page_is_noindex(client, movies):
    r = client.get("/mood/cozy")  # no fixture movie carries this tag
    assert r.status_code == 200 and 'content="noindex,follow"' in r.text


def test_genre_page(client, movies):
    r = client.get("/genre/sci-fi")
    assert r.status_code == 200 and "Sci-fi movies" in r.text or "Sci-Fi movies" in r.text
    assert "Interstellar" in r.text and "Filler 1" not in r.text


def test_year_pages(client, movies):
    r = client.get("/year/2014")
    assert r.status_code == 200 and "Movies from 2014" in r.text and "Interstellar" in r.text
    assert "/year/2020" in r.text  # other years are linked
    assert client.get("/year/1901").status_code == 404


def test_hubs(client, movies):
    assert "/mood/sad" in client.get("/moods").text
    assert "/genre/drama" in client.get("/genres").text


def test_single_filter_redirects_to_landing_page(client, movies):
    r = client.get("/movies?genre=drama", follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == "/genre/drama"
    assert client.get("/movies?mood=sad&page=2", follow_redirects=False).headers["location"] == "/mood/sad?page=2"
    assert client.get("/movies?year=2014", follow_redirects=False).headers["location"] == "/year/2014"
    assert client.get("/movies?genre=drama&mood=sad").status_code == 200  # combined: still a list


def test_home_has_finder_and_sections(client, movies):
    r = client.get("/")
    assert r.status_code == 200
    for needle in ('action="/find"', 'name="mood" value="sad"', "Find my movie", "Browse by mood",
                   "Movies for late nights", "Browse by genre", "Popular tonight"):
        assert needle in r.text
    assert '<option value="7" selected>' in r.text


def test_find_page_from_form_with_blank_fields(client, movies):
    r = client.get("/find?mood=sad&mood=atmospheric&genre=&runtime=&decade=&rating=&language=")
    assert r.status_code == 200 and "Interstellar" in r.text
    assert 'content="noindex,follow"' in r.text
    assert '<input type="checkbox" name="mood" value="sad" checked>' in r.text  # form stays filled


def test_find_summary_and_relaxed_note(client, movies):
    r = client.get("/find?mood=sad&genre=sci-fi&rating=9")
    assert r.status_code == 200 and "closest ones" in r.text and "Sci-Fi" in r.text


def test_find_ignores_garbage_params(client, movies):
    assert client.get("/find?rating=abc&runtime=zzz&decade=1x&mood=%3Cscript%3E").status_code == 200


def test_find_empty_result_message(client, movies):
    r = client.get("/find?mood=cozy&decade=2020")
    assert r.status_code == 200 and "Nothing matches" in r.text
