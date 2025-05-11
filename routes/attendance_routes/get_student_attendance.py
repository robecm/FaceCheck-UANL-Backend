from flask import Blueprint, request, jsonify
from modules.database_modules.attendance_database import AttendanceDatabase

get_student_attendance_bp = Blueprint('get_attendance_by_student', __name__)
db = AttendanceDatabase()

@get_student_attendance_bp.route('/attendance/student', methods=['GET'])
def get_student_attendance():
    try:
        student_id = request.args.get('student_id')
        if not student_id:
            return jsonify(AttendanceDatabase.generate_response(
                success=False,
                error='Missing student_id parameter',
                status_code=400
            )), 400

        result = db.get_attendance_by_student(student_id)
        return jsonify(result), result['status_code']

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(AttendanceDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500