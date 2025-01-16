from flask import Blueprint, request, jsonify
from modules.database_modules.class_database import ClassesDatabase


retrieve_classes_bp = Blueprint('retrieve_classes', __name__)
db = ClassesDatabase()


@retrieve_classes_bp.route('/retrieve-classes', methods=['GET'])
def retrieve_classes():
    try:
        print("Received request:", request.args)  # Debugging print
        teacher_id = request.args.get('teacher_id')
        print("Received teacher ID:", teacher_id)  # Debugging print
        if not teacher_id:
            return jsonify(ClassesDatabase.generate_response(
                success=False,
                error='Missing teacher_id parameter',
                status_code=400
            )), 400

        result = db.retrieve_classes(teacher_id)
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
