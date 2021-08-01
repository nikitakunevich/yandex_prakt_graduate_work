# noinspection PyUnresolvedReferences
import os

import sentry_sdk
from config.settings.base import *

ALLOWED_HOSTS = ['*']

SENTRY_URL = os.environ.get('SENTRY_URL', "https://6f0e6c17ccec41d6a58229df1c34b807@o828822.ingest.sentry.io/5883947")
sentry_sdk.init(
    SENTRY_URL,
    server_name="admin-panel",
    traces_sample_rate=1.0
)
