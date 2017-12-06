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

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "assets"),
    os.path.join(BASE_DIR, "filer_public"),
    os.path.join(BASE_DIR, "filer_public_thumbnails"),

]

WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": os.path.join(BASE_DIR, "webpack-stats.json"),
    }
}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&-)aly8rq=l8-7193rj0e@p$tp571+q5&g0jyi8#)u!rt-!=b8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


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
    'webpack_loader'
] + OUR_APPS

MIDDLEWARE_CLASSES = [
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


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

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

try:
    with open(BASE_DIR + "/env.json") as env_json:
        ENV = json.load(env_json)
except FileNotFoundError:
    import sys
    print("""
    ================================================================================
    No env.json settings file found.

    Try starting with the sample one:

    cp env.json.sample env.json
    """, file=sys.stderr)
    exit(1)

EMAIL_BACKEND = ENV.get("email_backend", 'django.core.mail.backends.smtp.EmailBackend')
PAYMENT_PROCESS = ENV.get("payment_process", "not set")
SITE_ID = 1
CMS_TEMPLATES = [
    ('home.html', 'Home page template'),
    ('about.html', 'Content page template'),
]
LANGUAGES = [
    ('en', 'English'),
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
                'location': 'filer_public',
                'base_url': '/static/',
            },
            'UPLOAD_TO': 'filer.utils.generate_filename.randomized',
            'UPLOAD_TO_PREFIX': 'filer_public',
        },
        'thumbnails': {
            'ENGINE': 'filer.storage.PublicFileSystemStorage',
            'OPTIONS': {
                'location': 'filer_public_thumbnails',
                'base_url': '/static/',
            },
        },
    }
}

CMS_PLACEHOLDER_CONF = {
    None: {
        "plugins": ['TextPlugin', 'LinkPlugin'],
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
                    'body':'<p>Lorem ipsum dolor sit amet...</p>',
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
    'release': raven.fetch_git_sha(os.path.abspath(os.path.dirname(os.path.dirname(__file__)))),
}
