from flask import Blueprint, request, jsonify
from modules.database_modules.assignment_database import AssignmentsDatabase

retrieve_teacher_assignments_bp = Blueprint('retrieve_teacher_assignments', __name__)
db = AssignmentsDatabase()


@retrieve_teacher_assignments_bp.route('/teacher/assignments', methods=['GET'])
def retrieve_teacher_assignments():
    try:
        teacher_id = request.args.get('teacher_id')

        if not teacher_id:
            return jsonify(AssignmentsDatabase.generate_response(
                success=False,
                error='Missing teacher_id parameter',
                status_code=400
            )), 400

        result = db.retrieve_teacher_assignments(teacher_id)

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