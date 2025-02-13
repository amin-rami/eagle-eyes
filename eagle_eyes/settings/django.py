"""
Django settings for eagle_eyes project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path
from corsheaders.defaults import default_headers

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', '') == "true"

# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space between each.
# For example: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]'
if DEBUG is True:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", default='localhost 127.0.0.1 [::1]').split(" ")
CSRF_TRUSTED_ORIGINS = [item for item in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if item != '']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'django_jsonform',
    'django_prometheus',
    'nested_admin',
    'corsheaders',
    'cacheops',
    'safedelete',

    'eagle_eyes.apps.campaigns',
    'eagle_eyes.apps.eagleusers',
    'eagle_eyes.apps.lucky_wheel',
    'eagle_eyes.apps.behsa',
    'eagle_eyes.apps.games',
    'eagle_eyes.apps.referral',
    'eagle_eyes.apps.referral_reward',
    'eagle_eyes.apps.general_processor',
    'eagle_eyes.apps.club'
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
    'eagle_eyes.middleware.userid.UserIDMiddleware',
    'eagle_eyes.middleware.logs.RequestResponseLogMiddleware',
]

ROOT_URLCONF = 'eagle_eyes.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eagle_eyes.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.getenv("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("SQL_DATABASE", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("SQL_USER", "user"),
        "PASSWORD": os.getenv("SQL_PASSWORD", "password"),
        "HOST": os.getenv("SQL_HOST", "localhost"),
        "PORT": os.getenv("SQL_PORT", "5432"),
    }
}

# DRF versioning
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissions',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


REDIS_USER = os.getenv("REDIS_USER", "")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "1")
REDIS_CONFIG = {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f'redis://{REDIS_USER}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,  # seconds
            "SOCKET_TIMEOUT": 5,  # seconds
        }
    }
DATABASE_CACHE_CONFIG = {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_table",
    }
TEST_MODE = os.getenv("TEST_MODE", "false")
CACHE_CONFIG = DATABASE_CACHE_CONFIG if TEST_MODE == "true" else REDIS_CONFIG

CACHES = {
    "default": CACHE_CONFIG
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'req_resp_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, "logs", "requests_responses", "logs.log"),
            'maxBytes': os.getenv('MAXBYTES', 100000000),
            'backupCount': os.getenv('BACKUPCOUNT', 2),
            'level': 'DEBUG',
        },
        'event_processor_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, "logs", "processor", "logs.log"),
            'maxBytes': os.getenv('MAXBYTES', 20000000),
            'backupCount': os.getenv('BACKUPCOUNT', 2),
            'level': 'DEBUG',
        },
        'eagleusers_api_calls_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, "logs", "eagleusers_api_calls", "logs.log"),
            'maxBytes': os.getenv('MAXBYTES', 20000000),
            'backupCount': os.getenv('BACKUPCOUNT', 2),
            'level': 'DEBUG',
        },
        'external_api_calls_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, "logs", "external_api_calls.json.log"),
            'maxBytes': os.getenv('MAXBYTES', 20000000),
            'backupCount': os.getenv('BACKUPCOUNT', 2),
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'requests_responses': {
            'handlers': ['req_resp_file'],
            'level': 'DEBUG'
        },
        'event_processor': {
            'handlers': ['event_processor_file'],
            'level': 'DEBUG'
        },
        'eagleusers_api_calls': {
            'handlers': ['eagleusers_api_calls_file'],
            'level': 'DEBUG'
        },
        'external_api_calls': {
            'handlers': ['external_api_calls_handler'],
            'level': 'DEBUG'
        }
    },
}

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'eagleusers.EagleUser'
CORS_ALLOW_HEADERS = list(default_headers) + ['x-token', 'x-client', 'x-device-id']
DATA_UPLOAD_MAX_NUMBER_FIELDS = None
METRICS_PREFIX = os.getenv('METRICS_PREFIX', 'gfs_eagle_eyes')
