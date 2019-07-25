import cv2


class Camera(object):
    def __init__(self):
        self.video = cv2.VideoCapture('video.mp4')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        if not success:
            print 'Failing'
        image_bytes = image.tobytes()
        return image_bytes