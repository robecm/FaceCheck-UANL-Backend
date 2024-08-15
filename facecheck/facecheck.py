from deepface import DeepFace


class FaceCheck:
    """

    """

    def __init__(self):
        self.face_match = False

    def check_match(self, frame, ref_img):
        """ """
        try:
            if DeepFace.verify(frame, ref_img)['verified']:
                self.face_match = True
            else:
                self.face_match = False
        except ValueError:
            self.face_match = False

        return self.face_match


