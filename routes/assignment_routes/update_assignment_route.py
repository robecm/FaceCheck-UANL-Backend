from flask import Blueprint, request, jsonify
from modules.database_modules.assignment_database import AssignmentsDatabase
from datetime import datetime

update_assignment_bp = Blueprint('update_assignment', __name__)
db = AssignmentsDatabase()

@update_assignment_bp.route('/assignment/update', methods=['PUT'])
def update_assignment():
    try:
        body = request.form if request.form else request.get_json()
        print("Received request body:", body)  # Debugging print

        # Check if assignment_id is provided
        if 'assignment_id' not in body or not body['assignment_id']:
            return jsonify(AssignmentsDatabase.generate_response(
                success=False,
                error='Missing required field: assignment_id',
                status_code=400
            )), 400

        # Define optional fields that can be updated
        optional_fields = ['title', 'description', 'due_date', 'class_id']
        update_data = {'assignment_id': body['assignment_id']}

        # Check if at least one optional field is provided
        has_update_field = False
        for field in optional_fields:
            if field in body:
                update_data[field] = body[field]
                has_update_field = True

        if not has_update_field:
            return jsonify(AssignmentsDatabase.generate_response(
                success=False,
                error='No fields provided for update',
                status_code=400
            )), 400

        # Validate due_date format if provided
        if 'due_date' in update_data:
            try:
                due_date = update_data['due_date']
                datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return jsonify(AssignmentsDatabase.generate_response(
                    success=False,
                    error='Invalid due_date format. Expected format: YYYY-MM-DD HH:MM:SS',
                    status_code=400
                )), 400

        # Attempt to update the assignment in the database
        print("Processed update data:", update_data)  # Debugging print
        result = db.update_assignment(**update_data)
        print("Database result:", result)  # Debugging print

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