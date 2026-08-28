"""Work2Win Technologies Flask application."""

from __future__ import annotations

import logging
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4
from urllib.error import URLError
from urllib.request import Request, urlopen
import json

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

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
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_ANNOUNCEMENT = {"title": "", "start_date": "", "timings": "", "details": "", "poster": "", "whatsapp_group_link": ""}


def read_json_file(path: Path, default: Any) -> Any:
    """Read lightweight local data; a missing file simply means no records yet."""
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json_file(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    temporary.replace(path)


def load_announcements(path: Path) -> list[dict[str, str]]:
    """Load posts, including a one-time conversion of the earlier single-post format."""
    raw = read_json_file(path, [])
    if isinstance(raw, dict):
        raw = [{"id": "legacy-post", "created_at": "", **raw}] if raw.get("title") or raw.get("poster") else []
    if not isinstance(raw, list):
        return []
    posts = [post for post in raw if isinstance(post, dict)]
    return sorted(posts, key=lambda post: post.get("created_at", ""), reverse=True)


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
        RESEND_API_KEY=os.getenv("RESEND_API_KEY", ""), FROM_EMAIL=os.getenv("FROM_EMAIL", ""),
        MAX_CONTENT_LENGTH=50 * 1024 * 1024, SECRET_KEY=os.getenv("SECRET_KEY", "change-this-secret-key"),
        ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD", "change-this-password"),
        ANNOUNCEMENT_FILE=BASE_DIR / "data" / "announcement.json",
        REGISTRATIONS_FILE=BASE_DIR / "data" / "course_registrations.json",
        REVIEWS_FILE=BASE_DIR / "data" / "student_reviews.json",
        UPLOAD_FOLDER=BASE_DIR / "static" / "uploads",
    )
    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def home() -> str:
        posts = load_announcements(app.config["ANNOUNCEMENT_FILE"])
        return render_template("index.html", courses=COURSES, announcement=posts[0] if posts else DEFAULT_ANNOUNCEMENT.copy())

    @app.get("/announcements")
    def announcements() -> str:
        return render_template("announcements.html", announcements=load_announcements(app.config["ANNOUNCEMENT_FILE"]))

    @app.get("/student-reviews")
    def student_reviews() -> str:
        reviews = read_json_file(app.config["REVIEWS_FILE"], [])
        reviews = sorted((review for review in reviews if isinstance(review, dict)), key=lambda review: review.get("created_at", ""), reverse=True)
        return render_template("student_reviews.html", reviews=reviews)

    @app.post("/api/course-registration")
    def course_registration() -> tuple[Any, int]:
        data = request.get_json(silent=True) or {}
        clean = {key: str(data.get(key, "")).strip() for key in ("name", "phone", "email", "message")}
        errors: dict[str, str] = {}
        if not 2 <= len(clean["name"]) <= 100:
            errors["name"] = "Enter your full name."
        if not PHONE_RE.fullmatch(clean["phone"]):
            errors["phone"] = "Enter a valid phone number."
        if clean["email"] and (len(clean["email"]) > 254 or not EMAIL_RE.fullmatch(clean["email"])):
            errors["email"] = "Enter a valid email address."
        if len(clean["message"]) > 1000:
            errors["message"] = "Message must be 1,000 characters or fewer."
        if errors:
            return jsonify(success=False, message="Please correct the highlighted fields.", errors=errors), 400
        registrations = read_json_file(app.config["REGISTRATIONS_FILE"], [])
        registrations.append({**clean, "created_at": datetime.now(timezone.utc).isoformat()})
        write_json_file(app.config["REGISTRATIONS_FILE"], registrations)
        return jsonify(success=True, message="Thanks! Your registration has been received."), 201

    @app.route("/admin", methods=["GET", "POST"])
    def admin() -> Any:
        action = request.form.get("action")
        if action == "login":
            if request.form.get("password") == app.config["ADMIN_PASSWORD"]:
                session["admin_logged_in"] = True
                return redirect(url_for("admin"))
            return render_template("admin.html", logged_in=False, error="Incorrect password."), 401
        if action == "logout":
            session.clear()
            return redirect(url_for("admin"))
        if not session.get("admin_logged_in"):
            return render_template("admin.html", logged_in=False)
        if action == "save-announcement":
            announcements = load_announcements(app.config["ANNOUNCEMENT_FILE"])
            post_id = request.form.get("post_id", "")
            announcement = next((post for post in announcements if post.get("id") == post_id), None)
            if announcement is None:
                announcement = {"id": uuid4().hex, "created_at": datetime.now(timezone.utc).isoformat(), **DEFAULT_ANNOUNCEMENT}
                announcements.append(announcement)
            announcement.update({key: request.form.get(key, "").strip() for key in ("title", "start_date", "timings", "details", "whatsapp_group_link")})
            poster = request.files.get("poster")
            if poster and poster.filename:
                extension = Path(secure_filename(poster.filename)).suffix.lower()
                if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
                    return render_template("admin.html", logged_in=True, announcement=announcement, announcements=announcements, registrations=[], error="Upload a JPG, PNG, or WebP poster."), 400
                app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)
                filename = f"poster-{datetime.now().strftime('%Y%m%d%H%M%S')}{extension}"
                poster.save(app.config["UPLOAD_FOLDER"] / filename)
                announcement["poster"] = f"uploads/{filename}"
            write_json_file(app.config["ANNOUNCEMENT_FILE"], announcements)
            return redirect(url_for("admin_announcements" if post_id else "admin", saved="1"))
        if action == "delete-announcement":
            post_id = request.form.get("post_id", "")
            write_json_file(app.config["ANNOUNCEMENT_FILE"], [post for post in load_announcements(app.config["ANNOUNCEMENT_FILE"]) if post.get("id") != post_id])
            return redirect(url_for("admin_announcements", deleted="1"))
        if action == "save-review":
            name = request.form.get("student_name", "").strip()
            course = request.form.get("student_course", "").strip()
            video = request.files.get("review_video")
            if not name or not course or not video or not video.filename:
                return redirect(url_for("admin", review_error="1"))
            extension = Path(secure_filename(video.filename)).suffix.lower()
            if extension not in {".mp4", ".webm", ".ogg"}:
                return redirect(url_for("admin", review_error="1"))
            app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)
            filename = f"review-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}{extension}"
            video.save(app.config["UPLOAD_FOLDER"] / filename)
            reviews = read_json_file(app.config["REVIEWS_FILE"], [])
            reviews.append({"id": uuid4().hex, "name": name, "course": course, "video": f"uploads/{filename}", "created_at": datetime.now(timezone.utc).isoformat()})
            write_json_file(app.config["REVIEWS_FILE"], reviews)
            return redirect(url_for("admin", review_saved="1"))
        if action == "delete-review":
            review_id = request.form.get("review_id", "")
            write_json_file(app.config["REVIEWS_FILE"], [review for review in read_json_file(app.config["REVIEWS_FILE"], []) if review.get("id") != review_id])
            return redirect(url_for("admin_reviews", review_deleted="1"))
        announcements = load_announcements(app.config["ANNOUNCEMENT_FILE"])
        registrations = list(reversed(read_json_file(app.config["REGISTRATIONS_FILE"], [])))
        return render_template("admin.html", logged_in=True, announcement=DEFAULT_ANNOUNCEMENT.copy(), registrations=registrations, saved=request.args.get("saved"), review_saved=request.args.get("review_saved"), review_error=request.args.get("review_error"))

    @app.get("/admin/announcements")
    def admin_announcements() -> Any:
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin"))
        announcements = load_announcements(app.config["ANNOUNCEMENT_FILE"])
        edit_id = request.args.get("edit", "")
        announcement = next((post for post in announcements if post.get("id") == edit_id), DEFAULT_ANNOUNCEMENT.copy())
        return render_template("admin_announcements.html", announcement=announcement, announcements=announcements, saved=request.args.get("saved"), deleted=request.args.get("deleted"))

    @app.get("/admin/reviews")
    def admin_reviews() -> Any:
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin"))
        reviews = list(reversed(read_json_file(app.config["REVIEWS_FILE"], [])))
        return render_template("admin_reviews.html", reviews=reviews, deleted=request.args.get("review_deleted"))

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
