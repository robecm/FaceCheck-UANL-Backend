import threading
import cv2
from facecheck import FaceCheck
from videocapture import VideoCapture

videocapture = VideoCapture()
facecheck = FaceCheck()
ref_img = cv2.imread('test.jpg')

while True:
    ret, frame = videocapture.cap.read()

    if ret:
        if videocapture.counter % 30 == 0:
            try:
                # facecheck.check_match(frame.copy(), ref_img)
                threading.Thread(target=facecheck.check_match, args=(frame.copy(), ref_img)).start()
            except ValueError:
                pass

        videocapture.counter += 1

        if facecheck.face_match:
            videocapture.set_text(frame, 'MATCH!')
        else:
            videocapture.set_text(frame, 'NO MATCH!')

        cv2.imshow('video', frame)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break

cv2.destroyAllWindows()
