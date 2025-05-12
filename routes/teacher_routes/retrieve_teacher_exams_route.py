from flask import Blueprint, request, jsonify
from modules.database_modules.teacher_database import TeacherDatabase


retrieve_teacher_exams_bp = Blueprint('retrieve_teacher_exams', __name__)
db = TeacherDatabase()


@retrieve_teacher_exams_bp.route('/teacher/exams', methods=['GET'])
def retrieve_teacher_exams():
    try:
        teacher_id = request.args.get('teacher_id')
        if not teacher_id:
            return jsonify(TeacherDatabase.generate_response(
                success=False,
                error='Missing teacher_id parameter',
                status_code=400
            )), 400

        result = db.retrieve_teacher_exams(teacher_id)
        if not result['success']:
            return jsonify(TeacherDatabase.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(TeacherDatabase.generate_response(
            success=True,
            data=result['data'],
            status_code=200
        )), 200

    except Exception as e:
        return jsonify(TeacherDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500