from flask import Blueprint, request, jsonify
from modules.database_modules.student_database import StudentDatabase


retrieve_student_classes_bp = Blueprint('retrieve_student_classes', __name__)
db = StudentDatabase()


@retrieve_student_classes_bp.route('/student/classes', methods=['GET'])
def retrieve_student_classes():
    try:
        student_id = request.args.get('student_id')
        print("Received student ID:", student_id)  # Debugging print
        if not student_id:
            return jsonify(StudentDatabase.generate_response(
                success=False,
                error='Missing student_id parameter',
                status_code=400
            )), 400

        result = db.retrieve_student_classes(student_id)
        if not result['success']:
            return jsonify(StudentDatabase.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(StudentDatabase.generate_response(
            success=True,
            data=result['data'],
            status_code=200
        )), 200

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(StudentDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
