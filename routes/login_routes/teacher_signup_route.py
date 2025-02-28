from flask import Blueprint, request, jsonify
from modules.database_modules.login_signup_database import LoginSignupDatabase
import bcrypt

teacher_signup_bp = Blueprint('teacher_signup', __name__)
db = LoginSignupDatabase()

# Constants for error messages
BAD_REQUEST_MSG = 'All fields must be present.'


@teacher_signup_bp.route('/signup/teacher', methods=['POST'])
def teacher_signup():
    try:
        body = request.get_json()
        print("Received request body:", body)  # Debugging print
        required_fields = ['name', 'username', 'birthdate', 'faculty', 'worknum', 'password', 'face_img', 'email']

        # Verificar campos obligatorios
        for field in required_fields:
            if field not in body or not body[field]:
                print(f"Missing field: {field}")  # Debugging print
                return jsonify(LoginSignupDatabase.generate_response(
                    success=False,
                    error=f'Missing field: {field}',
                    status_code=400
                )), 400

        # Extraer y procesar los datos del usuario
        user_data = {field: body[field] for field in required_fields}
        user_data['password'] = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print("Processed user data:", user_data)  # Debugging print

        # Intentar registrar el usuario en la base de datos
        result = db.teacher_signup(**user_data)
        print("Database result:", result)  # Debugging print
        if not result['success']:
            return jsonify(LoginSignupDatabase.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(LoginSignupDatabase.generate_response(
            success=True,
            data={'message': 'User registered successfully', 'teacher_id': result['teacher_id']},
            status_code=201
        )), 201

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(LoginSignupDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
