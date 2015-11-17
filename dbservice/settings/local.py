"""
Example settings for local development

Use this file as a base for your local development settings and copy
it to dbservice/settings/local.py. It should not be checked into
your code repository.

"""
from dbservice.settings.base import *   # pylint: disable=W0614,W0401

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Donald Duck', 'donald@duck.quack'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dbservice',
    }
}

INSTALLED_APPS += (
    'debug_toolbar',
    'django_extensions',
)

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE_CLASSES


# Debug toolbar:
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = '#ay18^-f)b#x2&s7p%&*vu#8&0htw@9@e0tw&=j+3@gz=hi%u*'