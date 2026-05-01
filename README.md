# Hotel QR Menu System

A full-stack hotel menu system built with React and Django. The project is designed for hotels that want to let guests scan a single QR code and browse the menu on their phones, while staff manage categories and menu items from a protected admin workspace.

## Overview

This system provides two main experiences:

- a public guest-facing digital menu
- a protected staff workspace for managing menu content

The main idea is simple:

- Guests scan one hotel QR code.
- The QR code opens the public menu.
- Staff sign in to manage categories and menu items.
- The backend exposes API routes under `/api/...`.

## Main features

- Public guest menu available at `/r/<restaurant-slug>`
- Staff workspace available at `/admin/<restaurant-slug>`
- Django API endpoints under `/api/...`
- Django built-in admin available at `/django-admin/`
- `/manage/` redirects to `/django-admin/`
- CSRF-protected write actions for the admin workspace
- QR endpoint for generating links for the current deployed site
- Health check endpoint at `/api/health`

## Adding Restaurants

The system supports multiple restaurants on one deployment. Each restaurant has its own public menu URL, staff workspace, menu categories, menu items, and QR code.

1. Sign in as the system admin at `/django-admin/`.
2. Open `Restaurants` and create a restaurant. Set the name, slug, tagline, currency, and hero message.
3. In the restaurant form, assign the staff users who can manage that restaurant in the `admins` field.
4. Save the restaurant. A default QR/table record is created automatically.
5. Add categories for that restaurant.
6. Give the restaurant staff this URL: `/admin/<restaurant-slug>`.
7. Give customers or printed QR codes this URL: `/r/<restaurant-slug>`.

Example for a restaurant with slug `blue-cafe`:

- Guest menu: `/r/blue-cafe`
- Staff workspace: `/admin/blue-cafe`
- QR image endpoint: `/api/tables/blue-cafe-menu/qr?target=https://your-domain.com/r/blue-cafe`

Superusers can manage every restaurant. Normal staff users can only edit restaurants assigned to them.

## Tech stack

- `frontend/`: Vite + React
- `backend/`: Django
- Production stack: PostgreSQL, Gunicorn, Nginx, Docker Compose

## Project structure

```text
frontend/   React client
backend/    Django project and API
render.yaml Render Blueprint configuration
deploy/     Example deployment files
```

## Demo staff login
Local development includes a demo staff account:

- Username: `admin`
- Password: `admin123`

This account should only be used for local development. In production, create a real staff user and remove shared demo credentials.

## Local development

Start the Django backend:

```bash
npm run dev:server
```

Start the React frontend:

```bash
npm run dev
```

During development, the Vite frontend proxies `/api` requests to `http://localhost:8000`.

## Production build

Build the frontend and collect static files:

```bash
npm run build:prod
```

Apply database migrations:

```bash
backend/.venv/bin/python backend/manage.py migrate
```

Start the production server:

```bash
npm run start:prod
```

This setup serves:

- the React app through Django
- API routes through Django
- built frontend assets from Django static files
- admin write operations protected by Django CSRF

## Environment variables

Copy `.env.example` and configure real values for production:

- `DJANGO_DEBUG`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CORS_ALLOWED_ORIGINS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_DB_ENGINE`
- `DJANGO_DB_NAME`
- `DJANGO_DB_USER`
- `DJANGO_DB_PASSWORD`
- `DJANGO_DB_HOST`
- `DJANGO_DB_PORT`
- `DJANGO_SECURE_SSL_REDIRECT`
- `DJANGO_SESSION_COOKIE_SECURE`
- `DJANGO_CSRF_COOKIE_SECURE`
- `DJANGO_SECURE_HSTS_SECONDS`
- `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS`
- `DJANGO_SECURE_HSTS_PRELOAD`
- `DJANGO_USE_X_FORWARDED_HOST`
- `DJANGO_USE_X_FORWARDED_PORT`
- `DJANGO_USE_X_FORWARDED_PROTO`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `APP_PORT`

## Recommended production deployment
The production setup included in this repository uses:

- Docker Compose
- PostgreSQL
- Gunicorn
- Nginx

## Render deployment

This repository includes a Render Blueprint file at [render.yaml](/home/dark/projects/scanner/render.yaml:1).
### Deploy on Render

1. Push the repository to GitHub, GitLab, or Bitbucket.
2. In Render, open `Blueprints` and create a new Blueprint from this repository.
3. Render will create:
   - `scanner-web` as the web service
   - `scanner-db` as the PostgreSQL database
4. During the first Blueprint apply, set:
   - `DJANGO_ALLOWED_HOSTS`
   - `DJANGO_CORS_ALLOWED_ORIGINS`
   - `DJANGO_CSRF_TRUSTED_ORIGINS`

Use the real Render subdomain or the real custom domain connected to the deployment.

Example:

- If the service URL is `https://scanner-web.onrender.com`
- set `DJANGO_ALLOWED_HOSTS` to `scanner-web.onrender.com`
- set `DJANGO_CORS_ALLOWED_ORIGINS` to `https://scanner-web.onrender.com`
- set `DJANGO_CSRF_TRUSTED_ORIGINS` to `https://scanner-web.onrender.com`

If a custom domain such as `menu.example.com` is later attached, update these values to include that domain as well.

### After deployment

Create the first admin user from the Render shell:

```bash
python /app/backend/manage.py createsuperuser
```

Example routes after deployment:

- Guest menu: `https://scanner-web.onrender.com/r/aster-hotel`
- Staff workspace: `https://scanner-web.onrender.com/admin/aster-hotel`
- Django admin: `https://scanner-web.onrender.com/django-admin/`
- Django admin shortcut: `https://scanner-web.onrender.com/manage/`

### Custom domain and HTTPS
Render can:

- issue and renew TLS certificates automatically
- keep HTTPS enabled automatically
- redirect HTTP to HTTPS automatically

## Docker deployment

### 1. Prepare the environment

```bash
cp .env.example .env
```

Then edit `.env` and set:

- a real `DJANGO_SECRET_KEY`
- the real domain in `DJANGO_ALLOWED_HOSTS`
- the real HTTPS origin in `DJANGO_CORS_ALLOWED_ORIGINS`
- the real HTTPS origin in `DJANGO_CSRF_TRUSTED_ORIGINS`
- a strong `POSTGRES_PASSWORD`

### 2. Start the stack

```bash
npm run docker:up
```

This will:

- build the frontend into the backend image
- start PostgreSQL
- wait for the database
- run Django migrations
- collect static files
- start Gunicorn behind Nginx

### 3. Create the first admin user

```bash
docker compose exec web python /app/backend/manage.py createsuperuser
```

### 4. Open the app

Use the real server address or domain where the app is deployed.

Example:

- Guest menu: `http://menu.example.com/r/aster-hotel`
- Staff workspace: `http://menu.example.com/admin/aster-hotel`
- Django admin: `http://menu.example.com/django-admin/`
- Django admin shortcut: `http://menu.example.com/manage/`

### 5. Useful commands

```bash
npm run docker:logs
npm run docker:down
docker compose ps
```

## Manual deployment checklist

1. Install Python dependencies from `backend/requirements.txt`.
2. Install Node dependencies with `npm install`.
3. Copy `.env.example` to `.env` and set production environment variables.
4. Run `backend/.venv/bin/python backend/manage.py migrate`.
5. Create a real staff user:

```bash
backend/.venv/bin/python backend/manage.py createsuperuser
```

6. Run `npm run build:prod`.
7. Run `backend/.venv/bin/python backend/manage.py check --deploy`.
8. Start the application with `npm run start:prod`.
9. Put Nginx, Caddy, or another reverse proxy in front for HTTPS and forwarded headers.

Example deployment assets:

- `deploy/scanner.service.example`
- `deploy/nginx.scanner.conf.example`

## Production notes

- `/admin` is the hotel staff workspace and should only be accessible to staff users.
- `/manage/` redirects to Django's built-in admin at `/django-admin/`.
- The frontend sends the CSRF protection required by backend write actions.
- If TLS is terminated at a reverse proxy, keep `DJANGO_USE_X_FORWARDED_PROTO=True` so Django correctly treats requests as HTTPS.
- The container stack exposes Nginx on `APP_PORT` and proxies requests to Django internally.

## Important routes

- Guest menu: `/r/<restaurant-slug>`
- Staff workspace: `/admin/<restaurant-slug>`
- Default restaurant fallback: `/`
- Default admin fallback: `/admin`
- Django admin: `/django-admin/`
- Django admin shortcut: `/manage/`
- Health check: `/api/health`
