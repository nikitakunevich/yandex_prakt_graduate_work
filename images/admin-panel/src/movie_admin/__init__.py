from django.conf import settings
import sentry_sdk


def startup():
    sentry_sdk.init(
        settings.SENTRY_URL,
        server_name="admin-panel",
        traces_sample_rate=1.0
    )


startup()
