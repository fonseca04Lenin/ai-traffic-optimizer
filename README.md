# Dispatch — AI Route Optimizer

A route planning and job management tool built for small field-service businesses. Think delivery crews, cleaning companies, lawn care, repair techs — anyone running a team of drivers who needs to stop wasting time on inefficient routes.

You add jobs, assign drivers, and let the app figure out the best order to visit every stop. It shows you the route on a live map with real road geometry, estimates total drive time, and tells you how much fuel you saved compared to just going in whatever order the jobs were entered.

---

## What it does

**Job management** — Create jobs with customer name, address, service type (delivery, pickup, cleaning, lawn care, repair, inspection), priority level, and optional time windows. Jobs can be filtered by status, priority, or driver on the list view. Status updates (pending → in progress → completed) can be done inline.

**Driver management** — Add drivers with vehicle type (van, truck, car, motorcycle, bike), max daily mileage, and availability. The dashboard shows each driver's pending job count and online/off-duty status at a glance.

**Route optimization** — Select any group of pending jobs, optionally set a depot starting point, and the engine runs a priority-weighted nearest-neighbor algorithm to find a good visit order. High-priority stops are treated as if they're "closer" so they naturally surface to the front without a hard sort overriding geography. The result is saved as a named route with total mileage, estimated duration, and fuel savings percentage.

**Interactive map** — Route detail pages render stops on a Leaflet map with CartoDB dark tiles. The app calls the OSRM public routing API to draw road-following polylines between stops. If that API is down or returns no data, it falls back to straight dashed lines and shows a warning on the map so you know what you're looking at.

**Dashboard** — Overview of total jobs, high-priority unassigned work, active drivers, routes run, in-progress jobs, and all-time completions. Recent jobs and routes are surfaced directly on the home page.

**Admin panel** — Full Django admin at `/admin/` for direct database access when needed.

---

## Stack

- Python / Django 6.0
- SQLite (dev database, file-based, zero config)
- NetworkX — graph construction for the route optimizer
- Nominatim / OpenStreetMap — free geocoding, no API key needed
- OSRM public server — free road-following route geometry, no API key needed
- Leaflet.js 1.9 with CartoDB Dark tiles
- Pure CSS design system (no Bootstrap, no Tailwind, no component library)

---

## Setup

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd ai-traffic-optimizer

# 2. Install dependencies
pip install django networkx requests

# 3. Run migrations
python manage.py migrate

# 4. (Optional) Load demo data — 5 drivers, 22 jobs across Miami and Omaha
python manage.py seed_demo

# 5. Create a superuser if you want admin access
python manage.py createsuperuser

# 6. Start the server
python manage.py runserver
```

Then open `http://127.0.0.1:8000`.

To wipe and reload the demo data at any time:
```bash
python manage.py seed_demo --reset
```

---

## What still needs to be built

This is a functional prototype. It covers the core loop but there's a real gap between "works in a demo" and "ready to hand to an actual business."

**Authentication** — Right now there's no login. Anyone who can reach the URL can read and edit everything. Django's built-in auth system is already a dependency, it just hasn't been wired to views yet. At minimum, wrap all views with `@login_required`.

**Real user accounts and multi-tenancy** — A cleaning company and a delivery company shouldn't share the same job list. Routes, drivers, and jobs need to be scoped to an organization or user account.

**Driver mobile view** — Drivers need a way to see their assigned route for the day on a phone without logging into the full admin UI. A simple driver-facing page (just the stop list and a map) would be enough to start.

**Time window enforcement** — The `time_window_start` and `time_window_end` fields exist on Job and display on route detail pages, but the optimizer completely ignores them. A real TSP solver or constraint-based approach (OR-Tools, Google's VRPTW solver) would need to replace the current nearest-neighbor heuristic to respect delivery windows.

**Live traffic data** — The route engine uses straight-line haversine distances and a fixed 25 mph average speed estimate. Integrating a real routing API (Google Maps, HERE, Mapbox) would give actual drive times based on current conditions.

**Recurring jobs** — Field service businesses often have the same stops every week. There's no concept of a job template or schedule right now, so recurring work has to be re-entered manually.

**Notifications** — No emails, no SMS, no push. Drivers don't get notified when they're assigned a route. Customers don't get an ETA. Something like Twilio for SMS or SendGrid for email would cover the basics.

**Reporting and analytics** — The dashboard shows counts but nothing over time. Useful additions: jobs completed per week, average route efficiency by driver, fuel savings trend, on-time delivery rate once time windows are enforced.

**Production deployment hardening** — `DEBUG = True` is still on, `SECRET_KEY` is hardcoded in settings, and SQLite isn't appropriate for anything beyond one machine. For a real deployment you'd swap in PostgreSQL, move secrets to environment variables, add `ALLOWED_HOSTS`, run behind gunicorn, and set up static file serving (whitenoise or S3).

**Geocoding reliability** — Nominatim has rate limits and occasionally returns wrong coordinates for ambiguous addresses. A fallback to a paid geocoder (Geocodio is cheap and US-focused) would make address entry more reliable for production use.
