# Dominion Local Business Directory — Daily City Builder

Runs on Render.com as a daily cron job at 6 AM UTC.
Builds 50 new city pages per day until all US cities and towns are covered.
Pushes directly to the dominionlocalbusinessdirectory-site GitHub repo.

## What it does
- Checks which cities already have pages
- Builds the next 50 unique city pages with full SEO schema
- Updates sitemap.xml with all URLs
- Pushes to GitHub → Netlify auto-deploys

## Deploy on Render
1. Create new Cron Job on Render
2. Connect this repo
3. Runtime: Python 3
4. Schedule: 0 6 * * * (6 AM UTC daily)
5. Start Command: python build_cities_daily.py
