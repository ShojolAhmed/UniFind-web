# Deployment Guide

This guide walks through deploying UniFind to production using a free-tier
stack:

- **Backend (Django REST API)** → [Render](https://render.com) Web Service
- **Database** → Render PostgreSQL
- **Media/image storage** → [Cloudinary](https://cloudinary.com)
- **Frontend (React SPA)** → [Vercel](https://vercel.com)

The backend and frontend deploy independently. Deploy the backend first so you
have its public URL when configuring the frontend.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [1. Cloudinary (media storage)](#1-cloudinary-media-storage)
- [2. Backend on Render](#2-backend-on-render)
- [3. Frontend on Vercel](#3-frontend-on-vercel)
- [4. Connect the two](#4-connect-the-two)
- [Environment Variable Reference](#environment-variable-reference)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- The repository pushed to GitHub.
- Free accounts on Render, Vercel, and Cloudinary.

---

## 1. Cloudinary (media storage)

Uploaded item images must be stored off the server, because Render's filesystem
is ephemeral (wiped on every deploy/restart).

1. Create a free Cloudinary account.
2. From the dashboard, copy the **API environment variable** value. It looks
   like:
   ```
   cloudinary://<API_KEY>:<API_SECRET>@<CLOUD_NAME>
   ```
3. Keep this value for the backend's `CLOUDINARY_URL` environment variable.

When `CLOUDINARY_URL` is set, Django automatically stores uploads on Cloudinary;
when it is unset (local dev), uploads fall back to the local filesystem.

---

## 2. Backend on Render

The repository includes [`render.yaml`](render.yaml), a Render Blueprint that
provisions the API web service **and** a PostgreSQL database, and wires them
together.

1. In Render, choose **New + → Blueprint** and select your GitHub repository.
2. Render reads `render.yaml` and creates:
   - a PostgreSQL database (`unifind-db`), and
   - a Python web service (`unifind-api`, `rootDir: backend`) that runs
     `pip install`, `collectstatic`, and `migrate` on build, then starts
     Gunicorn.
3. `SECRET_KEY` is generated automatically and `DATABASE_URL` is injected from
   the database. In the service's **Environment** tab, set the values marked
   `sync: false`:
   - `CLOUDINARY_URL` — from [step 1](#1-cloudinary-media-storage)
   - `CORS_ALLOWED_ORIGINS` — your frontend origin (add after
     [step 3](#3-frontend-on-vercel)), e.g. `https://unifind.vercel.app`
   - `CSRF_TRUSTED_ORIGINS` — your backend origin, e.g.
     `https://unifind-api.onrender.com`
   - `ALLOWED_HOSTS` — optional; the Render hostname is added automatically
4. **Create the initial admin account.** Render's free tier has no Shell or
   Jobs, so the build step runs `python manage.py ensure_superuser`, which
   creates a superuser from environment variables (idempotent — safe on every
   deploy). In the **Environment** tab, set:
   - `DJANGO_SUPERUSER_USERNAME`
   - `DJANGO_SUPERUSER_EMAIL`
   - `DJANGO_SUPERUSER_PASSWORD`

   Then redeploy (**Manual Deploy → Deploy latest commit**). Look for
   `ensure_superuser: created superuser "<name>"` in the build logs. For
   security you can remove `DJANGO_SUPERUSER_PASSWORD` afterwards; the account
   already exists and won't be recreated.

   **Alternative (no redeploy):** create the account from your machine against
   the database's **External Database URL** (Render → *unifind-db* → *Connect* →
   *External Database URL*):
   ```powershell
   # PowerShell, from the backend/ directory with the venv active
   $env:DATABASE_URL = "<external-database-url>"; $env:DB_SSL_REQUIRE = "True"
   python manage.py createsuperuser
   ```
   ```bash
   # bash/zsh
   DATABASE_URL="<external-database-url>" DB_SSL_REQUIRE=True python manage.py createsuperuser
   ```
5. Verify the API is live: `https://<your-service>.onrender.com/api/health/`
   should return `{"status": "ok"}`.

> The Python runtime is pinned to 3.12 (`PYTHON_VERSION` in `render.yaml` and
> `backend/.python-version`).

---

## 3. Frontend on Vercel

1. In Vercel, **Add New → Project** and import the repository.
2. Set **Root Directory** to `frontend`. Vercel auto-detects Vite
   (build: `npm run build`, output: `dist`).
3. Add an environment variable:
   - `VITE_API_URL` = `https://<your-render-service>.onrender.com/api`
4. Deploy. [`frontend/vercel.json`](frontend/vercel.json) configures SPA
   routing so client-side routes resolve on refresh.

---

## 4. Connect the two

1. Copy your Vercel URL (e.g. `https://unifind.vercel.app`).
2. In Render, set the backend's `CORS_ALLOWED_ORIGINS` to that URL and
   `CSRF_TRUSTED_ORIGINS` to the Render URL, then trigger a redeploy (or save,
   which redeploys automatically).
3. Open the Vercel URL and confirm you can register, post an item, and claim.

For preview deployments, you can allow Vercel's preview domains with a regex via
`CORS_ALLOWED_ORIGIN_REGEXES`, e.g. `^https://.*\.vercel\.app$`.

---

## Environment Variable Reference

All backend variables are read from the environment (or a local `.env` in
development). See [`backend/.env.example`](backend/.env.example).

| Variable | Where | Required | Description |
|---|---|---|---|
| `SECRET_KEY` | backend | ✓ (prod) | Django secret key. Auto-generated by `render.yaml`. |
| `DEBUG` | backend | – | `True` locally only. Production sets `False`. |
| `DATABASE_URL` | backend | ✓ (prod) | Postgres connection string. Injected by Render. |
| `CLOUDINARY_URL` | backend | ✓ (prod) | Cloudinary credentials for media storage. |
| `CORS_ALLOWED_ORIGINS` | backend | ✓ (prod) | Comma-separated frontend origins allowed to call the API. |
| `CSRF_TRUSTED_ORIGINS` | backend | recommended | Trusted origins for admin/browsable API over HTTPS. |
| `ALLOWED_HOSTS` | backend | – | Extra hostnames; Render's hostname is added automatically. |
| `CORS_ALLOWED_ORIGIN_REGEXES` | backend | – | Regex origins (e.g. preview URLs). |
| `SECURE_HSTS_SECONDS` | backend | – | HSTS max-age. Set on a real HTTPS domain (`render.yaml` sets 30 days). |
| `SECURE_SSL_REDIRECT` | backend | – | Redirect HTTP→HTTPS in production (default on when `DEBUG=False`). |
| `DJANGO_SUPERUSER_USERNAME` | backend | – | Admin username created by `ensure_superuser` on deploy. |
| `DJANGO_SUPERUSER_EMAIL` | backend | – | Admin email for the bootstrapped superuser. |
| `DJANGO_SUPERUSER_PASSWORD` | backend | – | Admin password for the bootstrapped superuser. |
| `VITE_API_URL` | frontend | ✓ (prod) | Base API URL including `/api`. |

---

## Troubleshooting

**Frontend shows "Network Error" and the backend logs `301` on every request.**
The backend is running with `DEBUG=False` locally, which forces an HTTP→HTTPS
redirect that the local dev server cannot serve. For local development, ensure
`DEBUG=True` in `backend/.env`, make sure no `DEBUG=False` is exported in your
shell, and restart `runserver`.

**"Network Error" persists after fixing `DEBUG`.**
A previous `DEBUG=False` run may have sent an HSTS header that pins HTTPS on
`localhost`/`127.0.0.1` in your browser. Clear it: open
`chrome://net-internals/#hsts` (or `edge://net-internals/#hsts`), and under
**Delete domain security policies** delete `127.0.0.1` and `localhost`, then
hard-reload (Ctrl+Shift+R).

**CORS errors in the browser console.**
Ensure the exact frontend origin (scheme + host, no trailing slash) is listed in
the backend's `CORS_ALLOWED_ORIGINS`, and redeploy the backend after changing it.

**Uploaded images don't persist after a redeploy.**
`CLOUDINARY_URL` is not set, so uploads are written to Render's ephemeral disk.
Set `CLOUDINARY_URL` and redeploy.

**`POST /api/items/` returns `500` when uploading an item.**
The image upload to Cloudinary is failing — usually a wrong or malformed
`CLOUDINARY_URL`. It must be exactly `cloudinary://API_KEY:API_SECRET@CLOUD_NAME`
(the "API Environment variable" value from the Cloudinary dashboard), with no
surrounding quotes or the `CLOUDINARY_URL=` prefix included in the value. The
full traceback is written to the Render logs (logging is always enabled).

**Can't create a superuser — the free plan has no Shell.**
Use the environment-variable bootstrap or an external DB connection described in
[step 4](#2-backend-on-render).

**`400 Bad Request` / `DisallowedHost`.**
Add the host to `ALLOWED_HOSTS`. The Render hostname is added automatically, so
this typically only affects custom domains.

**First request after idle is slow.**
Render's free tier spins services down when idle; the first request cold-starts
the service. This is expected on the free plan.
