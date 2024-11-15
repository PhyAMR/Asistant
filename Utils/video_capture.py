import cv2


class VideoCapture:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Can't read frame")
        return frame

    def release(self):
        self.cap.release()
