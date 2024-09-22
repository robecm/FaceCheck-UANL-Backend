from flask import Blueprint, request, jsonify
from modules.facecheck import FaceCheck, Base64

facecheck_bp = Blueprint('facecheck', __name__)


def decode_images(cap_frame_base64, ref_frame_base64):
    cap_frame = Base64.decode_base64(cap_frame_base64)
    ref_frame = Base64.decode_base64(ref_frame_base64)
    return cap_frame, ref_frame


@facecheck_bp.route('/verify-face', methods=['POST'])
def verify_face():
    try:
        body = request.get_json()

        cap_frame_base64 = body.get('cap_frame')
        ref_frame_base64 = body.get('ref_frame')

        if not (cap_frame_base64 and ref_frame_base64):
            return jsonify({
                'message': 'Bad Request',
                'error': 'Both images must be present.'
            }), 400

        cap_frame, ref_frame = decode_images(cap_frame_base64, ref_frame_base64)

        face_match = FaceCheck().check_match(cap_frame, ref_frame)

        return jsonify({'match': face_match}), 200

    except ValueError as ve:
        return jsonify({
            'message': 'Bad Request',
            'error': str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            'message': 'Internal server error',
            'error': str(e)
        }), 500
