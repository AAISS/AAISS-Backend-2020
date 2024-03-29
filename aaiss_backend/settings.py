"""
Django settings for aaiss_backend project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import configparser
import os
import environ
import mimetypes

# To make css load
mimetypes.add_type("text/html", ".css", True)

env = environ.Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(BASE_DIR + '/.env')

# production/development key
SECRET_KEY = env.str("SECRET_KEY", 'orlch#mu_+2-my=fo)akh_3+^j7+7tc@v*-*z^(g*%(&lih@pv')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", True)

ALLOWED_HOSTS = env.str("ALLOWED_HOSTS", "*").split(" ")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'backend_api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aaiss_backend.urls'
APPEND_SLASH = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/templates/html/'
        ],
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
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [
            BASE_DIR + '/templates/html/'],
    },
]
WSGI_APPLICATION = 'aaiss_backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
APPEND_SLASH = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default auth model
AUTH_USER_MODEL = 'backend_api.Account'

# media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# CORS
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ORIGIN_ALLOW_ALL = True

X_API_KEY = env.str('X_API_KEY', '')
X_SANDBOX = env.str('X_SANDBOX', '')

SERVER_EMAIL = 'smtp-relay.sendinblue.com'
EMAIL_BACKEND = "anymail.backends.sendinblue.EmailBackend"

EMAIL_HOST = env.str('EMAIL_HOST', '')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', '')
EMAIL_PORT = env.int('EMAIL_PORT', '')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
ANYMAIL = {
    "SENDINBLUE_API_KEY": env.str("SENDINBLUE_API_KEY", "")
}


ALT_EMAIL_HOST = env.str("ALT_EMAIL_HOST", '')
ALT_EMAIL_HOST_USER = env.str("ALT_EMAIL_HOST_USER", '')
ALT_EMAIL_HOST_PASSWORD = env.str("ALT_EMAIL_HOST_PASSWORD", '')
ALT_EMAIL_PORT = env.int("ALT_EMAIL_PORT", '')
ALT_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', '')
DISCORD_BOT_TOKEN = env.str('DISCORD_BOT_TOKEN', '')

BASE_URL = 'https://aaiss.ce.aut.ac.ir/'
