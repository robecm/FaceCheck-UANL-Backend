from flask import Blueprint, request, jsonify
from modules.database_modules.login_signup_database import LoginSignupDatabase

check_duplicate_bp = Blueprint('check_duplicate', __name__)
db = LoginSignupDatabase()

@check_duplicate_bp.route('/signup/student-duplicate', methods=['POST'])
def check_duplicate():
    try:
        body = request.get_json()

        # Print the request data to the console
        print("Request data:", body)

        # Validate that the required fields are present
        required_fields = ['email', 'matnum', 'username']
        for field in required_fields:
            if field not in body or not body[field]:
                return jsonify(LoginSignupDatabase.generate_response(
                    success=False,
                    error=f'Missing field: {field}',
                    status_code=400
                )), 400

        # Extract user data
        email = body['email']
        matnum = body['matnum']
        username = body['username']

        # Check for duplicate user
        result = db.check_user_exists(email, matnum, username)

        # Return the result
        return jsonify(result), result['status_code']

    except Exception as e:
        return jsonify(LoginSignupDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
