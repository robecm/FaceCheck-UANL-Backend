from flask import Blueprint, request, jsonify
from modules.database import Database
import bcrypt

user_signup_bp = Blueprint('user', __name__)
db = Database()


@user_signup_bp.route('/signup-user', methods=['POST'])
def signup_user():
    try:
        body = request.get_json()   # GET REQUEST

        # EXTRACT THE INFO FROM THE REQUEST'S BODY
        user_data = {
            'name': body.get('name'),
            'username': body.get('username'),
            'age': body.get('age'),
            'faculty': body.get('faculty'),
            'matriculation_num': body.get('matriculation_num'),
            'password': body.get('password'),
            'face_img': body.get('face_img'),
        }

        # VALIDATE THAT ALL FIELDS ARE PRESENT
        if not all(user_data.values()):
            return jsonify({
                'message': 'Bad Request',
                'error': 'Todos los campos deben de estar presentes.'
            }), 400

        # HASH PASSWORD
        user_data['hashed_password'] = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
        del user_data['password']  # REMOVE UNCRYPTED PWD

        # INSERT USER DATA INTO DATABASE
        insert_success = db.signup_user(
            name=user_data['name'],
            username=user_data['username'],
            age=user_data['age'],
            faculty=user_data['faculty'],
            matriculation_num=user_data['matriculation_num'],
            hashed_password=user_data['hashed_password'],
            face_img=user_data['face_img']
        )

        # VALIDATE IF INSERTION WAS SUCCESFUL
        if insert_success:
            return jsonify({'message': 'Usuario registrado con exito'}), 201
        else:
            return jsonify({'message': 'Error al registrar al usuario'}), 500

    except Exception as e:
        return jsonify({
            'message': 'Internal server error',
            'error': str(e)
        }), 500
