import models
from db import db
from exceptions import RoleAlreadyExists, UnknownRole

from . import UserService


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