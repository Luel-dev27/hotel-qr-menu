"""
Django settings for config project.
"""

import dj_database_url
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent
FRONTEND_DIST_DIR = BASE_DIR / 'frontend_dist'


def parse_csv(value):
    return [item.strip() for item in value.split(',') if item.strip()]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    'DJANGO_SECRET_KEY',
    default='django-insecure-dev-key-change-me',
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)
ON_RENDER = config('RENDER', default=False, cast=bool)
RENDER_EXTERNAL_HOSTNAME = config('RENDER_EXTERNAL_HOSTNAME', default='')
RENDER_EXTERNAL_URL = config('RENDER_EXTERNAL_URL', default='')

ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS',
    default='127.0.0.1,localhost',
    cast=parse_csv,
)

if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

USE_X_FORWARDED_HOST = config('DJANGO_USE_X_FORWARDED_HOST', default=not DEBUG, cast=bool)
USE_X_FORWARDED_PORT = config('DJANGO_USE_X_FORWARDED_PORT', default=not DEBUG, cast=bool)
if config('DJANGO_USE_X_FORWARDED_PROTO', default=not DEBUG, cast=bool):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'menuapi',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [FRONTEND_DIST_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=not DEBUG),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': config('DJANGO_DB_ENGINE', default='django.db.backends.sqlite3'),
            'NAME': config('DJANGO_DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
            'USER': config('DJANGO_DB_USER', default=''),
            'PASSWORD': config('DJANGO_DB_PASSWORD', default=''),
            'HOST': config('DJANGO_DB_HOST', default=''),
            'PORT': config('DJANGO_DB_PORT', default=''),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Addis_Ababa'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [FRONTEND_DIST_DIR] if FRONTEND_DIST_DIR.exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

SECURE_SSL_REDIRECT = config('DJANGO_SECURE_SSL_REDIRECT', default=not DEBUG, cast=bool)
SESSION_COOKIE_SECURE = config('DJANGO_SESSION_COOKIE_SECURE', default=not DEBUG, cast=bool)
CSRF_COOKIE_SECURE = config('DJANGO_CSRF_COOKIE_SECURE', default=not DEBUG, cast=bool)
SECURE_HSTS_SECONDS = config('DJANGO_SECURE_HSTS_SECONDS', default=31536000 if not DEBUG else 0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
    'DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS',
    default=not DEBUG,
    cast=bool,
)
SECURE_HSTS_PRELOAD = config('DJANGO_SECURE_HSTS_PRELOAD', default=not DEBUG, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = config('DJANGO_SECURE_REFERRER_POLICY', default='same-origin')
X_FRAME_OPTIONS = config('DJANGO_X_FRAME_OPTIONS', default='DENY')

CSRF_TRUSTED_ORIGINS = config(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    default='http://127.0.0.1,http://localhost',
    cast=parse_csv,
)

if RENDER_EXTERNAL_URL and RENDER_EXTERNAL_URL not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(RENDER_EXTERNAL_URL)

CORS_ALLOWED_ORIGINS = config(
    'DJANGO_CORS_ALLOWED_ORIGINS',
    default='http://localhost:5173',
    cast=parse_csv,
)

if RENDER_EXTERNAL_URL and RENDER_EXTERNAL_URL not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(RENDER_EXTERNAL_URL)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
