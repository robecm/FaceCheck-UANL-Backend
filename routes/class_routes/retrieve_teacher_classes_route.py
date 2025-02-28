from flask import Blueprint, request, jsonify
from modules.database_modules.teacher_database import TeacherDatabase


retrieve_teacher_classes_bp = Blueprint('retrieve_teacher_classes', __name__)
db = TeacherDatabase()


@retrieve_teacher_classes_bp.route('/teacher/classes', methods=['GET'])
def retrieve_teacher_classes():
    try:
        teacher_id = request.args.get('teacher_id')
        print("Received teacher ID:", teacher_id)  # Debugging print
        if not teacher_id:
            return jsonify(TeacherDatabase.generate_response(
                success=False,
                error='Missing teacher_id parameter',
                status_code=400
            )), 400

        result = db.retrieve_teacher_classes(teacher_id)
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
        print("Exception occurred:", str(e))
        return jsonify(TeacherDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
