import datetime

from flask_jwt_extended import create_access_token, create_refresh_token

from cache import redis_db
from exceptions import InvalidEmail, InvalidRefreshToken, UnknownDevice

from . import RoleService, UserService


class TokenService:

    @staticmethod
    def create_root_token():
        return create_access_token(identity='root',
                                   expires_delta=datetime.timedelta(hours=1),
                                   fresh=True)

    @staticmethod
    def create_token_pair(email, device_id):
        user = UserService.get_user_by_email(email)
        if not user:
            raise InvalidEmail

        user_roles = ','.join([role.role_name for role in RoleService.get_user_roles(email)])

        if user_roles:
            access_token = create_access_token(identity=user.email,
                                               additional_claims={'prm': user.is_premium,
                                                                  'roles': user_roles},
                                               fresh=True)
        else:
            access_token = create_access_token(identity=user.email,
                                               additional_claims={'prm': user.is_premium,
                                                                  'roles': ''},
                                               fresh=True)
        refresh_token = create_refresh_token(identity=user.email)

        redis_db.setex(device_id, 60 * 60 * 24 * 30, refresh_token)

        return access_token, refresh_token

    @classmethod
    def refresh_token_pair(cls, email, device_id, refresh_token):
        stored_refresh_token = redis_db.get(device_id)

        if stored_refresh_token and stored_refresh_token == refresh_token:
            access_token, refresh_token = cls.create_token_pair(email, device_id)
            return access_token, refresh_token
        else:
            raise InvalidRefreshToken

    @staticmethod
    def remove_refresh_token(email, device_id):
        user = UserService.get_user_by_email(email)
        for device in user.devices:
            if str(device.id) == device_id:
                redis_db.delete(device_id)
                return
        raise UnknownDevice

    @staticmethod
    def remove_all_refresh_tokens(email):
        user = UserService.get_user_by_email(email)
        for device in user.devices:
            redis_db.delete(str(device.id))

