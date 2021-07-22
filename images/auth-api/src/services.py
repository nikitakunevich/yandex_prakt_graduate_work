import datetime
import requests
import uuid

from authlib.oidc.core import CodeIDToken
from authlib.jose import jwt

from flask import url_for
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash

import models
from cache import redis_db
from db import db

from authlib.integrations.flask_client import OAuth

from main import app

oauth = OAuth(app)


class InvalidEmail(Exception):
    pass


class UnknownUser(Exception):
    pass


class UnknownRole(Exception):
    pass


class InvalidRefreshToken(Exception):
    pass


class UnknownDevice(Exception):
    pass


class DeviceAlreadyExists(Exception):
    pass


class RoleAlreadyExists(Exception):
    pass


class UserService:
    def __init__(self):
        pass

    @staticmethod
    def get_google_token_claims(id_token):
        keys = requests.get('https://www.googleapis.com/oauth2/v3/certs').json()
        claims = jwt.decode(id_token, keys, claims_cls=CodeIDToken)
        claims.validate()
        return claims

    @staticmethod
    def get_user_by_email(email):
        user = models.User.query.filter_by(email=email).first()
        if not user:
            raise UnknownUser
        return user

    @staticmethod
    def get_user_by_id(user_id):
        user = models.User.query.filter_by(id=user_id).first()
        if not user:
            raise UnknownUser
        return user

    @staticmethod
    def create_user(email, first_name, last_name, password):
        user = models.User(email=email, password=password, first_name=first_name, last_name=last_name)
        user.password = generate_password_hash(user.password, method='pbkdf2:sha256:5', salt_length=8)
        db.session.add(user)
        db.session.commit()

    @classmethod
    def update_user(cls, user_id, **user_new_data):
        user = cls.get_user_by_id(user_id)

        for key in user_new_data:
            if key == 'password':
                setattr(user, key, generate_password_hash(user_new_data[key], method='pbkdf2:sha256:5', salt_length=8))
            elif key not in ['id', 'is_premium']:
                setattr(user, key, user_new_data[key])
            else:
                raise Exception('insufficient privileges')
        db.session.add(user)
        db.session.commit()

    def delete_user(self):
        pass

    @classmethod
    def check_user_password(cls, email, plaintext_password):
        user = cls.get_user_by_email(email)
        if user:
            return check_password_hash(user.password, plaintext_password)
        return False


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

        user_roles = RoleService.get_user_roles(email)

        if user_roles:
            access_token = create_access_token(identity=user.email,
                                               additional_claims={'prm': user.is_premium,
                                                                  'roles': user_roles},
                                               fresh=True)
        else:
            access_token = create_access_token(identity=user.email,
                                               additional_claims={'prm': user.is_premium},
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


class DeviceService:
    def __init__(self):
        pass

    @staticmethod
    def get_device_by_id(device_id):
        device = models.Device.query.filter_by(id=uuid.UUID(device_id)).first()
        if not device:
            raise UnknownDevice
        return device

    @staticmethod
    def create_device_auth_request(email) -> (str, str):
        device_id = str(uuid.uuid4())
        device_auth_id = str(uuid.uuid4())

        data = {
                'email': email,
                'device_id': device_id
        }

        redis_db.hset(name=device_auth_id, mapping=data)
        redis_db.expire(name=device_auth_id, time=60 * 60 * 3)

        return device_id, device_auth_id

    @staticmethod
    def is_device_registered(email, device_id):
        user = UserService.get_user_by_email(email)
        registered_devices = user.devices
        for device in registered_devices:
            if device_id == str(device.id):
                return True
        return False

    @staticmethod
    def authorize_device(device_auth_id):
        device_data = redis_db.hgetall(str(device_auth_id))

        if not device_data:
            raise UnknownDevice

        email = device_data['email']
        device_id = device_data['device_id']

        user = UserService.get_user_by_email(email)
        user_devices = user.devices

        for user_device in user_devices:
            if str(user_device.id) == device_id:
                raise DeviceAlreadyExists

        device = models.Device(id=device_id, user_id=user.id)
        db.session.add(device)
        db.session.commit()

    @classmethod
    def delete_device(cls, device_id):
        device = cls.get_device_by_id(device_id)
        if device:
            db.session.delete(device)
            db.session.commit()
        else:
            raise UnknownDevice


class HistoryService:

    @staticmethod
    def add_history_record(device_id):
        device = DeviceService.get_device_by_id(device_id)
        if not device:
            raise UnknownDevice
        user_id = device.user_id
        login_date = datetime.datetime.utcnow()
        history_record = models.LoginHistoryRecord(user_id=user_id, device_id=device_id, login_date=login_date)
        db.session.add(history_record)
        db.session.commit()

    @staticmethod
    def get_history(email, start_date, end_date):
        user_id = UserService.get_user_by_email(email).id
        records = db.session.query(models.LoginHistoryRecord).filter(
            models.LoginHistoryRecord.user_id == user_id).filter(
            models.LoginHistoryRecord.login_date >= start_date).filter(models.LoginHistoryRecord.login_date <= end_date)
        result = []
        for record in records:
            result.append(
                {
                    'device_id': str(record.device_id),
                    'login_date': str(record.login_date)
                }
            )

        return result


class RoleService:

    @staticmethod
    def get_role_by_id(role_id):
        role = models.Role.query.filter_by(id=role_id).first()
        if not role:
            raise UnknownRole
        return role

    @staticmethod
    def get_role_by_name(role_name):
        role = models.Role.query.filter_by(role_name=role_name).first()
        return role

    @staticmethod
    def create_role(role_name):
        if RoleService.get_role_by_name(role_name):
            raise RoleAlreadyExists
        role = models.Role(role_name=role_name)
        db.session.add(role)
        db.session.commit()

    @staticmethod
    def delete_role(role_name):
        models.Role.query.filter_by(role_name=role_name).delete()
        db.session.commit()

    @staticmethod
    def add_user_role(email, role_name):
        user = UserService.get_user_by_email(email)
        role = RoleService.get_role_by_name(role_name)
        user.roles.append(role)
        db.session.commit()

    @staticmethod
    def delete_user_role(email, role_name):
        user = UserService.get_user_by_email(email)
        role = RoleService.get_role_by_name(role_name)
        user.roles.remove(role)
        db.session.commit()

    @staticmethod
    def get_user_roles(email):
        user = UserService.get_user_by_email(email)
        return [role for role in user.roles]


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


class OAuthService:
    providers = {
        'google': GoogleProvider
    }

    @classmethod
    def get_provider(cls, provider_name):
        return cls.providers[provider_name]
