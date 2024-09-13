import cv2
import facecheck


class VideoCapture:
    """

    """
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.counter = 0

    @staticmethod
    def set_text(frame, text):
        """Change the text in any given frame.
        :param frame: Frame dado
        :param text: Text Dado
        """
        cv2.putText(frame, text, (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

    @staticmethod
    def show_img(frame):
        """

        :param frame:
        :return: 
        """
        cv2.imshow("video", frame)

