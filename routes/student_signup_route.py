from flask import Blueprint, request, jsonify
from modules.database import Database
import bcrypt
from modules.facecheck import ImageProcessor

student_signup_bp = Blueprint('student_signup', __name__)
db = Database()

BAD_REQUEST_MSG = 'All fields must be present.'

@student_signup_bp.route('/student-signup', methods=['POST'])
def student_signup():
    try:
        body = request.form if request.form else request.get_json()
        print("Received request body:", body)  # Debugging print
        required_fields = ['name', 'username', 'age', 'faculty', 'matnum', 'password', 'face_img', 'email']

        # Verificar campos obligatorios
        for field in required_fields:
            if field not in body or not body[field]:
                print(f"Missing field: {field}")  # Debugging print
                return jsonify(Database.generate_response(
                    success=False,
                    error=f'Missing field: {field}',
                    status_code=400
                )), 400

        # Procesar datos del estudiante (sin imagen aún)
        user_data = {field: body[field] for field in required_fields}
        user_data['password'] = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print("Processed user data:", user_data)  # Debugging print

        # Insertar estudiante en la tabla principal
        result = db.student_signup(**user_data)
        print("Database result:", result)  # Debugging print
        if not result['success']:
            return jsonify(Database.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(Database.generate_response(
            success=True,
            data={'message': 'User registered successfully'},
            status_code=201
        )), 201

    except Exception as e:
        print("Exception occurred:", str(e))  # Debugging print
        return jsonify(Database.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500