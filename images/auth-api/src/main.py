import os
from flask import jsonify

from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.route('/health-check', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200


def main():
    app.run(host="0.0.0.0", port="5000")


if __name__ == '__main__':
    main()
