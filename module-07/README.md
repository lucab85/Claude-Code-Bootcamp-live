# Module 07 – Dashboard

**Track A: Flask + Jinja templates**

## Run

```bash
python3.12 app.py
```

Then open http://localhost:5001 in a browser at 1280×720.

## Layout

Matches `wireframe-sketch.png`:

- **Header** – "Dashboard" title left, "+ New Note" button right
- **Sidebar** – vertical nav: Overview, Notes, Tasks, Reports, Settings
- **KPI cards** – three bordered cards (Total Users · Active Projects · Days to Review)
- **Recent items** – bordered panel with five dot-leader rows
- **Footer** – version string

## Data

All data is hardcoded in `app.py` (no database, no auth).
