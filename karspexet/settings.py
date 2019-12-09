"""
Django settings for Karspexet project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import dj_database_url
import json
import raven

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    with open(BASE_DIR + "/env.json") as env_json:
        ENV = json.load(env_json)
except FileNotFoundError:
    import textwrap
    raise SystemExit(textwrap.dedent("""
    ================ ERROR ================
    ERROR: No env.json settings file found.

    Try starting with the sample one:

    cp env.json.sample env.json
    """))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV.get("SECRET_KEY", "&-)aly8rq=l8-7193rj0e@p$tp571+q5&g0jyi8#)u!rt-!=b8")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV.get("DEBUG", True)
if DEBUG:
    INTERNAL_IPS = ["127.0.0.1"]

ALLOWED_HOSTS = ENV.get("ALLOWED_HOSTS", [])


# Application definition

OUR_APPS = [
    'karspexet.show',
    'karspexet.ticket',
    'karspexet.venue',
    'cms',
    'menus',
    'treebeard',
    'sekizai',
    'filer',
    'easy_thumbnails',
    'mptt',
    'djangocms_text_ckeditor',
    'djangocms_picture',
    'djangocms_link',
]

INSTALLED_APPS = [
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.postgres',
    'raven.contrib.django.raven_compat',
    'svg',
    'django_assets',
] + OUR_APPS

MIDDLEWARE = [
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
]

APPEND_SLASH = True

ROOT_URLCONF = 'karspexet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['karspexet/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'karspexet.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(default='postgres://127.0.0.1/karspexet'),
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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

# Security
if ENV.get("HTTPS", False):
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'SAMEORIGIN'
    CSRF_COOKIE_HTTPONLY = True
    SECURE_SSL_REDIRECT = True


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'sv'

TIME_ZONE = 'Europe/Stockholm'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATE_FORMAT = "Y-m-d"

DATETIME_FORMAT = "c"

SHORT_DATE_FORMAT = "Y-m-d"

SHORT_DATETIME_FORMAT = "Y-m-d H-i-s"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django_assets.finders.AssetsFinder",
]

_static_path = lambda key, default: os.path.abspath(ENV.get(key, default))
MEDIA_ROOT = _static_path("MEDIA_ROOT", "./uploads")
STATIC_ROOT = _static_path("STATIC_ROOT", "./static_root")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "assets"),
    os.path.join(MEDIA_ROOT, "filer_public"),
    os.path.join(MEDIA_ROOT, "filer_public_thumbnails"),
]

EMAIL_BACKEND = ENV.get("email_backend", 'django.core.mail.backends.smtp.EmailBackend')
PAYMENT_PROCESS = ENV.get("payment_process", "not set")
SITE_ID = 1
CMS_TEMPLATES = [
    ('home.html', 'Home page template'),
    ('about.html', 'Content page template'),
    ('content_with_hero_image.html', 'Content page template with hero image'),
]
LANGUAGES = [
    ('sv', 'Swedish'),
]
THUMBNAIL_HIGH_RESOLUTION = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)

FILER_STORAGES = {
    'public': {
        'main': {
            'ENGINE': 'filer.storage.PublicFileSystemStorage',
            'OPTIONS': {
                'location': os.path.join(MEDIA_ROOT, 'filer_public/uploads'),
                'base_url': '/uploads',
            },
            'UPLOAD_TO': 'filer.utils.generate_filename.randomized',
            'UPLOAD_TO_PREFIX': '',
        },
        'thumbnails': {
            'ENGINE': 'filer.storage.PublicFileSystemStorage',
            'OPTIONS': {
                'location': os.path.join(MEDIA_ROOT, 'filer_public_thumbnails/uploads'),
                'base_url': '/uploads',
            },
            'UPLOAD_TO_PREFIX': '',
        },
    }
}

CMS_PLACEHOLDER_CONF = {
    None: {
        "plugins": ['TextPlugin', 'LinkPlugin', 'PicturePlugin'],
        'excluded_plugins': ['InheritPlugin'],
    },
    'image': {
        'plugins': ['PicturePlugin'],
        'name': "Image",
        'language_fallback': True,
        'default_plugins': [
            {
                'plugin_type': 'TextPlugin',
                'values': {
                    'body': '<p>Lorem ipsum dolor sit amet...</p>',
                },
            },
        ],
    },
    'home.html hero_image': {
        'inherit': 'image',
        'name': "Hero Image",
    },
    'home.html card_1_image': {
        'inherit': 'image',
        'name': "Card 1 Image",
    },
    'home.html card_2_image': {
        'inherit': 'image',
        'name': "Card 2 Image",
    },
    'home.html card_3_image': {
        'inherit': 'image',
        'name': "Card 3 Image",
    },
    'home.html sponsor_images': {
        'inherit': 'image',
        'name': "Sponsor Images",
    },
}

RAVEN_CONFIG = {
    'dsn': ENV.get('sentry_dsn'),
    'release': raven.fetch_git_sha(BASE_DIR),
}

WKHTMLTOPDF_PATH = ENV.get("wkhtmltopdf_path")

TICKET_EMAIL_FROM_ADDRESS = "biljett@karspexet.se"

ASSETS_MODULES = ["karspexet.assets"]
ASSETS_DEBUG = DEBUG
ASSETS_ROOT = "staticfiles"
ASSETS_AUTO_BUILD = ASSETS_DEBUG
ASSETS_URL_EXPIRE = True
SLIMIT_MANGLE = not ASSETS_DEBUG
SLIMIT_MANGLE_TOPLEVEL = not ASSETS_DEBUG

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
