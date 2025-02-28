from flask import Blueprint, request, jsonify
from modules.facecheck import FaceCheck, ImageProcessor

check_face_bp = Blueprint('check_face', __name__)

@check_face_bp.route('/face/check-existing', methods=['POST'])
def check_face():
    try:
        body = request.get_json()

        img_base64 = body.get('img')

        if not img_base64:
            return jsonify({
                'success': False,
                'error': 'Image must be present.',
                'status_code': 400
            }), 400

        img = ImageProcessor.decode_base64(img_base64)

        face_exists = FaceCheck().face_exists(img)

        return jsonify({
            'success': True,
            'data': {'face_exists': face_exists},
            'status_code': 200
        }), 200

    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': str(ve),
            'status_code': 400
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status_code': 500
        }), 500