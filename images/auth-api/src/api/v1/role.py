from flask import request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

import schemas
from services import  RoleService

from . import router


@router.route('/role', methods=['POST'])
@jwt_required(fresh=True)
def create_role():
    user_data = request.json
    schemas.RoleSchema().load(user_data)

    identity = get_jwt_identity()
    if identity != 'root':
        claims = get_jwt()
        roles = claims['roles'].split(',')
        if 'admin' not in roles:
            return {'error': 'access denied'}

    RoleService.create_role(user_data['role_name'])

    return {'error': 'no error', 'detail': 'Role created successfully'}, 201


@router.route('/role', methods=['DELETE'])
@jwt_required(fresh=True)
def delete_role():
    user_data = request.json
    schemas.RoleSchema().load(user_data)

    identity = get_jwt_identity()
    if identity != 'root':
        claims = get_jwt()
        roles = claims['roles'].split(',')
        if 'admin' not in roles:
            return {'error': 'access denied'}

    RoleService.delete_role(user_data['role_name'])

    return {'error': 'no error', 'detail': 'Role deleted successfully'}, 201


@router.route('/user_role', methods=['POST'])
@jwt_required(fresh=True)
def add_user_role():
    user_data = request.json
    schemas.UserRoleAssociationSchema().load(user_data)

    identity = get_jwt_identity()
    if identity != 'root':
        claims = get_jwt()
        roles = claims['roles'].split(',')
        if 'admin' not in roles:
            return {'error': 'access denied'}

    RoleService.add_user_role(email=user_data['email'],
                              role_name=user_data['role_name'])

    return {'error': 'no error', 'detail': 'Role added to user'}, 200


@router.route('/user_role', methods=['DELETE'])
@jwt_required(fresh=True)
def delete_user_role():
    user_data = request.json
    schemas.UserRoleAssociationSchema().load(user_data)

    identity = get_jwt_identity()
    if identity != 'root':
        claims = get_jwt()
        roles = claims['roles'].split(',')
        if 'admin' not in roles:
            return {'error': 'access denied'}

    RoleService.delete_user_role(email=user_data['email'],
                                 role_name=user_data['role_name'])

    return {'error': 'no error', 'detail': 'Role deleted from the user'}, 200
