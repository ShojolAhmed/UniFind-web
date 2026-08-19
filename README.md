# UniFind

> A centralized, university-based Lost &amp; Found platform for reporting, discovering, and claiming items across campus.

![Django](https://img.shields.io/badge/Django-6.1-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.18-A30000)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

UniFind is a decoupled web application: a **Django REST Framework API** and a
**React (Vite) single-page app** that communicate over JSON with JWT
authentication. The two halves can be developed, scaled, and deployed
independently.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

- **JWT authentication** — register, log in, and stay signed in with automatic
  access-token refresh.
- **Item reporting** — post lost or found items with a title, type, description,
  location, contact, and image.
- **Browse, search & filter** — search by title or location and filter by
  Lost / Found status.
- **Claim workflow** — submit a claim on an item; the owner is notified and can
  approve or reject it. Approving a claim marks the item as claimed and
  automatically rejects competing claims.
- **In-app notifications** — owners and claimants are notified of claim activity,
  with an unread badge.
- **Student dashboard** — track your posts, pending claims, and claimed items.
- **Admin panel** — manage users, items, claims, and notifications via Django admin.

## Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python, Django 6.1, Django REST Framework, SimpleJWT, django-cors-headers |
| **Database** | SQLite (development), PostgreSQL (production) |
| **Media** | Local filesystem (development), Cloudinary (production) |
| **Frontend** | React 19, Vite, React Router, Axios |
| **Serving** | Gunicorn, WhiteNoise |

## Architecture

```text
UniFind-web/
├── backend/                # Django + Django REST Framework API (JSON only)
│   ├── lost_and_found/     # Project config (settings, urls, wsgi/asgi)
│   ├── items/              # App: models, serializers, api views, permissions, admin, tests
│   ├── manage.py
│   ├── requirements.txt
│   ├── Procfile
│   ├── .python-version
│   └── .env.example
├── frontend/               # React 19 + Vite SPA
│   ├── src/
│   │   ├── api/            # Axios client with JWT + auto-refresh
│   │   ├── context/        # Auth + Toast providers
│   │   ├── components/     # Layout, ItemCard, ProtectedRoute
│   │   └── pages/          # Home, Login, Signup, Dashboard, Add, Edit, Notifications
│   ├── vercel.json
│   └── .env.example
├── render.yaml             # Render Blueprint (API web service + Postgres)
├── DEPLOYMENT.md           # Production deployment guide
└── CONTRIBUTING.md         # Contribution guidelines
```

The frontend communicates with the backend exclusively over HTTP/JSON. The
backend renders HTML only for the Django admin and the DRF browsable API.

## Getting Started

### Prerequisites

- **Python** 3.12+
- **Node.js** 20+
- **Git**

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

# Create a local env file (defaults to SQLite + DEBUG=True)
cp .env.example .env

python manage.py migrate
python manage.py createsuperuser   # optional, for the admin panel
python manage.py runserver
```

The API is served at `http://127.0.0.1:8000/`:

- `http://127.0.0.1:8000/api/` — browsable API root
- `http://127.0.0.1:8000/api/health/` — health check
- `http://127.0.0.1:8000/admin/` — Django admin

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173/` and, by default, talks to the local API
at `http://127.0.0.1:8000/api`.

## Configuration

Both apps are configured through environment variables; nothing sensitive is
committed. Copy the provided examples and adjust as needed:

- Backend: [`backend/.env.example`](backend/.env.example)
- Frontend: [`frontend/.env.example`](frontend/.env.example)

A minimal backend `.env` for local development:

```env
DEBUG=True
SECRET_KEY=dev-local-only-secret-key
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

A full description of every variable is in the
[Environment Variable Reference](DEPLOYMENT.md#environment-variable-reference).

## API Reference

All endpoints are prefixed with `/api/`. List endpoints are paginated and return
`{ count, next, previous, results }`.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register/` | – | Create an account; returns JWT tokens + user |
| `POST` | `/auth/token/` | – | Log in; returns `access` / `refresh` + user |
| `POST` | `/auth/token/refresh/` | – | Exchange a refresh token for a new access token |
| `GET` | `/auth/me/` | ✓ | Current user profile |
| `GET` | `/items/` | – | List / search items (`?title=`, `?location=`, `?item_type=`, `?owner=me`, `?claimed_by=me`) |
| `POST` | `/items/` | ✓ | Create an item (multipart, with image) |
| `GET` | `/items/{id}/` | – | Item detail |
| `PATCH` / `PUT` | `/items/{id}/` | owner | Update an item |
| `DELETE` | `/items/{id}/` | owner | Delete an item |
| `POST` | `/items/{id}/claim/` | ✓ | Submit a claim |
| `GET` | `/claims/` | ✓ | My submitted claims (`?status=pending`) |
| `POST` | `/claims/{id}/approve/` | item owner | Approve a claim (auto-rejects competing claims) |
| `POST` | `/claims/{id}/reject/` | item owner | Reject a claim |
| `GET` | `/notifications/` | ✓ | My notifications |
| `POST` | `/notifications/{id}/read/` | ✓ | Mark one notification as read |
| `POST` | `/notifications/read-all/` | ✓ | Mark all as read |
| `GET` | `/notifications/unread-count/` | ✓ | Unread notification count |

## Testing

```bash
cd backend
python manage.py test
```

The suite covers authentication, item CRUD with owner-only permissions, the
claim/approve/reject workflow, and notifications.

To verify a production frontend build:

```bash
cd frontend
npm run build
```

## Deployment

UniFind is designed to run on a free-tier stack: **Render** (API + PostgreSQL),
**Cloudinary** (media), and **Vercel** (frontend). See
**[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step instructions,
an environment-variable reference, and troubleshooting.

## Contributing

Contributions are welcome. Please read
**[CONTRIBUTING.md](CONTRIBUTING.md)** for the development workflow, coding
standards, and pull-request process.

## License

Released under the [MIT License](LICENSE). Copyright (c) 2026 Shojol.
