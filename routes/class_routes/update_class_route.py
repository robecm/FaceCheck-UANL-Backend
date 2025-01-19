from flask import Blueprint, request, jsonify
from modules.database_modules.class_database import ClassesDatabase


update_class_bp = Blueprint('update_class', __name__)
db = ClassesDatabase()


@update_class_bp.route('/class/update', methods=['PUT'])
def update_class():
    try:
        body = request.form if request.form else request.get_json()
        print("Received request body:", body)  # Debugging print
        required_fields = ['class_id']
        optional_fields = ['class_name', 'teacher_id', 'group_num', 'semester', 'class_room', 'start_time', 'end_time', 'week_days']

        # Validate that the required field is present
        if 'class_id' not in body or not body['class_id']:
            print("Missing field: class_id")  # Debugging print
            return jsonify(ClassesDatabase.generate_response(
                success=False,
                error='Missing field: class_id',
                status_code=400
            )), 400

        # Extract and process the class data
        class_data = {field: body[field] for field in required_fields}
        for field in optional_fields:
            if field in body:
                class_data[field] = body[field]
        print("Processed class data:", class_data)  # Debugging print

        # Attempt to update the class in the database
        result = db.update_class(**class_data)
        print("Database result:", result)  # Debugging print
        if not result['success']:
            return jsonify(ClassesDatabase.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(ClassesDatabase.generate_response(
            success=True,
            data={'message': 'Class updated successfully'},
            status_code=200
        )), 200

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(ClassesDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
