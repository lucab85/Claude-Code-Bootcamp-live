"""Dashboard web app – Track A: Flask + Jinja."""
from flask import Flask, render_template

app = Flask(__name__)

KPI_DATA = [
    {"label": "Total Users", "value": "128"},
    {"label": "Active Projects", "value": "42"},
    {"label": "Days to Review", "value": "7d"},
]

RECENT_ITEMS = [
    {"name": "Q2 Planning Doc", "value": "2026-05-28"},
    {"name": "Bug #4412 Investigation", "value": "2026-05-27"},
    {"name": "Team Onboarding Notes", "value": "2026-05-26"},
    {"name": "API Design Review", "value": "2026-05-25"},
    {"name": "Sprint Retrospective", "value": "2026-05-24"},
]

NAV_LINKS = ["Overview", "Notes", "Tasks", "Reports", "Settings"]


@app.route("/")
def index() -> str:
    return render_template(
        "index.html",
        kpis=KPI_DATA,
        items=RECENT_ITEMS,
        nav_links=NAV_LINKS,
        active="Overview",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
