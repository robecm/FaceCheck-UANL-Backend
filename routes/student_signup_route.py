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

        student_id = result.get('student_id')  # ID del estudiante recién registrado  # ID del estudiante recién registrado
        print("Student ID:", student_id)  # Debugging print

        # Procesar y almacenar la imagen en student_faces
        try:
            image_file = request.files['face_img']
            img_binary = image_file.read()
            img = ImageProcessor.decode_binary(img_binary)
            img_encoded = ImageProcessor.encode_binary(img)
            print("Processed face image")  # Debugging print

            # Guardar imagen en tabla de caras y obtener face_id
            face_result = db.insert_face_image(student_id, img_encoded)
            print("Face image insert result:", face_result)  # Debugging print
            if face_result['success']:
                face_id = face_result['data']['face_id']
                print("Face ID:", face_id)  # Debugging print

            # TODO Check if you can print the face_id and student_id

                # Actualizar estudiante con el face_id
                db.update_student_face_id(student_id, face_id)
            else:
                print("Error inserting face image.")  # Debugging print
        except Exception as e:
            print("Invalid image data:", str(e))  # Debugging print

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