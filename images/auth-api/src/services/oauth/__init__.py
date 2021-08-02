from authlib.integrations.flask_client import OAuth

from main import app

oauth = OAuth(app)

from .google_provider import GoogleProvider
from .oauth_service import OAuthService
