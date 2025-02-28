from flask import Blueprint, request, jsonify
from modules.database_modules.class_database import ClassesDatabase


student_class_bp = Blueprint('student_class', __name__)
db = ClassesDatabase()


@student_class_bp.route('/class/add-student', methods=['POST'])
def student_class():
    try:
        print('Request received') # Debugging print
        body = request.form if request.form else request.get_json()
        print('Received request body:', body) # Debugging print
        required_fields = ['matnum', 'class_id']

        # Validate that all required fields are present
        for field in required_fields:
            if field not in body or not body[field]:
                print(f'Missing field: {field}') # Debugging print
                return jsonify(ClassesDatabase.generate_response(
                    success=False,
                    error=f'Missing field: {field}',
                    status_code=400
                )), 400

        # Extract and process the student class data
        student_class_data = {field: int(body[field]) for field in required_fields}
        print('Processed student class data:', student_class_data) # Debugging print

        # Attempt to register the student into the class in the database
        result = db.add_student_to_class(**student_class_data)
        print('Database result:', result) # Debugging print
        if not result['success']:
            return jsonify(ClassesDatabase.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(ClassesDatabase.generate_response(
            success=True,
            data={'message': 'Student added to class successfully'},
            status_code=201
        )), 201

    except Exception as e:
        print('Exception occurred:', str(e))
        return jsonify(ClassesDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
