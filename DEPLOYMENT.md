# Production Deployment & SEO Guide - Moodreel

This guide covers deploying **Moodreel** to production and maximizing your SEO ranking.

---

## 1. Quick Production Deployment Options

### Option A: Render.com / Railway / Fly.io (Easiest & Free/Low Cost)
1. Push your repository to GitHub.
2. Log into [Render.com](https://render.com) or [Railway.app](https://railway.app).
3. Create a **Web Service** connected to your repository.
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4`
6. Set Environment Variables:
   - `APP_ENV` = `production`
   - `DATABASE_URL` = `postgresql://...` (or use internal SQLite if starting small)
   - `SECRET_KEY` = `<your-random-secret>`
   - `ADMIN_PASSWORD` = `<your-admin-password>`
   - `SITE_URL` = `https://yourdomain.com`
7. Click **Deploy**.

---

### Option B: VPS (Ubuntu + Docker Compose + Nginx + SSL)
1. SSH into your VPS:
   ```bash
   ssh root@YOUR_SERVER_IP
   ```
2. Clone your code:
   ```bash
   git clone https://github.com/your-username/movie-platform.git
   cd movie-platform
   ```
3. Edit `.env` or `docker-compose.yml` with your domain and passwords.
4. Run Docker Compose:
   ```bash
   docker-compose up -d --build
   ```
5. Seed initial reference data and starter movies inside the container:
   ```bash
   docker-compose exec web python -m scripts.seed
   ```
6. Set up Nginx & SSL (Let's Encrypt):
   ```bash
   sudo apt update && sudo apt install nginx certbot python3-certbot-nginx -y
   ```
7. Configure `/etc/nginx/sites-available/moodreel`:
   ```nginx
   server {
       server_name yourdomain.com www.yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
8. Enable site & Obtain SSL certificate:
   ```bash
   sudo ln -s /etc/nginx/sites-available/moodreel /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

---

## 2. SEO Complete Strategy Guide

SEO is a primary growth engine for Moodreel. Here is how it is structured and what steps to take after deployment:

### Built-in SEO Infrastructure (Already active in the codebase)
1. **Canonical URLs & Meta Tags**:
   - Dynamic canonical tags in `<head>` prevent duplicate content penalties.
   - Open Graph tags (`og:title`, `og:image`, `og:description`, `og:type`) generate rich previews on Telegram, Twitter/X, and Facebook.
2. **Dynamic Sitemap (`/sitemap.xml`)**:
   - Automatically generates XML sitemap covering all Mood landing pages (`/mood/*`), Genre landing pages (`/genre/*`), Year pages (`/year/*`), and Movie detail pages (`/movie/*`).
3. **Robots.txt (`/robots.txt`)**:
   - Instructs web crawlers to index all public pages while excluding internal API endpoints and `/admin`.
4. **Structured Data (Schema.org JSON-LD)**:
   - Movie detail pages output `Schema.org/Movie` JSON-LD with rating aggregates, release dates, and posters.
   - Mood landing pages output structured FAQ data for Google rich snippets.

---

### Step-by-Step SEO Launch Checklist

#### Step 1: Update `SITE_URL` in Production Environment
In your `.env` or container environment variables, set `SITE_URL` to your live domain:
```env
SITE_URL=https://yourdomain.com
```
*(This ensures all canonical links and sitemap URLs use `https://yourdomain.com` instead of `http://localhost:8000`).*

#### Step 2: Submit Sitemap to Google Search Console & Yandex Webmaster
1. Log into [Google Search Console](https://search.google.com/search-console).
2. Add your domain property (`https://yourdomain.com`).
3. Go to **Sitemaps** in the left menu.
4. Enter `https://yourdomain.com/sitemap.xml` and click **Submit**.
5. Repeat for [Yandex Webmaster](https://webmaster.yandex.ru) if targeting Russian-speaking audiences.

#### Step 3: Target High-Intent Search Keywords
Your platform naturally ranks for search terms like:
- *"movies to watch when feeling sad"* -> `/mood/sad`
- *"mind-bending sci-fi movies"* -> `/mood/mind-bending`
- *"romantic late night movies"* -> `/mood/romantic`
- *"best movies of 2024"* -> `/year/2024`

#### Step 4: Indexing Monitor
- Check Google Search Console **Page indexing** report after 3-5 days.
- Ensure all `/mood/`, `/genre/`, and `/movie/` URLs pass mobile usability and rich snippet validation tests.
