from flask import Blueprint, request, jsonify
from modules.database import Database
import bcrypt

user_login_bp = Blueprint('user_login', __name__)
db = Database()

# Constants for messages
BAD_REQUEST_MSG = 'All fields must be present.'
USER_NOT_FOUND_MSG = 'User not found.'
INCORRECT_PASSWORD_MSG = 'Incorrect password.'
SUCCESSFUL_LOGIN_MSG = 'Successful login.'

@user_login_bp.route('/login-user', methods=['POST'])
def login_user():
    try:
        body = request.get_json()

        user_entered_data = {
            'matnum': body.get('matnum'),
            'password': body.get('password')
        }

        # Validate each field individually to avoid accepting empty strings
        if not user_entered_data['matnum'] or not user_entered_data['password']:
            return jsonify({
                'message': 'Bad Request',
                'error': BAD_REQUEST_MSG
            }), 400

        user_registered_data = db.get_user_by_matnum(user_entered_data['matnum'])

        if not user_registered_data:
            return jsonify({
                'message': 'Unauthorized',
                'error': USER_NOT_FOUND_MSG
            }), 401

        hashed_password = user_registered_data['password']
        face_img_base64 = user_registered_data['face_img']

        if bcrypt.checkpw(user_entered_data['password'].encode('utf-8'), hashed_password.encode('utf-8')):
            return jsonify({
                'message': SUCCESSFUL_LOGIN_MSG,
                'face_img': face_img_base64
            }), 200
        else:
            return jsonify({
                'message': 'Unauthorized',
                'error': INCORRECT_PASSWORD_MSG
            }), 401

    except Exception as e:
        return jsonify({
            'message': 'Internal Server Error',
            'error': str(e)
        }), 500
