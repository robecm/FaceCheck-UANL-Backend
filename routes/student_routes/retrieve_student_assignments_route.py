from flask import Blueprint, request, jsonify
from modules.database_modules.assignment_database import AssignmentsDatabase

retrieve_student_assignments_bp = Blueprint('retrieve_student_assignments', __name__)
db = AssignmentsDatabase()


@retrieve_student_assignments_bp.route('/student/assignments', methods=['GET'])
def retrieve_student_assignments():
    try:
        student_id = request.args.get('student_id')
        print("Received student ID:", student_id)

        if not student_id:
            return jsonify(AssignmentsDatabase.generate_response(
                success=False,
                error='Missing student_id parameter',
                status_code=400
            )), 400

        result = db.retrieve_student_assignments(student_id)
        if not result['success']:
            return jsonify(AssignmentsDatabase.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(AssignmentsDatabase.generate_response(
            success=True,
            data=result['data'],
            status_code=200
        )), 200

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(AssignmentsDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500