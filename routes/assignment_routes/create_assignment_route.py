from flask import Blueprint, request, jsonify
from modules.database_modules.assignment_database import AssignmentsDatabase
from datetime import datetime  # Importing datetime class directly

create_assignment_bp = Blueprint('create_assignment', __name__)
db = AssignmentsDatabase()

@create_assignment_bp.route('/assignment/create', methods=['POST'])
def create_assignment():
    try:
        body = request.form if request.form else request.get_json()
        print("Received request body:", body)  # Debugging print
        required_fields = ['title', 'class_id', 'due_date']
        optional_fields = ['description']

        # Validate that all required fields are present
        for field in required_fields:
            if field not in body or not body[field]:
                print(f"Missing field: {field}")  # Debugging print
                return jsonify(AssignmentsDatabase.generate_response(
                    success=False,
                    error=f'Missing field: {field}',
                    status_code=400
                )), 400

        # Validate due_date format using the datetime class
        try:
            due_date = body['due_date']
            datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify(AssignmentsDatabase.generate_response(
                success=False,
                error='Invalid due_date format. Expected format: YYYY-MM-DD HH:MM:SS',
                status_code=400
            )), 400

        # Extract and process the assignment data
        assignment_data = {field: body[field] for field in required_fields}
        for field in optional_fields:
            if field in body:
                assignment_data[field] = body[field]
        print("Processed assignment data:", assignment_data)  # Debugging print

        # Attempt to create the assignment in the database
        result = db.create_assignment(**assignment_data)
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
            status_code=201
        )), 201

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(AssignmentsDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500