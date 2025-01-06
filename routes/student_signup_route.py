from flask import Blueprint, request, jsonify
from modules.database import Database
import bcrypt
from modules.facecheck import Base64

student_signup_bp = Blueprint('student_signup', __name__)
db = Database()

BAD_REQUEST_MSG = 'All fields must be present.'

@student_signup_bp.route('/student-signup', methods=['POST'])
def student_signup():
    try:
        body = request.get_json()
        print("Received request body:", body)

        required_fields = ['name', 'username', 'age', 'faculty', 'matnum', 'password', 'face_img', 'email']
        for field in required_fields:
            if field not in body or not body[field]:
                print(f"Missing field: {field}")
                return jsonify(Database.generate_response(
                    success=False,
                    error=f'Missing field: {field}',
                    status_code=400
                )), 400

        user_data = {field: body[field] for field in required_fields}
        user_data['password'] = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print("Processed user data:", user_data)

        # Check that the Base64 string for the face image is valid
        try:
            img = Base64.decode_base64(user_data['face_img'])
            user_data['face_img'] = Base64.encode_base64(img)
        except ValueError as e:
            print("Invalid Base64 image data")
            return jsonify(Database.generate_response(
                success=False,
                error=f"Invalid Base64 image data: {str(e)}",
                status_code=400
            )), 400

        result = db.student_signup(**user_data)
        print("Database result:", result)

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
        print("Exception occurred:", str(e))
        return jsonify(Database.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
