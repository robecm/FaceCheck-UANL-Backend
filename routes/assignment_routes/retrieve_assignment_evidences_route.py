from flask import Blueprint, request, jsonify
from modules.database_modules.assignment_database import AssignmentsDatabase

retrieve_assignment_evidences_bp = Blueprint('get_assignment_evidences', __name__)
db = AssignmentsDatabase()

@retrieve_assignment_evidences_bp.route('/assignment/evidence/list', methods=['GET'])
def retrieve_assignment_evidences():
    try:
        assignment_id = request.args.get('assignment_id')

        if not assignment_id:
            return jsonify(AssignmentsDatabase.generate_response(
                success=False,
                error='Missing assignment_id parameter',
                status_code=400
            )), 400

        result = db.get_assignment_evidences(assignment_id=assignment_id)
        return jsonify(result), result['status_code']

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(AssignmentsDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
