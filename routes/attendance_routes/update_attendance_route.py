from flask import Blueprint, request, jsonify
from modules.database_modules.attendance_database import AttendanceDatabase

update_attendance_bp = Blueprint('update_attendance', __name__)
db = AttendanceDatabase()

@update_attendance_bp.route('/attendance/update', methods=['PUT'])
def update_attendance():
    try:
        body = request.get_json() if request.is_json else request.form

        # Make sure attendance_id is provided
        if 'attendance_id' not in body or not body['attendance_id']:
            return jsonify(AttendanceDatabase.generate_response(
                success=False,
                error='Missing required field: attendance_id',
                status_code=400
            )), 400

        attendance_id = body['attendance_id']
        # Allowed fields: class_id, student_id, date, time, present.
        update_fields = {}
        allowed_fields = ['class_id', 'student_id', 'date', 'time', 'present']
        for field in allowed_fields:
            if field in body:
                update_fields[field] = body[field]

        if not update_fields:
            return jsonify(AttendanceDatabase.generate_response(
                success=False,
                error='No fields provided for update',
                status_code=400
            )), 400

        result = db.update_attendance(attendance_id, **update_fields)
        return jsonify(result), result['status_code']

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(AttendanceDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500