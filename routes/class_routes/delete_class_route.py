from flask import Blueprint, request, jsonify
from modules.database_modules.class_database import ClassesDatabase


delete_class_bp = Blueprint('delete_class_route', __name__)
db = ClassesDatabase()


@delete_class_bp.route('/class/delete', methods=['DELETE'])
def delete_class():
    try:
        class_id = request.args.get('class_id')
        print('Received class ID:', class_id)  # Debugging print
        if not class_id:
            return jsonify(ClassesDatabase.generate_response(
                success=False,
                error='Missing class_id parameter',
                status_code=400
            )), 400

        result = db.delete_class(class_id)
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
