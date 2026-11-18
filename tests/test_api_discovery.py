def test_api_recommendations(client, movies):
    d = client.get("/api/recommendations", params={"mood": ["sad", "atmospheric"], "genre": "sci-fi"}).json()
    assert d["items"][0]["slug"] == "interstellar"
    assert d["items"][0]["score"] == 5 + 5 + 3 
    assert d["total"] == 25 and d["relaxed"] is False


def test_api_recommendations_filters_and_blank_values(client, movies):
    d = client.get("/api/recommendations?mood=sad&rating=&decade=2020&runtime=").json()
    assert d["total"] == 24 and d["relaxed"] is False 


def test_api_runtime_filter_excludes_unknown_runtime_then_relaxes(client, movies):
    d = client.get("/api/recommendations?mood=sad&runtime=lt120").json()
    assert d["relaxed"] is True and d["total"] == 25


def test_api_moods_and_genres(client, movies):
    moods = {m["slug"]: m["movie_count"] for m in client.get("/api/moods").json()}
    assert len(moods) == 16 and moods["sad"] == 25 and moods["cozy"] == 0
    genres = {g["slug"]: g["movie_count"] for g in client.get("/api/genres").json()}
    assert len(genres) == 13 and genres["drama"] == 25 and genres["sci-fi"] == 1

def test_api_recommendations_page_validation(client, movies):
    assert client.get("/api/recommendations?page=0").status_code == 422