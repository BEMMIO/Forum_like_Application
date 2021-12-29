import re
import os
from pathlib import Path
from decouple import config as env,Csv

from django.urls import reverse, reverse_lazy
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_ROOT = BASE_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "SECRET_KEY",
    default="fOqtAorZrVqWYbuMPOcZnTzw2D5bKeHGpXUwCaNBnvFUmO1njCQZGz05x1BhDG0E",
)

# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env('DEBUG', default=True, cast=bool)

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env('ALLOWED_HOSTS', cast=Csv())


# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL regex.
ADMIN_URL = env('ADMIN_URL',default=r"^admin/")
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ('admin', 'admin@example.com'), ('admin2', 'admin2@example.com'),
]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    # crispy-forms 
    'crispy_forms',
    # taggit
    'taggit',
    # active-link
    'active_link',
    # capture
    'captcha',
]

LOCAL_APPS = [
    # user app.
    'dev.users.apps.UsersConfig',
    'dev.accounts.apps.AccountsConfig',
    # projects apps.
    'dev.core.apps.CoreConfig',
    'dev.blog.apps.BlogConfig',
    'dev.search.apps.SearchConfig',
    'dev.pages.apps.PagesConfig',
    'dev.blog.like.apps.LikeConfig',
    'dev.invitation.apps.InvitationConfig',
    'dev.blog.comments.apps.CommentsConfig',

]

# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # project middlewares
    'dev.users.middleware.OnlineTrackerMiddleware',
    # 'dev.users.middleware.RestrictViewsToAnonymousUsersMiddleware', #uncomment in production.
]


# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATE_DIR = os.path.join(PROJECT_ROOT,'templates')
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [TEMPLATE_DIR],
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            "debug": True,
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                # project_related context-processors
                "dev.core.context_processors.site_informations",
                "dev.core.context_processors.authenticated_user_data",
            ],
        },
    }
]

# https://www.postgresqltutorial.com/connect-to-postgresql-database/

DATABASES = {

    'default': {

        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': 'dev_blog_db',

        'USER': 'postgres',

        'PASSWORD': 'admin123',

        'HOST': 'localhost',

        'PORT': 5432,

    }

}

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
# http://mtweb.cs.ucl.ac.uk/mus/arabidopsis/xiang/software/src.Django-1.6.1/docs/topics/cache.txt

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'wger-cache',
        'TIMEOUT': 30 * 24 * 60 * 60,  # Cache for a month
    }
}

CACHE_TTL = 60 * 3 # 60sec * 3 = 3 min

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         },
#         "KEY_PREFIX": "example"
#     }
# }

# # Cache time to live is 3 minutes.
# CACHE_TTL = 60 * 3

# Logging
# See http://docs.python.org/library/logging.config.html
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "simple": {"format": "[%(name)s] %(levelname)s: %(message)s"},
        "full": {"format": "%(asctime)s [%(name)s] %(levelname)s: %(message)s"},
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
    },
    "loggers": {
        "django.request": {
            "handlers": [],
            "level": "ERROR",
            "propagate": False,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}


# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend

EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = 'smtp.gmail.com' 
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 587
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = 'edd.edwardmike@gmail.com'
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = 'qhzlydpqmqdrbeky'
# https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True
# https://docs.djangoproject.com/en/dev/ref/settings/#email-use-ssl
EMAIL_USE_SSL = False
# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend", # django's default
    "dev.accounts.auth_backend.DevBackend", 
]

#https://stackoverflow.com/questions/45961459/
#multiple-authentication-backends-configured-and-therefore-must-provide-the-back
BACKEND_AUTH = AUTHENTICATION_BACKENDS[0]

# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "blog:article-lists"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "accounts:login"
# # https://docs.djangoproject.com/en/dev/ref/settings/#logout-redirect-url
LOGOUT_REDIRECT_URL = 'accounts:login'
# # https://docs.djangoproject.com/en/dev/ref/settings/#logout-url
LOGOUT_URL = 'accounts:logout'


# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    'OPTIONS':{"user_attributes": ["username", "email"]}
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    'OPTIONS':{'min_length':7,}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

#
# Ignore these URLs if they cause 404
#
IGNORABLE_404_URLS = (re.compile(r'^/favicon\.ico$'), )

# GENERAL
# ------------------------------------------------------------------------------
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Europe/London"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True


# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = os.path.join(PROJECT_ROOT,'staticfiles')
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [os.path.join(PROJECT_ROOT,'static')]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = os.path.join(PROJECT_ROOT,'media')
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# DJANGO-DEBUG-TOOLBAR
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
if DEBUG:
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
    INSTALLED_APPS += ["debug_toolbar"]
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
    }
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
    INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]


# DATE FORMAT
# https://docs.djangoproject.com/en/3.2/ref/settings/#date-format
DATE_INPUT_FORMATS = (
    "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%b %d %Y",
    "%b %d, %Y", "%d %b %Y", "%d %b, %Y", "%B %d %Y",
    "%B %d, %Y", "%d %B %Y", "%d %B, %Y"
)

# Store the user messages in the session
# https://docs.djangoproject.com/en/3.2/ref/contrib/messages/
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# MESSAGE FRAMEWORK
# https://docs.djangoproject.com/en/3.2/ref/contrib/messages/
MESSAGE_TAGS = {

        messages.DEBUG: 'secondary', # alert-secondary

        messages.INFO: 'info', # alert-info

        messages.SUCCESS: 'success', # alert-success

        messages.WARNING: 'warning', # alert-warning

        messages.ERROR: 'danger', # alert-danger
 }


# Your stuff.....
# ------------------------------------------------------------------------------
# Project name and domain
PROJECT_NAME = env('PROJECT_NAME')

PROJECT_DOMAIN = env('PROJECT_DOMAIN')

# Random avatar path
RANDOM_AVATAR_PATH = os.path.join(MEDIA_ROOT,'random_avatars') 

# Crispy-forms
# https://django-crispy-forms.readthedocs.io/
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Taggit
# https://django-taggit.readthedocs.io/en/latest/index.html
TAGGIT_CASE_INSENSITIVE = False 
 

# REDIS setup
# ------------------------------------------------------------------------------
REDIS_URL = 'redis://127.0.0.1:6379/'

# CELERY setup
# ------------------------------------------------------------------------------

CELERY_BROKER_URL = REDIS_URL

CELERY_RESULT_BACKEND = REDIS_URL

CELERY_ACCEPT_CONTENT = ['application/json']

CELERY_TASK_SERIALIZER = 'json'

CELERY_RESULT_SERIALIZER = 'json'

CELERY_TIMEZONE = TIME_ZONE

CELERY_TASK_ALWAYS_EAGER = not CELERY_BROKER_URL

CELERY_TASK_TIME_LIMIT = 5 * 60

CELERY_TASK_SOFT_TIME_LIMIT = 60


# Third Party Keys & Secrets

# Google Recapture
# ----------------------------------------------------------------------------
RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY")

RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY")

RECAPTCHA_REQUIRED_SCORE = env("RECAPTCHA_REQUIRED_SCORE",default=0.85,cast=float)