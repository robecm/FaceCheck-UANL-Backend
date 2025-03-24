from flask import Blueprint, request, jsonify
from modules.database_modules.assignment_database import AssignmentsDatabase
import base64

upload_assignment_evidence_bp = Blueprint('upload_assignment_evidence', __name__)
db = AssignmentsDatabase()

@upload_assignment_evidence_bp.route('/assignment/evidence/upload', methods=['POST'])
def upload_assignment_evidence():
    try:
        # Check if request is JSON
        if request.is_json:
            # Process JSON request
            data = request.get_json()
            assignment_id = data.get('assignment_id')
            student_id = data.get('student_id')
            class_id = data.get('class_id')
            file_data = data.get('file_data')

            # Check required fields from JSON
            if not all([assignment_id, student_id, class_id, file_data]):
                return jsonify(AssignmentsDatabase.generate_response(
                    success=False,
                    error='Missing required parameters: assignment_id, student_id, class_id, and file_data are required.',
                    status_code=400
                )), 400

        else:
            # Process form data
            assignment_id = request.form.get('assignment_id')
            student_id = request.form.get('student_id')
            class_id = request.form.get('class_id')

            # Check required fields from form
            if not all([assignment_id, student_id, class_id]):
                return jsonify(AssignmentsDatabase.generate_response(
                    success=False,
                    error='Missing required parameters: assignment_id, student_id, and class_id are required.',
                    status_code=400
                )), 400

            # Get file from request
            if 'file' not in request.files:
                return jsonify(AssignmentsDatabase.generate_response(
                    success=False,
                    error='No file part in the request.',
                    status_code=400
                )), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify(AssignmentsDatabase.generate_response(
                    success=False,
                    error='No file selected.',
                    status_code=400
                )), 400

            # Convert file to base64
            file_data = base64.b64encode(file.read()).decode('utf-8')

        # Call the database method
        result = db.upload_assignment_evidence(
            assignment_id=assignment_id,
            student_id=student_id,
            class_id=class_id,
            file_data=file_data
        )

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