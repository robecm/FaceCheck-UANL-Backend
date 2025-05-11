from flask import Blueprint, request, jsonify
from modules.database_modules.user_database import UserDatabase


modify_user_info_bp = Blueprint('modify_user_info_bp', __name__)
db = UserDatabase()


@modify_user_info_bp.route('/user/modify', methods=['PUT'])
def modify_user_info():
    try:
        body = request.form if request.form else request.get_json()
        print('Received request body:', body)  # Debugging print
        required_fields = ['user_id', 'user_type']
        optional_fields = ['name', 'username', 'password', 'email',
                           'matnum', 'worknum','faculty', 'birthdate']

        # Validate that the required field is present
        for field in required_fields:
            if field not in body or not body[field]:
                print(f'Missing required field: {field}')  # Debugging print
                return jsonify(UserDatabase.generate_response(
                    success=False,
                    error=f'Missing required field: {field}',
                    status_code=400
                )), 400

        # Extract and process the user data
        user_data = {field: body[field] for field in required_fields}
        for field in optional_fields:
            if field in body:
                user_data[field] = body[field]
        print('Processed user data:', user_data)  # Debugging print

        #Attempt to update the user in the database
        result = db.modify_user_info(**user_data)
        print('Database result:', result)  # Debugging print
        if not result['success']:
            return jsonify(UserDatabase.generate_response(
                success=False,
                error=result['error'],
                status_code=result['status_code']
            )), result['status_code']

        return jsonify(UserDatabase.generate_response(
            success=True,
            data={'message': 'User updated successfully'},
            status_code=200
        ))

    except Exception as e:
        print(f'Error updating user: {str(e)}')
        return jsonify(UserDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
