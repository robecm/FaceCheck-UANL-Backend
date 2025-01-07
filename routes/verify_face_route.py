from flask import Blueprint, request, jsonify
from modules.facecheck import FaceCheck, ImageProcessor
from modules.database import Database  # Import the Database class

verify_face_bp = Blueprint('verify_face', __name__)


def decode_images(cap_frame_base64, ref_frame_base64):
    cap_frame = ImageProcessor.decode_base64(cap_frame_base64)
    ref_frame = ImageProcessor.decode_base64(ref_frame_base64)
    return cap_frame, ref_frame


@verify_face_bp.route('/verify-face', methods=['POST'])
def verify_face():
    try:
        body = request.get_json()

        cap_frame_base64 = body.get('cap_frame')
        ref_frame_base64 = body.get('ref_frame')

        if not (cap_frame_base64 and ref_frame_base64):
            return jsonify(Database.generate_response(
                success=False,
                error='Both images must be present.',
                status_code=400
            )), 400

        cap_frame, ref_frame = decode_images(cap_frame_base64, ref_frame_base64)

        face_match = FaceCheck().check_match(cap_frame, ref_frame)

        return jsonify(Database.generate_response(
            success=True,
            data={'match': face_match},
            status_code=200
        )), 200

    except ValueError as ve:
        return jsonify(Database.generate_response(
            success=False,
            error=str(ve),
            status_code=400
        )), 400
    except Exception as e:
        return jsonify(Database.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500
