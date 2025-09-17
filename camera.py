import cv2

class CameraHandler:
    def __init__(self, camera_index=0):
        self.cap = None
        self.camera_running = False
        self.index = camera_index

    def start(self):
        self.cap = cv2.VideoCapture(self.index)
        if not self.cap.isOpened():
            return False
        self.camera_running = True
        return True

    def read_frame(self):
        if self.cap and self.camera_running:
            ret, frame = self.cap.read()
            return ret, frame
        return False, None

    def stop(self):
        self.camera_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
