import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

jwt_access_token_expires_minutes = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_MINUTES')) if \
    os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_MINUTES') else 5

jwt_refresh_token_expires_days = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES_DAYS')) if \
    os.environ.get('JWT_REFRESH_TOKEN_EXPIRES_DAYS') else 30


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = os.environ.get('REDIS_HOST')
    REDIS_PORT = int(os.environ.get('REDIS_PORT'))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=jwt_access_token_expires_minutes)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=jwt_refresh_token_expires_days)
    JWT_PUBLIC_KEY = os.environ.get('JWT_PUBLIC_KEY')
    JWT_PRIVATE_KEY = os.environ.get('JWT_PRIVATE_KEY')
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'RS256')
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', None)
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', None)
    # Google re-captcha v2
    GOOGLE_RECAPTCHA_SECRET_KEY = os.environ.get('GOOGLE_RECAPTCHA_SECRET_KEY', None)
    # Root account settings
    ROOT_PASSWORD = os.environ.get('ROOT_PASSWORD', 'change_me')
    ROOT_SESSION_HOURS = int(os.environ.get('ROOT_SESSION_HOURS')) if \
        os.environ.get('ROOT_SESSION_HOURS') else 1

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'postgresql://postgres:oracle@localhost/postgres'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:oracle@localhost/postgres'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
