# Contributing to UniFind

Thanks for your interest in improving UniFind! This document explains how to set
up the project, the conventions we follow, and how to propose changes.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Project Layout](#project-layout)
- [Development Setup](#development-setup)
- [Branching & Commits](#branching--commits)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Requests](#pull-requests)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

Be respectful and constructive. Assume good intent, keep discussions technical,
and help maintain a welcoming environment for everyone.

## Project Layout

UniFind is a monorepo with two independently deployable apps:

- `backend/` — Django + Django REST Framework JSON API
- `frontend/` — React (Vite) single-page application

See [`README.md`](README.md) for the full architecture and
[`DEPLOYMENT.md`](DEPLOYMENT.md) for deployment.

## Development Setup

Follow the **Getting Started** section of the [`README.md`](README.md) to run
the backend (`http://127.0.0.1:8000`) and frontend (`http://localhost:5173`)
locally. In short:

```bash
# Backend
cd backend
python -m venv venv && venv\Scripts\activate   # or: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Branching & Commits

- Create a feature branch from `main`: `git checkout -b feature/short-description`.
- Use clear, imperative commit messages (e.g. `Add claim rejection endpoint`).
- Conventional Commit prefixes are welcome but not required
  (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
- Keep commits focused; avoid mixing unrelated changes.

## Coding Standards

**Backend (Python / Django)**
- Follow PEP 8; keep views thin and put reusable logic in serializers/models.
- Add or update serializers and permissions when changing API behavior.
- Create migrations for any model change (`python manage.py makemigrations`).
- Never commit secrets. Configuration comes from environment variables
  (see `backend/.env.example`).

**Frontend (React)**
- Use functional components and hooks.
- Keep API calls in `src/api/`, shared state in `src/context/`.
- Run the linter before pushing: `npm run lint`.
- Keep components small and reuse the existing design system in `src/index.css`.

## Testing

Every backend change should keep the test suite green and add coverage for new
behavior:

```bash
cd backend
python manage.py test
```

For the frontend, ensure a production build succeeds:

```bash
cd frontend
npm run build
```

## Pull Requests

1. Ensure `python manage.py test` passes and `npm run build` succeeds.
2. Update documentation (`README.md` / `DEPLOYMENT.md`) when behavior changes.
3. Describe **what** changed and **why**, and link any related issue.
4. Keep PRs reasonably small and focused for easier review.

## Reporting Issues

Open a GitHub issue and include:

- A clear description of the problem or request.
- Steps to reproduce, expected vs. actual behavior.
- Environment details (OS, Python/Node versions) and relevant logs.

Thanks for contributing!
