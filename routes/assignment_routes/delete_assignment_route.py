from flask import Blueprint, request, jsonify
from modules.database_modules.assignment_database import AssignmentsDatabase

delete_assignment_bp = Blueprint('delete_assignment', __name__)
db = AssignmentsDatabase()

@delete_assignment_bp.route('/assignment/delete', methods=['DELETE'])
def delete_assignment():
    try:
        assignment_id = request.args.get('assignment_id')
        print('Received assignment ID:', assignment_id)  # Debugging print
        if not assignment_id:
            return jsonify(AssignmentsDatabase.generate_response(
                success=False,
                error='Missing assignment_id parameter',
                status_code=400
            )), 400

        result = db.delete_assignment(assignment_id)
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