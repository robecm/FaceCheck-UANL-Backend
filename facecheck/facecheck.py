from deepface import DeepFace
import numpy as np
import base64
import cv2


class FaceCheck:
    def __init__(self):
        self.face_match = False

    @staticmethod
    def decode_base64(image_base64):
        img_data = base64.b64decode(image_base64)
        np_img = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        return img

    def check_match(self, cap_frame, ref_frame):
        """Check if two faces match using DeepFace."""
        try:
            # Verificar el match de las imágenes
            result = DeepFace.verify(cap_frame, ref_frame)
            self.face_match = result['verified']
        except Exception as e:
            # Manejo de errores detallado
            print(f"Error durante la verificación facial: {e}")
            self.face_match = 'ERROR'

        return self.face_match
