"""
Django settings for Karspexet project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
import contextlib
import json
import logging
import os
from urllib.parse import urljoin

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def to_bool(value: str) -> bool:
    value = value.lower()
    if value == "true":
        return True
    if value == "false":
        return False
    raise ValueError(value)


ENV: dict = {}
with contextlib.suppress(FileNotFoundError):
    with open(BASE_DIR + "/env.json") as env_json:
        ENV = json.load(env_json)
ENV.update(os.environ)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

SECRET_KEY = ENV.get("SECRET_KEY", "&-)aly8rq=l8-7193rj0e@p$tp571+q5&g0jyi8#)u!rt-!=b8")
DEBUG = to_bool(ENV.get("DEBUG", "True"))
if DEBUG:
    INTERNAL_IPS = ["127.0.0.1"]

ALLOWED_HOSTS = ENV.get("ALLOWED_HOSTS", "localhost").split(",")


SITE_ID = 1

EMAIL_BACKEND = ENV.get("email_backend", "django.core.mail.backends.smtp.EmailBackend")

PAYMENT_PROCESS = ENV.get("payment_process", "not set")
STRIPE_SECRET_KEY = ENV.get("STRIPE_SECRET_KEY", "fake")
STRIPE_PUBLISHABLE_KEY = ENV.get("STRIPE_PUBLISHABLE_KEY", "fake")

TICKET_EMAIL_FROM_ADDRESS = "biljett@karspexet.se"

try:
    with open(BASE_DIR + "/RELEASE.txt") as f:
        RELEASE = f.read()
except FileNotFoundError:
    RELEASE = ""

sentry_sdk.init(
    dsn=ENV.get("sentry_dsn"),
    release=RELEASE,
    integrations=[
        DjangoIntegration(),
        # Capture info and above as breadcrumbs, send errors as events
        LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
    ],
)

# Application definition

OUR_APPS = [
    "karspexet.show",
    "karspexet.ticket",
    "karspexet.venue",
]

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "djangocms_admin_style",
    "djangocms_text_ckeditor",
    "djangocms_picture",
    "djangocms_link",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.postgres",
    "cms",
    "menus",
    "treebeard",
    "sekizai",
    "filer",
    "easy_thumbnails",
    "mptt",
    "django_assets",
    "svg",
] + OUR_APPS

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "cms.middleware.utils.ApphookReloadMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
]

APPEND_SLASH = True

ROOT_URLCONF = "karspexet.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["karspexet/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai",
                "cms.context_processors.cms_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "karspexet.wsgi.application"


# Database
DATABASE_URL = ENV.get("DATABASE_URL", "postgres://karspexet@127.0.0.1/karspexet")
DATABASES = {
    "default": dj_database_url.config(default=DATABASE_URL),
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Security
CSRF_COOKIE_HTTPONLY = True
if to_bool(ENV.get("HTTPS", "False")):
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "SAMEORIGIN"


# Internationalization
LANGUAGES = [
    ("sv", "Swedish"),
]
LANGUAGE_CODE = "sv"
TIME_ZONE = "Europe/Stockholm"
USE_I18N = True
USE_L10N = True
USE_TZ = True

DATE_FORMAT = "Y-m-d"
DATETIME_FORMAT = "c"
SHORT_DATE_FORMAT = "Y-m-d"
SHORT_DATETIME_FORMAT = "Y-m-d H-i-s"


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
MEDIA_URL = "/uploads/"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django_assets.finders.AssetsFinder",
]

STATIC_ROOT = os.path.abspath("./staticfiles")
MEDIA_ROOT = os.path.abspath("./uploads")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "assets"),
]

ASSETS_MODULES = ["karspexet.assets"]
ASSETS_DEBUG = DEBUG
ASSETS_ROOT = "assets"
ASSETS_AUTO_BUILD = ASSETS_DEBUG
ASSETS_URL_EXPIRE = True
SLIMIT_MANGLE = not ASSETS_DEBUG
SLIMIT_MANGLE_TOPLEVEL = not ASSETS_DEBUG

THUMBNAIL_HIGH_RESOLUTION = True

THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    "filer.thumbnail_processors.scale_and_crop_with_subject_location",
    "easy_thumbnails.processors.filters",
)


MEDIA_FILER_LOC = os.path.join(MEDIA_ROOT, "filer_public/uploads/")
MEDIA_FILER_ROOT = os.path.join(MEDIA_ROOT, "filer_public/uploads/")
MEDIA_FILER_URL = urljoin(MEDIA_URL, "filer_public/")

MEDIA_THUMBS_LOC = os.path.join(MEDIA_ROOT, "filer_public_thumbnails/uploads/")
MEDIA_THUMBS_ROOT = os.path.join(MEDIA_ROOT, "filer_public_thumbnails/uploads/filer_public_thumbnails/")
MEDIA_THUMBS_URL = urljoin(MEDIA_URL, "filer_public_thumbnails/")

FILER_STORAGES = {
    "public": {
        "main": {
            "ENGINE": "filer.storage.PublicFileSystemStorage",
            "OPTIONS": {
                "location": MEDIA_FILER_LOC,
                "base_url": "/uploads/filer_public/",
            },
            "UPLOAD_TO": "filer.utils.generate_filename.randomized",
            "UPLOAD_TO_PREFIX": "",
        },
        "thumbnails": {
            "ENGINE": "filer.storage.PublicFileSystemStorage",
            "OPTIONS": {
                "location": MEDIA_THUMBS_LOC,
                "base_url": "/uploads/",
            },
            "UPLOAD_TO_PREFIX": "",
        },
    }
}

CMS_TEMPLATES = [
    ("home.html", "Home page template"),
    ("about.html", "Content page template"),
    ("content_with_hero_image.html", "Content page template with hero image"),
]
CMS_PLACEHOLDER_CONF = {
    None: {
        "plugins": ["TextPlugin", "LinkPlugin", "PicturePlugin"],
        "excluded_plugins": ["InheritPlugin"],
    },
    "image": {
        "plugins": ["PicturePlugin"],
        "name": "Image",
        "language_fallback": True,
        "default_plugins": [
            {
                "plugin_type": "TextPlugin",
                "values": {
                    "body": "<p>Lorem ipsum dolor sit amet...</p>",
                },
            },
        ],
    },
    "home.html hero_image": {
        "inherit": "image",
        "name": "Hero Image",
    },
    "home.html card_1_image": {
        "inherit": "image",
        "name": "Card 1 Image",
    },
    "home.html card_2_image": {
        "inherit": "image",
        "name": "Card 2 Image",
    },
    "home.html card_3_image": {
        "inherit": "image",
        "name": "Card 3 Image",
    },
    "home.html sponsor_images": {
        "inherit": "image",
        "name": "Sponsor Images",
    },
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["stdout"]},
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%H:%M:%S",
        },
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[%(asctime)s] %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "null": {"class": "logging.NullHandler"},
        "stdout": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
        },
        "django.server": {
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
    },
    "loggers": {
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
        },
    },
}
