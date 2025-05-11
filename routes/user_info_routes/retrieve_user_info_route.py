from flask import Blueprint, request, jsonify
from modules.database_modules.user_database import UserDatabase


retrieve_user_info_bp = Blueprint('retrieve_user_data', __name__)
db = UserDatabase()


@retrieve_user_info_bp.route('/user/info', methods=['GET'])
def retrieve_user_info():
    try:
        user_type = request.args.get('user_type')
        if not user_type:
            return jsonify(
                {'success': False,
                 'error': 'User type must be provided',
                 'status_code': 400})

        if user_type not in ['student', 'teacher']:
            return jsonify(
                {'success': False,
                 'error': 'Invalid user type',
                 'status_code': 400})

        user_id = int(request.args.get('user_id'))
        if not user_id:
            return jsonify(
                {'success': False,
                 'error': 'User ID must be provided',
                 'status_code': 400})

        user_info = db.retrieve_user_info(user_id, user_type)

        return jsonify(UserDatabase.generate_response(
            success=True,
            data=user_info['data'],
            status_code=200
        )), 200

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify(UserDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500