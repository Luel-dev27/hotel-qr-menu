# Hotel QR Menu System

This is a hotel QR menu system I built with a React frontend and a Django backend.

It includes:

- a public guest menu
- a protected staff workspace
- one hotel QR code that opens the guest menu

## How it works

- Guests scan one hotel QR code and land on the public menu.
- Staff log in to `/admin` to manage menu items and categories.
- API routes are available under `/api/...`.
- Django's built-in admin is available at `/django-admin/`.
- `/manage/` is only a shortcut that redirects to `/django-admin/`.

## Tech stack

- `frontend/`: Vite + React
- `backend/`: Django

## Demo staff login

<<<<<<< HEAD
- Username:
- Password:
=======
For local development only:

- Username: `admin`
- Password: `admin123`
>>>>>>> 657cb5a (update Readme)

For production, create a real staff account and remove any shared demo credentials.

## Local development

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

This setup serves:

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

<<<<<<< HEAD
The in this repo is:
=======
The production setup included in this repository uses:
>>>>>>> 657cb5a (update Readme)

- `Docker Compose`
- `PostgreSQL`
- `Gunicorn`
- `Nginx`

## Render deployment

This repository includes a Render Blueprint file at [render.yaml](/home/dark/projects/scanner/render.yaml:1).

<<<<<<< HEAD
=======
### Why I prepared a Render setup

- It uses a Render web service and Render PostgreSQL.
- Render automatically provides HTTPS for both `onrender.com` subdomains and custom domains.
- Render automatically redirects HTTP traffic to HTTPS.
- The app is configured to work with Render host and CSRF handling.

>>>>>>> 657cb5a (update Readme)
### Deploy on Render

1. Push this repository to GitHub, GitLab, or Bitbucket.
2. In Render, open `Blueprints` and create a new Blueprint from this repository.
3. Render will create:
   - `scanner-web` as the web service
   - `scanner-db` as the PostgreSQL database
4. During the first Blueprint apply, set these values:
   - `DJANGO_ALLOWED_HOSTS`
   - `DJANGO_CORS_ALLOWED_ORIGINS`
   - `DJANGO_CSRF_TRUSTED_ORIGINS`

<<<<<<< HEAD
=======
Use your real Render subdomain or your real custom domain.

Example:

- If Render gives the web service URL `https://scanner-web.onrender.com`
- then set `DJANGO_ALLOWED_HOSTS` to `scanner-web.onrender.com`
- set `DJANGO_CORS_ALLOWED_ORIGINS` to `https://scanner-web.onrender.com`
- set `DJANGO_CSRF_TRUSTED_ORIGINS` to `https://scanner-web.onrender.com`

If I later connect a custom domain such as `menu.myhotel.com`, I should update these values to include that real domain too.

>>>>>>> 657cb5a (update Readme)
### After deploy

Create the first admin user from the Render Shell:

```bash
python /app/backend/manage.py createsuperuser
```

Then open the live app using the actual domain connected to the deployment.

<<<<<<< HEAD
- Guest menu: `https://my-service.onrender.com/`
- Hotel staff admin: `https://my-service.onrender.com/admin`
- Django system admin: `https://my-service.onrender.com/manage/`

### Custom domain and HTTPS

Add my custom domain in the Render Dashboard under your web service settings. Render will:
=======
Example:

- Guest menu: `https://scanner-web.onrender.com/`
- Staff workspace: `https://scanner-web.onrender.com/admin`
- Django admin: `https://scanner-web.onrender.com/django-admin/`
- Django admin shortcut: `https://scanner-web.onrender.com/manage/`

### Custom domain and HTTPS

Add the custom domain in the Render dashboard under the web service settings. Render will:
>>>>>>> 657cb5a (update Readme)

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

Use the real server address for the machine or domain where the app is deployed.

Example if running on a server with domain `menu.myhotel.com`:

- Guest menu: `http://menu.myhotel.com/`
- Staff workspace: `http://menu.myhotel.com/admin`
- Django admin: `http://menu.myhotel.com/django-admin/`
- Django admin shortcut: `http://menu.myhotel.com/manage/`

### 5. Useful commands

```bash
npm run docker:logs
npm run docker:down
docker compose ps
```

## Legacy manual deployment checklist

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
8. Start the app with `npm run start:prod`.
9. Put Nginx, Caddy, or another reverse proxy in front for HTTPS and forwarded headers.

Example deployment assets:

- `deploy/scanner.service.example`
- `deploy/nginx.scanner.conf.example`

## Production notes

- `/admin` is the hotel staff workspace and only staff users should be allowed to log in.
- `/manage/` redirects to Django's built-in admin at `/django-admin/`.
- The API expects valid CSRF protection on write actions, and the built frontend sends it automatically.
- The QR endpoint is restricted to generating links for the current deployed site.
- If TLS is terminated at a reverse proxy, keep `DJANGO_USE_X_FORWARDED_PROTO=True` so Django correctly treats requests as HTTPS.
- The container stack exposes Nginx on `APP_PORT` and proxies requests to Django internally.
- A health endpoint is available at `/api/health`.

## Important routes

- Guest menu: `/`
- Staff workspace: `/admin`
- Django admin: `/django-admin/`
- Django admin shortcut: `/manage/`
