from flask import Blueprint, request, jsonify
from modules.database_modules.attendance_database import AttendanceDatabase

delete_attendance_bp = Blueprint('delete_attendance', __name__)
db = AttendanceDatabase()

@delete_attendance_bp.route('/attendance/delete', methods=['DELETE'])
def delete_attendance():
    try:
        attendance_id = request.args.get('attendance_id')
        if not attendance_id:
            return jsonify(AttendanceDatabase.generate_response(
                success=False,
                error='Missing attendance_id parameter',
                status_code=400
            )), 400

        result = db.delete_attendance(attendance_id)
        return jsonify(result), result['status_code']

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(AttendanceDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500