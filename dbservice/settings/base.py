import json
import os
import sys

from django.conf.global_settings import *  # noqa
from django.core.exceptions import ImproperlyConfigured
from unipath import Path
import dbservice as project_module


"""Base settings shared by all environments"""

# =============================================================================
# Generic Django project settings
# =============================================================================

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# SITE_ID = 1
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'UTC'
USE_TZ = False
USE_I18N = False
USE_L10N = False
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', 'English'),
)
# based on Django REST Framework interpretation of ISO 8601
DATE_INPUT_FORMATS = (
    '%Y',        # '2006'
    '%Y-%m',     # '2006-10'
    '%Y-%m-%d',  # '2006-10-25'
)
TIME_INPUT_FORMATS = (
    '%H:%M',        # '14:30'
    '%H:%M:%S',     # '14:30:59'
    '%H:%M:%S.%f',  # '14:30:59.000200'
)
DATETIME_INPUT_FORMATS = (
    '%Y%m%dT%H:%M:%S.%f',    # '20061025T14:30:59.000200'
    '%Y%m%dT%H:%M:%S',       # '20061025T14:30:59'
    '%Y%m%dT%H:%M',          # '20061025T14:30'
    '%Y%m%dT%H',             # '20061025T14'
    '%Y%m%d',                # '20061025'
    '%Y-%m-%dT%H:%M:%S.%f',  # '2006-10-25T14:30:59.00200'
    '%Y-%m-%dT%H:%M:%S',     # '2006-10-25T14:30:59'
    '%Y-%m-%dT%H:%M',        # '2006-10-25T14:30'
    '%Y-%m-%dT%H',           # '2006-10-25T14'
    '%Y-%m-%d',              # '2006-10-25'
    '%m/%d/%YT%H:%M:%S.%f',  # '10/25/2006T14:30:59.000200'
    '%m/%d/%YT%H:%M:%S',     # '10/25/2006T14:30:59'
    '%m/%d/%YT%H:%M',        # '10/25/2006T14:30'
    '%m/%d/%YT%H',           # '10/25/2006T14'
    '%m/%d/%Y',              # '10/25/2006'
    '%m/%d/%yT%H:%M:%S.%f',  # '10/25/06T14:30:59.000200'
    '%m/%d/%yT%H:%M:%S',     # '10/25/06T14:30:59'
    '%m/%d/%yT%H:%M',        # '10/25/06T14:30'
    '%m/%d/%yT%H',           # '10/25/06T14'
    '%m/%d/%y',              # '10/25/06'
)

INSTALLED_APPS = (
    'dbservice.apps.users',
    'dbservice.apps.private',
    'dbservice.apps.homes',

    'rest_framework',
    'rest_framework_jwt',
    'django_filters',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # 'django.contrib.admindocs',
)

# =============================================================================
# Calculation of directories relative to the project module location
# =============================================================================

PROJECT_DIR = os.path.dirname(os.path.realpath(project_module.__file__))

LOGS_DIR = os.path.join(PROJECT_DIR, os.pardir, 'logs')
PYTHON_BIN = os.path.dirname(sys.executable)
VE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(PROJECT_DIR)))
# Assume that the presence of 'activate_this.py' in the python bin/
# directory means that we're running in a virtual environment.
if os.path.exists(os.path.join(PYTHON_BIN, 'activate_this.py')):
    # We're running with a virtualenv python executable.
    VAR_ROOT = os.path.join(os.path.dirname(PYTHON_BIN), 'var')
elif VE_PATH and os.path.exists(os.path.join(VE_PATH, 'bin',
                                             'activate_this.py')):
    # We're running in [virtualenv_root]/src/[project_name].
    VAR_ROOT = os.path.join(VE_PATH, 'var')
else:
    # Set the variable root to a path in the project which is
    # ignored by the repository.
    VAR_ROOT = os.path.join(PROJECT_DIR, 'var')

if not os.path.exists(VAR_ROOT):
    os.mkdir(VAR_ROOT)

if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)

# =============================================================================
# Logging
# =============================================================================
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'simple_sql': {
            'format': '[%(asctime)s] duration(sec): %(duration).6f|sql: %(sql)s|params: %(params)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'general_debug.log'),
            'formatter': 'verbose'
        },
        'file_database': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple_sql',
            'filename': os.path.join(LOGS_DIR, 'debug_database.log'),
            'level': 'DEBUG',
            'maxBytes': 1024 * 1000 * 10,
            'backupCount': 3
        },
        'email_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['email_admins'],
            'level': 'ERROR',
            'propogate': True
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console', 'email_admins', 'file'],
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['file_database'],
            'propagate': False,
        }
    }
}
import logging.config
logging.config.dictConfig(LOGGING)

# =============================================================================
# Project URLS and media settings
# =============================================================================

ROOT_URLCONF = 'dbservice.urls'

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'

STATIC_URL = '/static/'
MEDIA_URL = '/uploads/'

STATIC_ROOT = os.path.join(VAR_ROOT, 'static')
MEDIA_ROOT = os.path.join(VAR_ROOT, 'uploads')

STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'static'),
)

# =============================================================================
# Templates
# =============================================================================

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
)

# =============================================================================
# Middleware
# =============================================================================

MIDDLEWARE_CLASSES += (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)


# =============================================================================
# Auth / security
# =============================================================================

AUTHENTICATION_BACKENDS += (
)

# =============================================================================
# Miscellaneous project settings
# =============================================================================

AUTH_USER_MODEL = 'users.User'

# =============================================================================
# Third party app settings
# =============================================================================

REST_FRAMEWORK = {
    'FILTER_BACKEND': 'rest_framework.filters.DjangoFilterBackend',
    'PAGINATE_BY': 20,
    'PAGINATE_BY_PARAM': 'page_size',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'measurements': '100/minute',
        'user': '10000/minute',
    }
}


JWT_AUTH = {
    # To simplify things we turn off token expiration. We can turn this on and
    # write token refresh mechanisms later.
    'JWT_VERIFY_EXPIRATION': False,
}


# SECRETS ##############################
_secrets = None
_secrets_filename = Path('~', 'dbservice.json').expand()


def _load_secrets():
    global _secrets
    if os.path.exists(_secrets_filename):
        try:
            with open(_secrets_filename) as f:
                _secrets = json.load(f)
        except ValueError:
            error_msg = 'Failed to parse JSON in {0}.'.format(
                _secrets_filename)
            raise ImproperlyConfigured(error_msg)
    else:
        error_msg = 'Missing secrets configuration file {0}.'.format(
            _secrets_filename)
        raise ImproperlyConfigured(error_msg)


def get_secret(setting):
    if _secrets is None:
        _load_secrets()
    try:
        return _secrets[setting]
    except KeyError:
        error_msg = 'Set {0} in secrets configuration file {0}.'.format(
            setting, _secrets_filename)
        raise ImproperlyConfigured(error_msg)
