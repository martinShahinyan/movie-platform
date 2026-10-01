"""Shared Jinja2 environment, filters and SEO helper."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.finder_config import FINDER
from app.services.tmdb_service import image_url

BASE_DIR = Path(__file__).resolve().parent
SITE_NAME = "Moodreel"
TAGLINE = "Find something worth watching."

templates = Jinja2Templates(directory=BASE_DIR / "templates")


def img(path: str | None, size: str = "w342") -> str:
    return image_url(path, size) or ""


def srcset(path: str | None, widths: tuple[int, ...] = (185, 342, 500)) -> str:
    if not path:
        return ""
    if path.startswith("http://") or path.startswith("https://") or path.startswith("/static/"):
        return f"{path} 1x"
    return ", ".join(f"{image_url(path, f'w{w}')} {w}w" for w in widths)


def runtime_fmt(minutes: int | None) -> str:
    if not minutes:
        return ""
    h, m = divmod(minutes, 60)
    return f"{h}h {m:02d}m" if h and m else (f"{h}h" if h else f"{m}m")


def rating_fmt(value: float | None) -> str:
    return f"{value:.1f}" if value else ""


templates.env.filters.update(img=img, srcset=srcset, runtime=runtime_fmt, rating=rating_fmt)
templates.env.globals.update(site_name=SITE_NAME, tagline=TAGLINE, FINDER=FINDER)


def make_seo(
    request: Request,
    *,
    title: str,
    description: str,
    image: str | None = None,
    og_type: str = "website",
    noindex: bool = False,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Per-page SEO data consumed by base.html (canonical, Open Graph, Twitter, robots)."""
    base = get_settings().site_url.rstrip("/")
    query = urlencode({k: v for k, v in (params or {}).items() if v not in (None, "", 1)})
    canonical = f"{base}{request.url.path}" + (f"?{query}" if query else "")
    return {
        "title": title,
        "description": description[:200],
        "canonical": canonical,
        "image": image,
        "og_type": og_type,
        "robots": "noindex,follow" if noindex else "index,follow",
    }


def page_url(request: Request, n: int) -> str:
    """Current URL with ?page=n, keeping every other (possibly repeated) query parameter."""
    items = [(k, v) for k, v in request.query_params.multi_items() if k != "page"]
    if n > 1:
        items.append(("page", str(n)))
    return request.url.path + (f"?{urlencode(items)}" if items else "")
