from flask import Blueprint, request, jsonify
from modules.database_modules.class_database import ClassesDatabase


delete_student_class_bp = Blueprint('delete_student_class', __name__)
db = ClassesDatabase()


@delete_student_class_bp.route('/class/delete-student', methods=['DELETE'])
def delete_student_class():
    try:
        class_id = request.args.get('class_id')
        student_id = request.args.get('student_id')
        print('Received class ID:', class_id)  # Debugging print
        print('Received student ID:', student_id)  # Debugging print

        if not class_id or not student_id:
            return jsonify(ClassesDatabase.generate_response(
                success=False,
                error='Missing class_id or student_id parameter',
                status_code=400
            )), 400

        result = db.del_student_from_class(student_id, class_id)
        print(result)
        if not result['success']:
            return jsonify(ClassesDatabase.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(ClassesDatabase.generate_response(
            success=True,
            data=result['data'],
            status_code=200
        )), 200

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(ClassesDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
