# noinspection PyUnresolvedReferences
import os

from config.settings.base import *

ALLOWED_HOSTS = ['*']

SENTRY_URL = os.environ.get('SENTRY_URL', None)
