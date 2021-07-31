from flask import url_for

from services import UserService

from . import oauth


class GoogleProvider:

    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    @classmethod
    def get_redirect(cls):
        redirect_uri = url_for('router.social_callback', _external=True, backend='google')
        return oauth.google.authorize_redirect(redirect_uri)

    @staticmethod
    def get_user_id_token():
        token = oauth.google.authorize_access_token()
        return {'id_token': token['id_token']}

    @staticmethod
    def get_user_info(token):
        claims = UserService.get_google_token_claims(token)
        email = claims.get('email')
        first_name = claims.get('given_name')
        last_name = claims.get('family_name')
        return {'email': email, 'first_name': first_name, 'last_name': last_name}
