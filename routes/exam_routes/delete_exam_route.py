from flask import Blueprint, request, jsonify
from modules.database_modules.exam_database import ExamsDatabase


delete_exam_bp = Blueprint('delete_exam_route', __name__)
db = ExamsDatabase()


@delete_exam_bp.route('/exam/delete', methods=['DELETE'])
def delete_exam():
    try:
        exam_id = request.args.get('exam_id')
        print('Received exam ID:', exam_id)  # Debugging print
        if not exam_id:
            return jsonify(ExamsDatabase.generate_response(
                success=False,
                error='Missing exam_id parameter',
                status_code=400
            )), 400

        result = db.delete_exam(exam_id)
        if not result['success']:
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
        print("Exception occurred:", str(e))
        return jsonify(ExamsDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
