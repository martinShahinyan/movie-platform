"""Import movies from TMDB into PostgreSQL.

Examples:
  python -m scripts.import_movies --popular 5          # 5 pages (~100 movies)
  python -m scripts.import_movies --top-rated 5
  python -m scripts.import_movies --search "interstellar"
  python -m scripts.import_movies --tmdb-id 157336
"""
import argparse
import logging

from app.database import SessionLocal
from app.services.tmdb_service import TmdbError, TmdbService
from scripts.seed import seed_reference_data

log = logging.getLogger("import_movies")


def import_ids(tmdb: TmdbService, db, ids: list[int]) -> tuple[int, int]:
    ok = failed = 0
    for tmdb_id in dict.fromkeys(ids):  # de-duplicate, keep order
        try:
            tmdb.import_movie(db, tmdb_id)
            ok += 1
        except TmdbError as exc:
            db.rollback()
            failed += 1
            log.warning("skip %s: %s", tmdb_id, exc)
    return ok, failed


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--popular", type=int, metavar="PAGES")
    p.add_argument("--top-rated", type=int, metavar="PAGES")
    p.add_argument("--search", metavar="QUERY")
    p.add_argument("--tmdb-id", type=int)
    args = p.parse_args()
    if not any([args.popular, args.top_rated, args.search, args.tmdb_id]):
        p.error("choose at least one source")

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        tmdb = TmdbService()
    except TmdbError as exc:
        raise SystemExit(f"Error: {exc}")
    ids: list[int] = []
    try:
        for page in range(1, (args.popular or 0) + 1):
            ids += [m["id"] for m in tmdb.get_popular_movies(page)]
        for page in range(1, (args.top_rated or 0) + 1):
            ids += [m["id"] for m in tmdb.get_top_rated_movies(page)]
        if args.search:
            ids += [m["id"] for m in tmdb.search_movies(args.search)]
        if args.tmdb_id:
            ids.append(args.tmdb_id)

        with SessionLocal() as db:
            seed_reference_data(db)  # genres/moods must exist before linking
            ok, failed = import_ids(tmdb, db, ids)
        print(f"Done: {ok} imported/updated, {failed} failed.")
    except TmdbError as exc:
        raise SystemExit(f"Error: {exc}")
    finally:
        tmdb.close()


if __name__ == "__main__":
    main()
