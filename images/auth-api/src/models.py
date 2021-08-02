import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship
from sqlalchemy.schema import UniqueConstraint

from db import db


def create_partition(target, connection, **kw):
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_smart" PARTITION OF "login_history" FOR VALUES IN ('smart')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_mobile" PARTITION OF "login_history" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_web" PARTITION OF "login_history" FOR VALUES IN ('web')"""
    )


class LoginHistoryRecord(db.Model):
    __tablename__ = 'login_history'
    __table_args__ = {
        'postgresql_partition_by': 'LIST (device_type)',
        'listeners': [('after_create', create_partition)],
    }
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    device_id = db.Column(UUID(as_uuid=True), db.ForeignKey('devices.id'), nullable=False)
    login_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    device_type = db.Column(db.String, primary_key=True, default='web', nullable=False)
    UniqueConstraint('id', 'device_type', name='id_device_type_pk')

    def __repr__(self):
        return f'<LoginHistoryRecord user={self.user_id} device={self.device_id} date={self.login_date}>'


class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    user_agent = db.Column(db.Text)
    history_records = relationship("LoginHistoryRecord", backref="device")

    def __repr__(self):
        return f'<Device id={self.id}, user_id={self.user_id}>'


user_role_asscoations = db.Table(
    "user_role_association",
    db.Column("user_id", UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True),
    db.Column("role_id", UUID(as_uuid=True), db.ForeignKey('roles.id'), primary_key=True))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    role_name = db.Column(db.String, unique=True, nullable=False)
    users = relationship(
        "User",
        secondary="user_role_association",
        back_populates="roles")


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    is_premium = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    devices = relationship("Device", backref=backref("user", uselist=False))
    roles = relationship(
        "Role",
        secondary="user_role_association",
        back_populates="users")

    def __repr__(self):
        return f'<User {self.email} with id={self.id}>'


class UserSocialInfo(db.Model):
    __tablename__ = 'user_social_info'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    user_phone = db.Column(db.Text)
    user_birthday = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Social info id={self.id}, user_id={self.user_id}>'
