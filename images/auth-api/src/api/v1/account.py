from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
import schemas
from services import UserService, HistoryService
from flask import request, jsonify
from . import router


@router.route('/account', methods=['GET'])
@jwt_required(fresh=True)
def get_account():
    user = UserService.get_user_by_email(email=get_jwt_identity())

    return {
        'user_id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'created': user.created,
        'updated': user.updated
           }, 200


@router.route('/account', methods=['PUT'])
@jwt_required(fresh=True)
def update_account():

    user_data = request.json
    schemas.UserSchema().load(user_data)
    user_id = UserService.get_user_by_email(email=get_jwt_identity()).id
    UserService.update_user(
        user_id=user_id,
        **user_data
    )
    return {'error': 'no error', 'detail': 'Account updated successfully'}, 200


@router.route('/history', methods=['GET'])
@jwt_required(fresh=True)
def get_history():
    user_data = request.json
    schemas.DateRangeSchema().load(user_data)
    email = get_jwt_identity()
    history_records = HistoryService.get_history(email,
                                                 start_date=user_data['start_date'],
                                                 end_date=user_data['end_date'])
    return jsonify({'history': history_records}), 200
