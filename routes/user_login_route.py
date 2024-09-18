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
        # Obtener los datos del JSON enviado en la solicitud
        body = request.get_json()

        # Validar que el JSON no sea None o vacío
        if not body:
            return jsonify({
                'message': 'Bad Request',
                'error': 'No JSON data provided'
            }), 400

        # Extraer 'matnum' y 'password' del cuerpo del JSON
        user_entered_data = {
            'matnum': body.get('matnum'),
            'password': body.get('password')
        }

        # Validar que ambos campos no estén vacíos
        if not user_entered_data['matnum'] or not user_entered_data['password']:
            return jsonify({
                'message': 'Bad Request',
                'error': BAD_REQUEST_MSG
            }), 401

        # Obtener los datos del usuario registrado por su número de matrícula
        user_registered_data = db.get_user_by_matnum(user_entered_data['matnum'])

        # Verificar si el usuario fue encontrado
        if not user_registered_data:
            return jsonify({
                'message': 'Unauthorized',
                'error': USER_NOT_FOUND_MSG
            }), 402

        # Log para verificar los datos del usuario recuperado
        print("Datos del usuario recuperado:", user_registered_data)

        # Comparar la contraseña introducida con la almacenada en la base de datos
        hashed_password = user_registered_data['password']
        face_img_base64 = user_registered_data['face_img']

        # Verificar si la contraseña ingresada coincide
        if bcrypt.checkpw(user_entered_data['password'].encode('utf-8'), hashed_password.encode('utf-8')):
            return jsonify({
                'message': SUCCESSFUL_LOGIN_MSG,
                'face_img': face_img_base64
            }), 200
        else:
            return jsonify({
                'message': 'Unauthorized',
                'error': INCORRECT_PASSWORD_MSG
            }), 403

    except Exception as e:
        # Log para capturar el mensaje completo de la excepción
        print(f"Error: {e}")
        return jsonify({
            'message': 'Internal Server Error',
            'error': str(e)
        }), 500
