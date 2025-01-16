from flask import Blueprint, request, jsonify
from modules.database_modules.login_signup_database import LoginSignupDatabase


register_class_bp = Blueprint('register_class', __name__)
db = LoginSignupDatabase()


@register_class_bp.route('/register-class', methods=['POST'])
def register_class():
    try:
        body = request.form if request.form else request.get_json()
        print("Received request body:", body)  # Debugging print

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(LoginSignupDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
