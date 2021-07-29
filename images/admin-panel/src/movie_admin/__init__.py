import sentry_sdk


def startup():
    sentry_sdk.init(
        "https://6f0e6c17ccec41d6a58229df1c34b807@o828822.ingest.sentry.io/5883947",
        server_name="admin-panel",
        traces_sample_rate=1.0
    )


startup()
