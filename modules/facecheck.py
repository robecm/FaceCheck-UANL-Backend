from deepface import DeepFace
import numpy as np
import base64
import cv2


class FaceCheck:
    def __init__(self):
        self.face_match = False

    def check_match(self, cap_frame, ref_frame):
        try:
            if DeepFace.verify(cap_frame, ref_frame)['verified']:
                self.face_match = True
            else:
                self.face_match = False
        except ValueError:
            self.face_match = 'VALUE ERROR'

        return self.face_match


class Base64:
    @staticmethod
    def decode_base64(image_base64):
        img_data = base64.b64decode(image_base64)
        np_img = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        return img

    @staticmethod
    def encode_base64(image):
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return image_base64
