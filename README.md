# Work2Win Training Website

This is a Django website for publishing Work2Win courses, announcements, registration enquiries and approved student testimonials. Content is managed through Django Admin and the default SQLite database (`db.sqlite3`).

## Run locally

```text
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py createsuperuser
.venv\Scripts\python manage.py runserver
```

Open the public site at `http://127.0.0.1:8000/` and administration at `http://127.0.0.1:8000/admin/`.

## Admin workflow

1. Create and publish courses.
2. Create and schedule announcements.
3. Review and update registration enquiries.
4. Manage and approve student testimonials.

## Verification

```text
.venv\Scripts\python manage.py test
.venv\Scripts\python manage.py check
```
