from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, bcrypt
from models import User

users_bp = Blueprint('users', __name__)


@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user = User.query.get(int(get_jwt_identity()))
    return jsonify({'success': True, 'user': user.to_dict()})


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json()
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'username' in data:
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user.id:
            return jsonify({'success': False, 'error': 'Username taken'}), 409
        user.username = data['username']
    db.session.commit()
    return jsonify({'success': True, 'user': user.to_dict()})


@users_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json()
    if not bcrypt.check_password_hash(user.password, data.get('current_password', '')):
        return jsonify({'success': False, 'error': 'Current password incorrect'}), 400
    user.password = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')
    db.session.commit()
    return jsonify({'success': True, 'message': 'Password changed'})
