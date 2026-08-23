# Work2Win Technologies

A responsive professional-institute website for Work2Win Technologies. It provides course discovery, direct WhatsApp contact and a secure enquiry flow that persists to PostgreSQL before attempting an optional Resend email notification.

## Features

- Accessible, responsive single-page website for mobile through desktop
- Eleven maintainable course records rendered from Python configuration
- Client and server validation, request-size limit and safe API errors
- PostgreSQL/Supabase storage using parameterized SQL
- Optional Resend HTTPS notification after successful storage
- Floating WhatsApp contact, prefilled with the institute enquiry message
- Render blueprint, schema, tests and deployment guidance

## Structure

```text
app.py                 Flask app, courses, validation and API
templates/index.html   Website markup
static/css/style.css   Responsive visual design
static/js/app.js       Navigation and form behaviour
database/schema.sql    Supabase PostgreSQL schema
tests/                 Pytest coverage
```

## Local setup

1. Create and activate a Python 3.11+ virtual environment.
2. Run `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set the values below. Load it with your preferred local environment tool, or set the variables in your shell.
4. Run the SQL in `database/schema.sql` against local PostgreSQL or your Supabase database.
5. Start with `python app.py`, then visit `http://127.0.0.1:5000`.

Without `DATABASE_URL`, the application uses a local `work2win.db` SQLite file for development, so form submissions work immediately. This file is ignored by Git. PostgreSQL/Supabase is required in production; set `DATABASE_URL` to the Supabase URI before deployment.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | Supabase/PostgreSQL connection string; never commit it. |
| `ADMIN_EMAIL` | Notification recipient, normally `work2wintechnologies@gmail.com`. |
| `RESEND_API_KEY` | Resend API key; optional locally. |
| `FROM_EMAIL` | A verified Resend sender, such as `Work2Win <updates@your-domain>`. |

Email is intentionally best-effort. An enquiry is stored first; an email outage never discards it. `FROM_EMAIL` must be verified in Resend—do not use an unverified address.

## Supabase and Render deployment

1. Create a Supabase project and open its SQL editor.
2. Run `database/schema.sql`, then copy the project PostgreSQL connection string to `DATABASE_URL`.
3. Push this project to a new GitHub repository. Keep `.env` local only.
4. In Render, create a Blueprint from the repository (the included `render.yaml` supplies the build and start commands).
5. Enter `DATABASE_URL`, `RESEND_API_KEY` and `FROM_EMAIL` in Render’s secret environment-variable settings. Confirm `ADMIN_EMAIL`.
6. Deploy and submit a test enquiry. Verify the database row and, if configured, the notification email.

Supabase is the permanent datastore; Render’s free PostgreSQL offering is not used. Render supplies HTTPS for the public service. The application is not claimed as deployed until those manual account steps and the live verification are complete.

## WhatsApp

The floating contact link uses `https://wa.me/916300157088` with the specified URL-encoded message. Course-card links preselect the matching course in the form.

## Tests

Run `pytest`. Tests use an injected saver and mock the email path, so no production database or API credential is needed.

## Assumptions

- Fees, duration, certification, placements, trainer names and outcomes are not published because they were not supplied.
- Course records currently live in `app.py` to keep version one lightweight. Their fields align with the planned database model (`id`, `name`, `slug`, `description`, `category`, `active`, timestamps), making a future courses table migration straightforward.
- Rate limiting is left to Render/edge configuration for this lightweight deployment. For high-volume public traffic, add Flask-Limiter backed by a shared store and optionally CAPTCHA.

## Troubleshooting

- A 500 on submission normally means `DATABASE_URL` is missing, inaccessible or its schema was not installed; review server logs rather than exposing diagnostic details to visitors.
- If the record saves but no email arrives, check Resend’s verified sender, API key and delivery logs.
- Ensure the Supabase connection URL works from Render (use its recommended pooled connection configuration where appropriate).
