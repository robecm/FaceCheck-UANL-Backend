from flask import Blueprint, request, jsonify
from modules.database import Database
import bcrypt

student_signup_bp = Blueprint('student_signup', __name__)
db = Database()

# Constants for error messages
BAD_REQUEST_MSG = 'All fields must be present.'


@student_signup_bp.route('/student-signup', methods=['POST'])
def student_signup():
    try:
        body = request.get_json()

        # Validar que los campos requeridos estén presentes
        required_fields = ['name', 'username', 'age', 'faculty', 'matnum', 'password', 'face_img', 'email']
        for field in required_fields:
            if field not in body or not body[field]:
                return jsonify(Database.generate_response(
                    success=False,
                    error=f'Missing field: {field}',
                    status_code=400
                )), 400

        # Extraer y procesar los datos del usuario
        user_data = {field: body[field] for field in required_fields}
        user_data['password'] = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Intentar registrar el usuario en la base de datos
        result = db.student_signup(**user_data)

        # Verificar si el registro fue exitoso
        if result['success']:
            return jsonify(Database.generate_response(
                success=True,
                data={'message': 'User registered successfully'},
                status_code=201
            )), 201
        else:
            return jsonify(Database.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code'],
                duplicate_field=result.get('duplicate_field')
            )), result['status_code']

    except Exception as e:
        return jsonify(Database.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
