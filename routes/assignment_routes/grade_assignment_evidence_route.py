from flask import Blueprint, request, jsonify
from modules.database_modules.assignment_database import AssignmentsDatabase

grade_assignment_evidence_bp = Blueprint('grade_assignment_evidence', __name__)
db = AssignmentsDatabase()

@grade_assignment_evidence_bp.route('/assignment/evidence/grade', methods=['PUT'])
def grade_assignment_evidence():
    try:
        # Get parameters from request
        if request.is_json:
            # Process JSON request
            data = request.get_json()
            evidence_id = data.get('evidence_id')
            grade = data.get('grade')
            feedback = data.get('feedback')  # New parameter - optional
        else:
            # Process form data
            evidence_id = request.form.get('evidence_id')
            grade = request.form.get('grade')
            feedback = request.form.get('feedback')  # New parameter - optional

        # Check required fields
        if not evidence_id:
            return jsonify(AssignmentsDatabase.generate_response(
                success=False,
                error='Missing required parameter: evidence_id is required.',
                status_code=400
            )), 400

        if grade is None:
            return jsonify(AssignmentsDatabase.generate_response(
                success=False,
                error='Missing required parameter: grade is required.',
                status_code=400
            )), 400

        # Call the database method with the optional feedback parameter
        result = db.grade_assignment_evidence(
            evidence_id=evidence_id,
            grade=grade,
            feedback=feedback
        )

        return jsonify(result), result['status_code']

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(AssignmentsDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500