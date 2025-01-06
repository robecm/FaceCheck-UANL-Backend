from deepface import DeepFace
import numpy as np
import base64
import cv2
import zlib

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

    @staticmethod
    def face_exists(image):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            for (x, y, w, h) in faces:
                print(f"Face detected with characteristics: x={x}, y={y}, width={w}, height={h}")
            return True
        return False

class Base64:
    @staticmethod
    def decode_base64(image_base64):
        try:
            img_data = base64.b64decode(image_base64)
            np_img = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            raise ValueError(f"Invalid Base64 input: {str(e)}")

    # TODO Make img uploadable into the database

    @staticmethod
    def resize_image(image, max_height=320):
        height, width = image.shape[:2]
        new_height = max_height
        new_width = int((9 / 16) * max_height)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return image

    @staticmethod
    def encode_base64(image):
        resized_image = Base64.resize_image(image)
        _, buffer = cv2.imencode('.jpg', resized_image, [int(cv2.IMWRITE_JPEG_QUALITY), 25])  # Reduce quality to 25
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        compressed_base64 = zlib.compress(image_base64.encode('utf-8'))
        return compressed_base64

    @staticmethod
    def decompress_base64(compressed_base64):
        decompressed_data = zlib.decompress(compressed_base64)
        return decompressed_data.decode('utf-8')
