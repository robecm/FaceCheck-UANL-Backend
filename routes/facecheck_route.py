from flask import Blueprint, request, jsonify
from facecheck.facecheck import FaceCheck

facecheck_bp = Blueprint('facecheck', __name__)


@facecheck_bp.route('/verify-face', methods=['POST'])
def verify_face():
    try:
        body = request.get_json()   # GET REQUEST

        # EXTRACT IMAGES FROM REQUEST JSON
        cap_frame_base64 = body.get('cap_frame')
        ref_frame_base64 = body.get('ref_frame')

        # IF IMAGES NOT PRESENT
        if not cap_frame_base64 or not ref_frame_base64:
            return jsonify({
                'message': 'Bad Request',
                'error': 'Both images must be present.'
            }), 400

        # CONVERT BASE64 STRINGS BACK INTO IMAGES
        facecheck = FaceCheck()
        cap_frame = facecheck.decode_base64(cap_frame_base64)
        ref_frame = facecheck.decode_base64(ref_frame_base64)

        face_match = facecheck.check_match(cap_frame, ref_frame)    # CHECK FACE MATCH

        return jsonify({'match': face_match}), 200    # RETURN JSON RESULTS

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
