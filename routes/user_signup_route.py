from flask import Blueprint, request, jsonify
from modules.database import Database
import bcrypt

user_signup_bp = Blueprint('user_signup', __name__)
db = Database()

# Constants for error messages
BAD_REQUEST_MSG = 'All fields must be present.'

@user_signup_bp.route('/signup-user', methods=['POST'])
def signup_user():
    try:
        body = request.get_json()

        user_data = {
            'name': body.get('name'),
            'username': body.get('username'),
            'age': body.get('age'),
            'faculty': body.get('faculty'),
            'matnum': body.get('matnum'),
            'password': body.get('password'),
            'face_img': body.get('face_img'),
        }

        # Validate each field individually
        if not all(user_data.values()):
            return jsonify({
                'message': 'Bad Request',
                'error': BAD_REQUEST_MSG
            }), 400

        # Hash password and remove plain text version
        user_data['hashed_password'] = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        del user_data['password']  # Remove plaintext password

        result = db.signup_user(
            name=user_data['name'],
            username=user_data['username'],
            age=user_data['age'],
            faculty=user_data['faculty'],
            matnum=user_data['matnum'],
            password=user_data['hashed_password'],
            face_img=user_data['face_img']
        )

        if result['success']:
            return jsonify({'message': 'User registered successfully'}), result['status_code']
        else:
            return jsonify({
                'message': 'Error registering user',
                'error': result['error'],
                'error_code': result.get('error_code')
            }), result['status_code']

    except Exception as e:
        return jsonify({
            'message': 'Internal server error',
            'error': str(e)
        }), 500
