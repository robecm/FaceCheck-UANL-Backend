from flask import Blueprint, request, jsonify
from modules.database_modules.exam_database import ExamsDatabase


create_exam_bp = Blueprint('create_exam', __name__)
db = ExamsDatabase()


@create_exam_bp.route('/exam/create', methods=['POST'])
def create_exam():
    try:
        body = request.form if request.form else request.get_json()
        print("Received request body:", body)  # Debugging print
        required_fields = ['exam_name', 'class_id']
        optional_fields = ['date', 'class_room', 'hour']

        # Validate that all required fields are present
        for field in required_fields:
            if field not in body or not body[field]:
                print(f"Missing field: {field}")  # Debugging print
                return jsonify(ExamsDatabase.generate_response(
                    success=False,
                    error=f'Missing field: {field}',
                    status_code=400
                )), 400

        # Extract and process the exam data
        exam_data = {field: body[field] for field in required_fields}
        for field in optional_fields:
            if field in body:
                exam_data[field] = body[field]
        print("Processed exam data:", exam_data)  # Debugging print

        # Attempt to create the exam in the database
        result = db.create_exam(**exam_data)
        print("Database result:", result)  # Debugging print
        if not result['success']:
            return jsonify(ExamsDatabase.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(ExamsDatabase.generate_response(
            success=True,
            data={'message': 'Exam created successfully'},
            status_code=201
        )), 201

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(ExamsDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
