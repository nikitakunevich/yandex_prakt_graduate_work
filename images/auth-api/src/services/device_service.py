import uuid

import models
from cache import redis_db
from db import db
from exceptions import DeviceAlreadyExists, UnknownDevice

from . import UserService


class DeviceService:

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
        if user.devices.filter_by(id=device_id).exists():
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

        if user.devices.filter_by(id=device_id).exists():
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

