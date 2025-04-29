from flask import Blueprint, request, jsonify
from modules.database_modules.attendance_database import AttendanceDatabase

get_class_attendance_bp = Blueprint('get_attendance_by_class', __name__)
db = AttendanceDatabase()

@get_class_attendance_bp.route('/attendance/class', methods=['GET'])
def get_class_attendance():
    try:
        class_id = request.args.get('class_id')
        if not class_id:
            return jsonify(AttendanceDatabase.generate_response(
                success=False,
                error='Missing class_id parameter',
                status_code=400
            )), 400

        result = db.get_attendance_by_class(class_id)
        return jsonify(result), result['status_code']

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(AttendanceDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500