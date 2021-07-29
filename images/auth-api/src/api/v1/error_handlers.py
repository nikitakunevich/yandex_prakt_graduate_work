from authlib.jose.errors import ExpiredTokenError
from marshmallow.exceptions import ValidationError
from flask import jsonify, url_for
from werkzeug.exceptions import BadRequest

from services import DeviceAlreadyExists
from services import RoleAlreadyExists
from services import InvalidEmail
from services import InvalidRefreshToken
from services import UnknownDevice
from services import UnknownUser


from . import router


@router.errorhandler(ExpiredTokenError)
def handle_bad_request(e):
    return {'error': 'expired oauth token', 'auth_url': url_for('router.social_auth', backend='google')}


@router.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({'error': e.description}), e.code


@router.errorhandler(ValidationError)
def handle_validation_error(e):
    return {'error': e.messages}, 400


@router.errorhandler(InvalidRefreshToken)
def handle_invalid_refresh_token(e):
    return {'error': 'invalid refresh token'}, 422


@router.errorhandler(UnknownDevice)
def handle_unknown_device(e):
    return {'error': 'unknown device'}, 422


@router.errorhandler(DeviceAlreadyExists)
def handle_device_already_exists(e):
    return {'error': 'the device has been already activated'}, 422


@router.errorhandler(RoleAlreadyExists)
def handle_role_already_exists(e):
    return {'error': 'role already exists'}, 422


@router.errorhandler(InvalidEmail)
def handle_invalid_email(e):
    return {'error': 'invalid email'}, 422


@router.errorhandler(UnknownUser)
def handle_unknown_user(e):
    return {'error': 'unknown user'}, 422

