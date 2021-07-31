import requests
from authlib.jose import jwt
from authlib.oidc.core import CodeIDToken
from werkzeug.security import check_password_hash, generate_password_hash

import models
from db import db
from exceptions import UnknownUser


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
