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

        # Validar que los campos requeridos estén presentes
        required_fields = ['name', 'username', 'age', 'faculty', 'matnum', 'password', 'face_img', 'email']
        for field in required_fields:
            if field not in body or not body[field]:
                return jsonify({
                    'message': 'Bad Request',
                    'error': f'Missing field: {field}'
                }), 400

        # Extraer los datos del usuario
        user_data = {
            'name': body['name'],
            'username': body['username'],
            'age': body['age'],
            'faculty': body['faculty'],
            'matnum': body['matnum'],
            'password': body['password'],
            'face_img': body['face_img'],
            'email': body['email']
        }

        # Hash la contraseña y eliminar la versión en texto plano
        user_data['hashed_password'] = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode(
            'utf-8')
        del user_data['password']  # Eliminar la contraseña en texto plano

        # Intentar registrar el usuario en la base de datos
        result = db.signup_user(
            name=user_data['name'],
            username=user_data['username'],
            age=user_data['age'],
            faculty=user_data['faculty'],
            matnum=user_data['matnum'],
            password=user_data['hashed_password'],
            face_img=user_data['face_img'],
            email=user_data['email']
        )

        # Verificar si el registro fue exitoso
        if result['success']:
            return jsonify({'message': 'User registered successfully'}), result['status_code']
        else:
            return jsonify({
                'message': 'Error registering user',
                'error': result['error'],
                'error_code': result.get('status_code'),
                'duplicate_field': result['duplicate_field']
            }), result['status_code']

    except Exception as e:
        return jsonify({
            'message': 'Internal server error',
            'error': str(e)
        }), 500
