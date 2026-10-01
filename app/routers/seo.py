import xml.etree.ElementTree as ET

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.services import movie_service

router = APIRouter(include_in_schema=False)
settings = get_settings()


@router.get("/sitemap.xml")
def sitemap_xml(request: Request, db: Session = Depends(get_db)):
    base_url = str(request.base_url).rstrip("/")
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    urls = [
        ("/", "1.0", "daily"),
        ("/movies", "0.9", "daily"),
        ("/moods", "0.8", "weekly"),
        ("/genres", "0.8", "weekly"),
    ]

    # Mood pages
    for m in movie_service.all_moods(db):
        urls.append((f"/mood/{m.slug}", "0.8", "weekly"))

    # Genre pages
    for g in movie_service.all_genres(db):
        urls.append((f"/genre/{g.slug}", "0.8", "weekly"))

    # Year pages
    for yr, _ in movie_service.available_years(db):
        urls.append((f"/year/{yr}", "0.7", "monthly"))

    # Movie pages
    pg = movie_service.list_movies(db, page=1, per_page=5000)
    for movie in pg.items:
        urls.append((f"/movie/{movie.slug}", "0.9", "weekly"))

    for loc, priority, changefreq in urls:
        url_elem = ET.SubElement(urlset, "url")
        loc_elem = ET.SubElement(url_elem, "loc")
        loc_elem.text = f"{base_url}{loc}"

        freq_elem = ET.SubElement(url_elem, "changefreq")
        freq_elem.text = changefreq

        prio_elem = ET.SubElement(url_elem, "priority")
        prio_elem.text = priority

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(urlset, encoding="utf-8").decode("utf-8")
    return Response(content=xml_content, media_type="application/xml")


@router.get("/robots.txt")
def robots_txt(request: Request):
    base_url = str(request.base_url).rstrip("/")
    content = f"""User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin
Disallow: /search

Sitemap: {base_url}/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")
