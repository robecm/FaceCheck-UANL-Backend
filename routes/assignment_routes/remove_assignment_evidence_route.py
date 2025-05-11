from flask import Blueprint, request, jsonify
from modules.database_modules.assignment_database import AssignmentsDatabase

remove_assignment_evidence_bp = Blueprint('remove_assignment_evidence', __name__)
db = AssignmentsDatabase()

@remove_assignment_evidence_bp.route('/assignment/evidence/remove', methods=['DELETE'])
def remove_assignment_evidence():
    try:
        evidence_id = request.args.get('evidence_id')
        print('Received evidence ID:', evidence_id)  # Debugging print

        if not evidence_id:
            return jsonify(AssignmentsDatabase.generate_response(
                success=False,
                error='Missing evidence_id parameter',
                status_code=400
            )), 400

        result = db.remove_assignment_evidence(evidence_id=evidence_id)
        if not result['success']:
            return jsonify(result), result['status_code']

        return jsonify(result), result['status_code']

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(AssignmentsDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500