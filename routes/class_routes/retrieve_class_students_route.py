from flask import Blueprint, request, jsonify
from modules.database_modules.class_database import ClassesDatabase


retrieve_class_students_bp = Blueprint('retrieve_class_students', __name__)
db = ClassesDatabase()


@retrieve_class_students_bp.route('/class/students', methods=['GET'])
def retrieve_class_students():
    try:
        class_id = request.args.get('class_id')
        print("Received class ID:", class_id)  # Debugging print
        if not class_id:
            return jsonify(ClassesDatabase.generate_response(
                success=False,
                error='Missing class_id parameter',
                status_code=400
            )), 400

        result = db.retrieve_class_students(class_id)
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
