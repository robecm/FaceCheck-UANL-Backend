from deepface import DeepFace
import numpy as np
import cv2
import base64

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

class ImageProcessor:
    @staticmethod
    def decode_base64(image_base64):
        try:
            img_data = base64.b64decode(image_base64)
            np_img = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            raise ValueError(f"Invalid Base64 input: {str(e)}")

    @staticmethod
    def resize_image(image, max_height=320):
        height, width = image.shape[:2]
        new_height = max_height
        new_width = int((9 / 16) * max_height)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return image

    @staticmethod
    def encode_binary(image):
        resized_image = ImageProcessor.resize_image(image)
        _, buffer = cv2.imencode('.jpg', resized_image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])  # Calidad ajustada a 90
        return buffer.tobytes()
