from flask import Blueprint, request, jsonify
from modules.database_modules.login_signup_database import LoginSignupDatabase
import bcrypt

student_login_bp = Blueprint('student_login', __name__)
db = LoginSignupDatabase()

# Constants for messages
BAD_REQUEST_MSG = 'All fields must be present.'
USER_NOT_FOUND_MSG = 'User not found.'
INCORRECT_PASSWORD_MSG = 'Incorrect password.'
SUCCESSFUL_LOGIN_MSG = 'Successful login.'


@student_login_bp.route('/login/student', methods=['POST'])
def student_login():
    try:
        # Obtener los datos del JSON enviado en la solicitud
        body = request.get_json()

        # Validar que el JSON no sea None o vacío
        if not body:
            return jsonify(LoginSignupDatabase.generate_response(
                success=False,
                error='No JSON data provided',
                status_code=400
            )), 400

        # Extraer 'matnum' y 'password' del cuerpo del JSON
        user_entered_data = {
            'matnum': body.get('matnum'),
            'password': body.get('password')
        }

        # Validar que ambos campos no estén vacíos
        if not user_entered_data['matnum'] or not user_entered_data['password']:
            return jsonify(LoginSignupDatabase.generate_response(
                success=False,
                error=BAD_REQUEST_MSG,
                status_code=401
            )), 401

        # Obtener los datos del usuario registrado por su número de matrícula
        user_registered_data = db.get_user_by_matnum(user_entered_data['matnum'])

        # Verificar si el usuario fue encontrado
        if not user_registered_data:
            return jsonify(LoginSignupDatabase.generate_response(
                success=False,
                error=USER_NOT_FOUND_MSG,
                status_code=402
            )), 402

        # Log para verificar los datos del usuario recuperado
        print("Datos del usuario recuperado:", {**user_registered_data, 'data': {**user_registered_data['data'], 'face_img': user_registered_data['data']['face_img'][:100]}})

        # Comparar la contraseña introducida con la almacenada en la base de datos
        hashed_password = user_registered_data['data']['password']
        face_img_base64 = user_registered_data['data']['face_img']

        # Verificar si la contraseña ingresada coincide
        if bcrypt.checkpw(user_entered_data['password'].encode('utf-8'), hashed_password.encode('utf-8')):
            face_img_base64_str = face_img_base64.decode('utf-8')
            print('Face image string:', face_img_base64_str[:100])
            return jsonify(LoginSignupDatabase.generate_response(
                success=True,
                data={'message': SUCCESSFUL_LOGIN_MSG, 'face_img': face_img_base64_str, 'student_id': user_registered_data['data']['student_id']},
                status_code=200
            )), 200
        else:
            return jsonify(LoginSignupDatabase.generate_response(
                success=False,
                error=INCORRECT_PASSWORD_MSG,
                status_code=403
            )), 403

    except Exception as e:
        # Log para capturar el mensaje completo de la excepción
        print(f"Exception: {e}")
        return jsonify(LoginSignupDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
