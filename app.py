"""Work2Win Technologies Flask application."""

from __future__ import annotations

import logging
import os
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen
import json

from flask import Flask, jsonify, render_template, request

try:
    import psycopg
except ImportError:  # Allows frontend-only setup before dependencies are installed.
    psycopg = None

COURSES = [
    {"id": 1, "name": "Data Analyst", "slug": "data-analyst", "description": "Build practical skills for working with, understanding and presenting data.", "category": "Data"},
    {"id": 2, "name": "Data Science", "slug": "data-science", "description": "Explore data-driven problem solving with modern analytical techniques.", "category": "Data"},
    {"id": 3, "name": "Excel & Power BI", "slug": "excel-power-bi", "description": "Turn everyday data into clear reports, dashboards and insights.", "category": "Analytics"},
    {"id": 4, "name": "Python", "slug": "python", "description": "Learn a versatile programming language through hands-on practice.", "category": "Programming"},
    {"id": 5, "name": "MySQL", "slug": "mysql", "description": "Understand relational databases and write useful SQL queries.", "category": "Database"},
    {"id": 6, "name": "UI / HTML / CSS", "slug": "ui-html-css", "description": "Create accessible, responsive interfaces for the web.", "category": "Web"},
    {"id": 7, "name": "PostgreSQL", "slug": "postgresql", "description": "Work confidently with a powerful open-source database system.", "category": "Database"},
    {"id": 8, "name": "JavaScript", "slug": "javascript", "description": "Add interaction and modern browser behaviour to web projects.", "category": "Web"},
    {"id": 9, "name": "ReactJS", "slug": "reactjs", "description": "Build component-based user interfaces for modern web applications.", "category": "Web"},
    {"id": 10, "name": "Django Framework", "slug": "django-framework", "description": "Develop structured, maintainable web applications with Python.", "category": "Backend"},
    {"id": 11, "name": "Python Full Stack", "slug": "python-full-stack", "description": "Connect frontend, backend and database skills in one learning path.", "category": "Full Stack"},
]
COURSE_NAMES = {course["name"] for course in COURSES}
for _course in COURSES:
    # These fields match the planned PostgreSQL course model while content remains
    # lightweight configuration in version one.
    _course.update(active=True, created_at=None, updated_at=None)
PHONE_RE = re.compile(r"^[+()\-\s0-9]{7,25}$")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def load_local_env() -> None:
    """Load simple KEY=VALUE pairs from a local .env without overriding real env vars."""
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.isfile(env_file):
        return
    with open(env_file, encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_local_env()


def validate_enquiry(data: Any) -> tuple[dict[str, str], dict[str, str]]:
    """Normalize an enquiry and return field errors without trusting the client."""
    if not isinstance(data, dict):
        return {}, {"form": "Please send a valid enquiry."}
    clean = {key: str(data.get(key, "")).strip() for key in ("name", "whatsapp", "email", "course", "message")}
    errors: dict[str, str] = {}
    if not 2 <= len(clean["name"]) <= 100:
        errors["name"] = "Enter a name between 2 and 100 characters."
    if not PHONE_RE.fullmatch(clean["whatsapp"]):
        errors["whatsapp"] = "Enter a valid WhatsApp number."
    if clean["email"] and (len(clean["email"]) > 254 or not EMAIL_RE.fullmatch(clean["email"])):
        errors["email"] = "Enter a valid email address."
    if clean["course"] not in COURSE_NAMES:
        errors["course"] = "Please select a course."
    if len(clean["message"]) > 1000:
        errors["message"] = "Message must be 1,000 characters or fewer."
    return clean, errors


def save_enquiry(enquiry: dict[str, str], database_url: str) -> None:
    if database_url.startswith("sqlite:///"):
        database_path = database_url.removeprefix("sqlite:///")
        with sqlite3.connect(database_path) as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS enquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
                whatsapp TEXT NOT NULL, email TEXT NOT NULL, course TEXT NOT NULL,
                message TEXT, created_at TEXT NOT NULL)"""
            )
            connection.execute(
                """INSERT INTO enquiries (name, whatsapp, email, course, message, created_at)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (*enquiry.values(), datetime.now(timezone.utc).isoformat()),
            )
        return
    if not database_url or psycopg is None:
        raise RuntimeError("Database is not configured")
    query = """INSERT INTO enquiries (name, whatsapp, email, course, message, created_at)
               VALUES (%s, %s, %s, %s, %s, %s)"""
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (*enquiry.values(), datetime.now(timezone.utc)))


def send_email(enquiry: dict[str, str], config: dict[str, Any]) -> bool:
    """Send a best-effort Resend notification; storage must already have completed."""
    api_key, recipient, sender = (config.get("RESEND_API_KEY"), config.get("ADMIN_EMAIL"), config.get("FROM_EMAIL"))
    if not all((api_key, recipient, sender)):
        return False
    payload = json.dumps({
        "from": sender, "to": [recipient], "subject": f"New Work2Win enquiry: {enquiry['course']}",
        "text": "\n".join(f"{label}: {enquiry[key]}" for label, key in (("Name", "name"), ("WhatsApp", "whatsapp"), ("Course", "course"), ("Message", "message"))),
    }).encode()
    req = Request("https://api.resend.com/emails", data=payload, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=8) as response:
            return 200 <= response.status < 300
    except (URLError, OSError) as error:
        logging.getLogger(__name__).warning("Resend notification failed: %s", error)
        return False


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    database_url = os.getenv("DATABASE_URL", "")
    # Never try to resolve the instructional placeholder as a real hostname.
    if not database_url or "YOUR_SUPABASE_CONNECTION_STRING" in database_url:
        database_url = "sqlite:///work2win.db"
    app.config.from_mapping(
        DATABASE_URL=database_url, ADMIN_EMAIL=os.getenv("ADMIN_EMAIL", "work2wintechnologies@gmail.com"),
        RESEND_API_KEY=os.getenv("RESEND_API_KEY", ""), FROM_EMAIL=os.getenv("FROM_EMAIL", ""), MAX_CONTENT_LENGTH=16 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def home() -> str:
        return render_template("index.html", courses=COURSES)

    @app.post("/api/enquiry")
    def enquiry() -> tuple[Any, int]:
        clean, errors = validate_enquiry(request.get_json(silent=True))
        if errors:
            return jsonify(success=False, message="Please correct the highlighted fields.", errors=errors), 400
        try:
            saver = app.config.get("ENQUIRY_SAVER", save_enquiry)
            saver(clean, app.config["DATABASE_URL"])
        except Exception:
            app.logger.exception("Unable to save enquiry")
            return jsonify(success=False, message="Unable to send your enquiry right now. Please try again or contact us through WhatsApp."), 500
        emailed = send_email(clean, app.config)
        message = "Thank you! Your enquiry was received."
        if app.config.get("RESEND_API_KEY") and not emailed:
            message += " Our team will still be in touch shortly."
        return jsonify(success=True, message=message), 201

    @app.errorhandler(413)
    def request_too_large(_: Any) -> tuple[Any, int]:
        return jsonify(success=False, message="Your request is too large."), 413

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
