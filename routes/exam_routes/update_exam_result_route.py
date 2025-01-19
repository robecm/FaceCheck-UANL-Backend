from flask import Blueprint, request, jsonify
from modules.database_modules.exam_database import ExamsDatabase


update_exam_result_bp = Blueprint('update_exam_result_bp', __name__)
db = ExamsDatabase()


@update_exam_result_bp.route('/update-exam-result', methods=['PUT'])
def update_exam_result():
    try:
        body = request.form if request.form else request.get_json()
        print('Received request body:', body)  # Debugging print
        required_fields = ['result_id', 'score']

        # Validate that all required fields are present
        for field in required_fields:
            if field not in body or not body[field]:
                print(f'Missing required field: {field}')  # Debugging print
                return jsonify(ExamsDatabase.generate_response(
                    success=False,
                    error=f'Missing required field: {field}',
                    status_code=400
                )), 400

        # Validate that the score is a valid number
        try:
            body['score'] = float(body['score'])
            if not (0 <= body['score'] <= 100):
                return jsonify(ExamsDatabase.generate_response(
                    success=False,
                    error='Score value must be between 0 and 100',
                    status_code=400
                )), 400
            # Round to 2 decimal places if more than 3 decimals
            body['score'] = round(body['score'], 2)
        except ValueError:
            return jsonify(ExamsDatabase.generate_response(
                success=False,
                error='Invalid score value: must be a number',
                status_code=400
            )), 400

        # Extract and process the exam result data
        exam_result_data = {field: body[field] for field in required_fields}
        print('Processed exam result data:', exam_result_data)  # Debugging print

        # Attempt to update the exam result in the database
        result = db.update_exam_result(**exam_result_data)
        print('Database result:', result)  # Debugging print
        if not result['success']:
            return jsonify(ExamsDatabase.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(ExamsDatabase.generate_response(
            success=True,
            data={'message': 'Exam result updated successfully'},
            status_code=200
        )), 200

    except Exception as e:
        print(f'Error updating exam result: {str(e)}')
        return jsonify(ExamsDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
