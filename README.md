# Hotel QR Menu System

This project is a hotel menu system with:

- a public guest menu
- a protected staff workspace
- one hotel QR code that opens the guest menu

## Current behavior

- Guests scan one hotel QR code and land on the public menu
- Staff manage menu items and categories from `/admin`
- Django API routes stay under `/api/...`
- Django's built-in admin is available at `/django-admin/`

## Tech stack

- `frontend/`: Vite + React
- `backend/`: Django

## Demo staff login

- Username:
- Password:

Use the demo login for local development only. In production, create a real staff user and remove any shared demo credentials.

## Development

Start the backend:

```bash
npm run dev:server
```

Start the frontend:

```bash
npm run dev
```

The Vite frontend proxies `/api` requests to `http://localhost:8000`.

## Production build

Build the frontend and collect static files for Django:

```bash
npm run build:prod
```

Apply migrations:

```bash
backend/.venv/bin/python backend/manage.py migrate
```

Start the production server:

```bash
npm run start:prod
```

This serves:

- the React app from Django
- API routes from Django
- built frontend assets from Django static files
- secure admin write actions protected by Django CSRF

## Environment variables

Copy `.env.example` and set real values for production:

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

## Production deployment

The in this repo is:

- `Docker Compose`
- `PostgreSQL`
- `Gunicorn`
- `Nginx`

## Render deployment

This repo is now prepared for Render with a Blueprint file at [render.yaml](/home/dark/projects/scanner/render.yaml:1).

### Deploy on Render

1. Push this repository to GitHub, GitLab, or Bitbucket.
2. In Render, open `Blueprints` and create a new Blueprint from this repo.
3. Render will create:
   - `scanner-web` as the web service
   - `scanner-db` as the PostgreSQL database
4. During the first Blueprint apply, set these prompted values:
   - `DJANGO_ALLOWED_HOSTS`
   - `DJANGO_CORS_ALLOWED_ORIGINS`
   - `DJANGO_CSRF_TRUSTED_ORIGINS`

### After deploy

Create the first admin user from the Render Shell:

```bash
python /app/backend/manage.py createsuperuser
```

Then use:

- Guest menu: `https://my-service.onrender.com/`
- Hotel staff admin: `https://my-service.onrender.com/admin`
- Django system admin: `https://my-service.onrender.com/manage/`

### Custom domain and HTTPS

Add my custom domain in the Render Dashboard under your web service settings. Render will:

- issue and renew the TLS certificate for you
- keep HTTPS enabled automatically
- redirect HTTP to HTTPS automatically

### 1. Prepare the environment

```bash
cp .env.example .env
```

Then edit `.env` and set:

- a real `DJANGO_SECRET_KEY`
- your real domain in `DJANGO_ALLOWED_HOSTS`
- your HTTPS origin in `DJANGO_CORS_ALLOWED_ORIGINS`
- your HTTPS origin in `DJANGO_CSRF_TRUSTED_ORIGINS`
- strong `POSTGRES_PASSWORD`

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

- Guest menu: `http://your-server/`
- Staff workspace: `http://your-server/admin`
- Django admin alias: `http://your-server/manage/`

### 5. Useful commands

```bash
npm run docker:logs
npm run docker:down
docker compose ps
```

## Legacy/manual deploy checklist

1. Install Python dependencies from `backend/requirements.txt`
2. Install Node dependencies with `npm install`
3. Copy `.env.example` to `.env` and set production env vars
4. Run `backend/.venv/bin/python backend/manage.py migrate`
5. Create a real staff user:

```bash
backend/.venv/bin/python backend/manage.py createsuperuser
```

6. Run `npm run build:prod`
7. Run `backend/.venv/bin/python backend/manage.py check --deploy`
8. Start with `npm run start:prod`
9. Put Nginx, Caddy, or another reverse proxy in front for HTTPS and forwarded headers

Example deploy assets:

- `deploy/scanner.service.example`
- `deploy/nginx.scanner.conf.example`

## Production notes

- `/admin` is the hotel staff workspace and only staff users should be allowed to log in.
- `/manage/` redirects to Django's built-in admin for system administration.
- The API now expects valid CSRF protection on write actions, which the built frontend sends automatically.
- The QR endpoint is restricted to generating links for the current deployed site.
- If you terminate TLS at a reverse proxy, keep `DJANGO_USE_X_FORWARDED_PROTO=True` so Django correctly treats requests as HTTPS.
- The container stack exposes Nginx on `APP_PORT` and proxies requests to Django internally.
- A health endpoint is available at `/api/health`.

## Important routes

- Guest menu: `/`
- Staff workspace: `/admin`
- Django admin: `/django-admin/`
