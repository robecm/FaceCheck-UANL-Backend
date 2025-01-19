from flask import Blueprint, request, jsonify
from modules.database_modules.class_database import ClassesDatabase


register_class_bp = Blueprint('register_class', __name__)
db = ClassesDatabase()


@register_class_bp.route('/class/register', methods=['POST'])
def register_class():
    try:
        body = request.form if request.form else request.get_json()
        print("Received request body:", body)  # Debugging print
        required_fields = ['class_name', 'teacher_id', 'group_num', 'semester']
        optional_fields = ['class_room', 'start_time', 'end_time', 'week_days']

        # Validate that all required fields are present
        for field in required_fields:
            if field not in body or not body[field]:
                print(f"Missing field: {field}")  # Debugging print
                return jsonify(ClassesDatabase.generate_response(
                    success=False,
                    error=f'Missing field: {field}',
                    status_code=400
                )), 400

        # Extract and process the class data
        class_data = {field: body[field] for field in required_fields}
        for field in optional_fields:
            if field in body:
                class_data[field] = body[field]
        print("Processed class data:", class_data)  # Debugging print

        # Attempt to register the class in the database
        result = db.register_class(**class_data)
        print("Database result:", result)  # Debugging print
        if not result['success']:
            return jsonify(ClassesDatabase.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(ClassesDatabase.generate_response(
            success=True,
            data={'message': 'Class registered successfully'},
            status_code=201
        )), 201

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(ClassesDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
