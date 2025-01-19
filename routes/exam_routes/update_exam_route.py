from flask import Blueprint, request, jsonify
from modules.database_modules.exam_database import ExamsDatabase


update_exam_bp = Blueprint('update_exam_bp', __name__)
db = ExamsDatabase()


@update_exam_bp.route('/exam/update', methods=['PUT'])
def update_exam():
    try:
        body = request.form if request.form else request.get_json()
        print('Received request body:', body)  # Debugging print
        required_fields = ['exam_id']
        optional_fields = ['exam_name', 'class_id','date', 'class_room', 'hour']

        # Validate that the required field is present
        if 'exam_id' not in body or not body['exam_id']:
            print('Missing required field: exam_id')  # Debugging print
            return jsonify(ExamsDatabase.generate_response(
                success=False,
                error='Missing required field: exam_id',
                status_code=400
            )), 400

        # Extract and process the exam data
        exam_data = {field: body[field] for field in required_fields}
        for field in optional_fields:
            if field in body:
                exam_data[field] = body[field]
        print('Processed exam data:', exam_data)  # Debugging print

        # Attempt to update the exam in the database
        result = db.update_exam(**exam_data)
        print('Database result:', result)  # Debugging print
        if not result['success']:
            return jsonify(ExamsDatabase.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(ExamsDatabase.generate_response(
            success=True,
            data={'message': 'Exam updated successfully'},
            status_code=200
        )), 200

    except Exception as e:
        print(f'Error updating exam: {str(e)}')
        return jsonify(ExamsDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
