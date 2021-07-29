import os

from flask import jsonify
import sentry_sdk

from app import create_app

sentry_sdk.init(
    "https://6f0e6c17ccec41d6a58229df1c34b807@o828822.ingest.sentry.io/5883947",
    server_name="auth-api",
    traces_sample_rate=1.0
)
app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.route('/health-check', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200


def main():
    app.run(host="0.0.0.0", port="5000")


if __name__ == '__main__':
    main()
