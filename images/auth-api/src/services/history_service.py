import datetime

import models
from db import db
from exceptions import UnknownDevice

from . import DeviceService, UserService


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

