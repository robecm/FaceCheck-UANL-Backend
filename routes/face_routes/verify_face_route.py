from flask import Blueprint, request, jsonify
from modules.facecheck import FaceCheck, ImageProcessor
from modules.database_modules.login_signup_database import LoginSignupDatabase
import base64

verify_face_bp = Blueprint('verify_face', __name__)


def decode_images(cap_frame_base64, ref_frame_base64):
    if not cap_frame_base64:
        raise ValueError("Missing captured frame data")

    if not ref_frame_base64:
        raise ValueError("Missing reference frame data")

    try:
        cap_frame = ImageProcessor.decode_base64(cap_frame_base64)
        ref_frame = ImageProcessor.decode_base64(ref_frame_base64)
        return cap_frame, ref_frame
    except Exception as e:
        raise


@verify_face_bp.route('/face/verify', methods=['POST'])
def verify_face():
    try:
        body = request.get_json()

        if not body:
            return jsonify(LoginSignupDatabase.generate_response(
                success=False,
                error='No JSON data provided.',
                status_code=400
            )), 400

        cap_frame_base64 = body.get('cap_frame')
        ref_frame_base64 = body.get('ref_frame')
        student_id = body.get('student_id')

        # Case 1: Both cap_frame and ref_frame are provided directly
        if cap_frame_base64 and ref_frame_base64:
            cap_frame, ref_frame = decode_images(cap_frame_base64, ref_frame_base64)
            face_match = FaceCheck().check_match(cap_frame, ref_frame)

            return jsonify(LoginSignupDatabase.generate_response(
                success=True,
                data={'match': face_match},
                status_code=200
            )), 200

        # Case 2: cap_frame and student_id are provided
        elif cap_frame_base64 and student_id:
            # Get reference face from the database
            db_result = LoginSignupDatabase().get_face_by_student_id(student_id)

            if not db_result['success']:
                return jsonify(LoginSignupDatabase.generate_response(
                    success=False,
                    error=db_result['error'],
                    status_code=db_result['status_code']
                )), db_result['status_code']

            ref_frame_base64 = db_result['data']['face_img_base64']

            # Decode both images
            cap_frame, ref_frame = decode_images(cap_frame_base64, ref_frame_base64)

            # Compare faces
            face_match = FaceCheck().check_match(cap_frame, ref_frame)

            return jsonify(LoginSignupDatabase.generate_response(
                success=True,
                data={'match': face_match},
                status_code=200
            )), 200

        else:
            return jsonify(LoginSignupDatabase.generate_response(
                success=False,
                error='Both captured frame and either reference frame or student ID must be provided.',
                status_code=400
            )), 400

    except ValueError as ve:
        return jsonify(LoginSignupDatabase.generate_response(
            success=False,
            error=str(ve),
            status_code=400
        )), 400
    except Exception as e:
        import traceback
        return jsonify(LoginSignupDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500