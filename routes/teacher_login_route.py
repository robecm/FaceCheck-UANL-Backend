from flask import Blueprint, request, jsonify
from modules.database import Database
import bcrypt

teacher_login_bp = Blueprint('teacher_login', __name__)
db = Database()

# Constants for messages
BAD_REQUEST_MSG = 'All fields must be present.'
USER_NOT_FOUND_MSG = 'User not found.'
INCORRECT_PASSWORD_MSG = 'Incorrect password.'
SUCCESSFUL_LOGIN_MSG = 'Successful login.'


@teacher_login_bp.route('/teacher-login', methods=['POST'])
def teacher_login():
    try:
        # Get the data from the JSON sent in the request
        body = request.get_json()

        # Validate that the JSON is not None or empty
        if not body:
            return jsonify(Database.generate_response(
                success=False,
                error='No JSON data provided',
                status_code=400
            )), 400

        # Extract 'worknum' and 'password' from the JSON body
        user_entered_data = {
            'worknum': body.get('worknum'),
            'password': body.get('password')
        }

        # Validate that both fields are not empty
        if not user_entered_data['worknum'] or not user_entered_data['password']:
            return jsonify(Database.generate_response(
                success=False,
                error=BAD_REQUEST_MSG,
                status_code=401
            )), 401

        # Get the data of the registered user by their work number
        user_registered_data = db.get_user_by_worknum(user_entered_data['worknum'])

        # Check if the user was found
        if not user_registered_data:
            return jsonify(Database.generate_response(
                success=False,
                error=USER_NOT_FOUND_MSG,
                status_code=402
            )), 402

        # Log to verify the data of the retrieved user
        print("Retrieved user data:", user_registered_data)

        # Compare the entered password with the one stored in the database
        hashed_password = user_registered_data['data']['password']
        face_img_base64 = user_registered_data['data']['face_img']

        # Check if the entered password matches the stored password
        if bcrypt.checkpw(user_entered_data['password'].encode('utf-8'), hashed_password.encode('utf-8')):
            return jsonify(Database.generate_response(
                success=True,
                data={'face_img': face_img_base64},
                message=SUCCESSFUL_LOGIN_MSG,
                status_code=200
            )), 200
        else:
            return jsonify(Database.generate_response(
                success=False,
                error=INCORRECT_PASSWORD_MSG,
                status_code=403
            )), 403

    except Exception as e:
        # Log the error
        print(f'Exception: {e}')
        return jsonify(Database.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
