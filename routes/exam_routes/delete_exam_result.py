from flask import Blueprint, request, jsonify
from modules.database_modules.exam_database import ExamsDatabase


delete_exam_result_bp = Blueprint('delete_exam_result_bp', __name__)
db = ExamsDatabase()


@delete_exam_result_bp.route('/exam/delete-result', methods=['DELETE'])
def delete_exam_result():
    try:
        result_id = request.args.get('result_id')
        print('Received result ID:', result_id) # Debugging print
        if not result_id:
            return jsonify(ExamsDatabase.generate_response(
                success=False,
                error='Missing result_id parameter',
                status_code=400
            )), 400

        result = db.delete_exam_result(result_id)
        if not result ['success']:
            return jsonify(ExamsDatabase.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(ExamsDatabase.generate_response(
            success=True,
            data=result['data'],
            status_code=200
        )), 200

    except Exception as e:
        print('Exception ocurred:', str(e))
        return jsonify(ExamsDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
