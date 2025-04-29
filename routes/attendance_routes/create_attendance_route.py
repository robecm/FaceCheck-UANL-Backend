from flask import Blueprint, request, jsonify
from modules.database_modules.attendance_database import AttendanceDatabase

create_attendance_bp = Blueprint('create_attendance', __name__)
db = AttendanceDatabase()

@create_attendance_bp.route('/attendance/create', methods=['POST'])
def create_attendance():
    try:
        # Accept JSON or form data
        body = request.get_json() if request.is_json else request.form
        # Required fields: class_id, student_id, attendance_date.
        required_fields = ['class_id', 'student_id', 'attendance_date']
        for field in required_fields:
            if field not in body or not body[field]:
                return jsonify(AttendanceDatabase.generate_response(
                    success=False,
                    error=f'Missing required field: {field}',
                    status_code=400
                )), 400

        # Optional: attendance_time and present status
        class_id = body['class_id']
        student_id = body['student_id']
        attendance_date = body['attendance_date']
        attendance_time = body.get('attendance_time')  # Format expected: HH:MM:SS
        present = body.get('present', True)

        result = db.create_attendance(class_id, student_id, attendance_date, attendance_time, present)
        return jsonify(result), result['status_code']

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(AttendanceDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500