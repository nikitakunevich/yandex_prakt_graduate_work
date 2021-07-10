import random
import string
import json

from urllib.parse import urlencode
from urllib.request import urlopen

from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

import schemas
from . import router

from services import UserService
from services import DeviceService
from services import TokenService
from services import HistoryService
from services import OAuthService

from main import app


@router.route('/social_auth/auth/<string:backend>')
def social_auth(backend):
    provider = OAuthService.get_provider(backend)
    return provider.get_redirect()


@router.route('/social_auth/callback/<string:backend>')
def social_callback(backend):
    provider = OAuthService.get_provider(backend)
    return {'id_token': provider.get_user_id_token()}


@router.route('/social_auth/login/<string:backend>', methods=['POST'])
def social_login(backend):
    user_data = request.json
    schemas.IdTokenAuthSchema().load(user_data)

    provider = OAuthService.get_provider(backend)
    user_info = provider.get_user_info(user_data['id_token'])

    device_id = user_data.get('device_id', None)
    if device_id:
        if DeviceService.is_device_registered(email=user_info['email'], device_id=device_id):
            access_token, refresh_token = TokenService.create_token_pair(user_info['email'], device_id)
            HistoryService.add_history_record(device_id)
            return {'access_token': access_token, 'refresh_token': refresh_token}, 200
        else:
            return {'error': 'Unknown device'}, 400

    device_id, device_auth_id = DeviceService.create_device_auth_request(user_info['email'])
    return {'device_id': device_id, 'device_auth_id': device_auth_id}, 200


def password_generator(length):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase +
                                                string.ascii_lowercase +
                                                string.digits +
                                                '~!@#$%^&*()/<>_-+=?.,') for _ in range(length))


@router.route('/social_auth/register/<string:backend>', methods=['POST'])
def social_register(backend):
    user_data = request.json
    schemas.IdTokenAuthSchema().load(user_data)

    provider = OAuthService.get_provider(backend)
    user_info = provider.get_user_info(user_data['id_token'])

    email = user_info.get('email')
    first_name = user_info.get('given_name')
    last_name = user_info.get('family_name')
    password = password_generator(128)

    UserService.create_user(email=email,
                            first_name=first_name,
                            last_name=last_name,
                            password=password)

    return {'error': 'no error', 'detail': 'Account created successfully'}, 201


@router.route('/root_login', methods=['POST'])
def root_login():
    user_data = request.json
    schemas.RootPasswordSchema().load(user_data)

    if user_data['root_password'] == app.config['ROOT_PASSWORD']:
        return {'root_access_token': TokenService.create_root_token()}
    else:
        return {'error': 'Wrong username or password'}, 401


@router.route('/login', methods=['POST'])
def login():
    user_data = request.json

    is_smarttv = False
    user_agent = request.headers.get('User-Agent')
    smarttvs = 'smart-tv|smarttv|googletv|appletv|hbbtv|pov_tv|netcast.tv'.split('|')

    for tv in smarttvs:
        if tv in user_agent:
            is_smarttv = True

    # Google re-captcha v2
    if is_smarttv:
        uri_recaptcha = 'https://www.google.com/recaptcha/api/siteverify'
        recaptcha_response = user_data.get('recaptcha_response', None)
        private_recaptcha = app.config['GOOGLE_RECAPTCHA_SECRET_KEY']
        params = urlencode({
            'secret': private_recaptcha,
            'response': recaptcha_response,
        })

        data = urlopen(uri_recaptcha, params.encode('utf-8')).read()
        result = json.loads(data)
        success = result.get('success', None)

        if not success:
            return {'error': 'Invalid re-captcha validation. This site is for humans only'}

    schemas.UserAuthInfoSchema().load(user_data)
    is_password_correct = UserService.check_user_password(user_data['email'], user_data['password'])
    email = user_data['email']

    if not is_password_correct:
        return {'error': 'Wrong username or password'}, 401

    device_id = user_data.get('device_id', None)
    if device_id:
        if DeviceService.is_device_registered(email=email, device_id=device_id):
            access_token, refresh_token = TokenService.create_token_pair(email, device_id)
            HistoryService.add_history_record(device_id)
            return {'access_token': access_token, 'refresh_token': refresh_token}, 200
        else:
            return {'error': 'Unknown device'}, 400

    device_id, device_auth_id = DeviceService.create_device_auth_request(email)
    return {'device_id': device_id, 'device_auth_id': device_auth_id}, 200


@router.route('/register', methods=['POST'])
def create_account():
    user_data = request.json

    schemas.UserSchema().load(user_data)
    email = user_data.get('email')
    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')
    password = user_data.get('password')

    UserService.create_user(email=email, first_name=first_name, last_name=last_name, password=password)
    return {'error': 'no error', 'detail': 'Account created successfully'}, 201


@router.route('/authorize_device/<uuid:device_auth_id>', methods=['GET'])
def authorize_device(device_auth_id):
    DeviceService.authorize_device(device_auth_id)
    return {'msg': 'device activated'}, 200


@router.route('/refresh', methods=['POST'])
def refresh():
    user_data = request.json
    schemas.RefreshTokenSchema().load(user_data)
    access_token, refresh_token = TokenService.refresh_token_pair(
        user_data['email'],
        user_data['device_id'],
        user_data['refresh_token']
    )
    return {'access_token': access_token, 'refresh_token': refresh_token}, 200


@router.route('/logout', methods=['POST'])
@jwt_required(fresh=True)
def logout():
    user_data = request.json
    schemas.DeviceIdSchema().load(user_data)
    email = get_jwt_identity()
    TokenService.remove_refresh_token(email, user_data['device_id'])
    return {'error': 'no error'}, 200


@router.route('/logout_all', methods=['POST'])
@jwt_required(fresh=True)
def logout_all():
    email = get_jwt_identity()
    TokenService.remove_all_refresh_tokens(email)
    return {'error': 'no error'}, 200

