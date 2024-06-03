import cv2

CONST_STR_CSI = "csi"
CONST_STR_USB = "usb"
CONST_STR_WEBCAM = "webcam"

CONST_LIST_CAMERA = [CONST_STR_CSI, CONST_STR_USB, CONST_STR_WEBCAM]

class Cam():
    '''
    reference
    - "CSI-Camera": https://github.com/JetsonHacksNano/CSI-Camera
    - "USB-Camera": https://github.com/jetsonhacks/USB-Camera
    '''

    def __init__(self, camera_id:int=0, type=CONST_STR_CSI):
        assert type in CONST_LIST_CAMERA

        self.camera_id = camera_id
        self.cap = ''
        self.window_title = type
        self.frame = ''

        if self.window_title == CONST_STR_CSI:
            self.set_csi_camera()
        elif self.window_title == CONST_STR_USB:
            self.set_usb_camera()
        else:
            self.set_web_camera()

    def __gstreamer_pipeline(
            self,
            sensor_id=0,
            capture_width=1920,
            capture_height=1080,
            display_width=960,
            display_height=540,
            framerate=30,
            flip_method=0,
            ):
        return (
            "nvarguscamerasrc sensor-id=%d ! "
            "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink"
            % (
                sensor_id,
                capture_width,
                capture_height,
                framerate,
                flip_method,
                display_width,
                display_height,
            )
        )

    def set_csi_camera(self,
                       capture_width=1920,
                       capture_height=1080,
                       display_width=960,
                       display_height=540,
                       framerate=30,
                       flip_method=0,):
        
        self.cap = cv2.VideoCapture(self.__gstreamer_pipeline(self.camera_id, 
                                                              capture_width, 
                                                              capture_height, 
                                                              display_width, 
                                                              display_height,
                                                              framerate,
                                                              flip_method), cv2.CAP_GSTREAMER)
        self.window_title = "CSI Camera"

    def set_usb_camera(self):
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_V4L2)
        self.window_title = "USB Camera"

    def set_web_camera(self):
        self.cap = cv2.VideoCapture(self.camera_id)
        self.window_title = "Web Camera"
    
    def close_camera(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def get_frame(self):
        assert self.cap.isOpened()

        res, frame = self.cap.read()
        if res:
            self.frame = frame
        else:
            raise ValueError("Can't get frame from camera")

    def show_cam(self, show:bool=True):
        assert self.cap.isOpened()
        try:
            window_handle = cv2.namedWindow(
                self.window_title, cv2.WINDOW_AUTOSIZE )
            # Window
            while True:
                ret_val, frame = self.cap.read()
                # Check to see if the user closed the window
                # Under GTK+ (Jetson Default), WND_PROP_VISIBLE does not work correctly. Under Qt it does
                # GTK - Substitute WND_PROP_AUTOSIZE to detect if window has been closed by user
                if cv2.getWindowProperty(self.window_title, cv2.WND_PROP_AUTOSIZE) >= 0:
                    cv2.imshow(self.window_title, frame)
                else:
                    break
                keyCode = cv2.waitKey(10) & 0xFF
                # Stop the program on the ESC key or 'q'
                if keyCode == 27 or keyCode == ord('q'):
                    break

        finally:
            self.close_camera()