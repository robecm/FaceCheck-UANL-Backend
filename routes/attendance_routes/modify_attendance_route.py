from flask import Blueprint, request, jsonify
from modules.database_modules.attendance_database import AttendanceDatabase
import json

modify_attendance_bp = Blueprint('modify_attendance', __name__)
db = AttendanceDatabase()

@modify_attendance_bp.route('/attendance/modify', methods=['PUT', 'POST'])
def modify_attendance():
    try:
        # Accept JSON or form data
        body = request.get_json() if request.is_json else request.form

        # Check if all required fields are present
        if 'class_id' not in body or not body['class_id']:
            return jsonify(AttendanceDatabase.generate_response(
                success=False,
                error='Missing required field: class_id',
                status_code=400
            )), 400

        if 'student_id' not in body and 'student_ids' not in body:
            return jsonify(AttendanceDatabase.generate_response(
                success=False,
                error='Missing required field: student_id or student_ids',
                status_code=400
            )), 400

        if 'attendance_date' not in body or not body['attendance_date']:
            return jsonify(AttendanceDatabase.generate_response(
                success=False,
                error='Missing required field: attendance_date',
                status_code=400
            )), 400

        # Get common parameters
        class_id = body['class_id']
        attendance_date = body['attendance_date']
        attendance_time = body.get('attendance_time')  # Format expected: HH:MM:SS
        present = body.get('present', True)

        # Determine if we're handling single or multiple students
        if 'student_ids' in body and body['student_ids']:
            # Multiple students mode
            student_id = body['student_ids']

            if not isinstance(student_id, list):
                try:
                    # Try to parse as JSON if it's a string (form data case)
                    student_id = json.loads(student_id)
                except Exception as e:
                    return jsonify(AttendanceDatabase.generate_response(
                        success=False,
                        error='student_ids must be a JSON array of student IDs',
                        status_code=400
                    )), 400
        else:
            # Single student mode
            student_id = body['student_id']

        result = db.modify_attendance(class_id, student_id, attendance_date, attendance_time, present)
        return jsonify(result), result['status_code']

    except Exception as e:
        import traceback
        return jsonify(AttendanceDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500