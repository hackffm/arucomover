import cv2
import cv2.aruco as aruco
import numpy as np
import time


class Camera:
    def __init__(self, configuration, helper, m_modus, shm):
        self.configuration = configuration
        self.helper = helper
        self.m_modus = m_modus

        self.config = configuration.config
        self.config_camera = self.config['camera']
        self.debug = self.config['debug']
        self.default = self.config['default']

        self.shm_video = shm

        mtx, dist = self.configuration.camera_calibration()
        if self.debug:
            self.log("Camera Calibration Configuration")
            self.log(mtx)
            self.log(dist)
        self.dist = dist
        self.mtx = mtx

        # must match the real world dimensions
        ARUCO_DICT = {
            "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
            "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
            "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
            "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
            "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
        }
        self.aruco_dict = aruco.Dictionary_get(ARUCO_DICT["DICT_6X6_50"])
        self.parameters = aruco.DetectorParameters_create()

    def capture_config(self):
        _input = self.config['input'][self.config_camera['input']]
        _frame_height = self.config_camera['frame_height']
        _frame_width = self.config_camera['frame_width']

        self.log('using camera from input ' + str(_input) +
                 ' width:' + str(_frame_width) + " height:" + str(_frame_height))

        cap = cv2.VideoCapture(_input)
        cap.set(3, _frame_width)
        cap.set(4, _frame_height)
        if not cap.isOpened():
            self.log('Unable to read camera feed')
            return False
        else:
            # wait for camera warm up
            time.sleep(1.0)
        return cap

    def frame_grey(self, frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            return gray
        except Exception as e:
            self.log('frame_grey:exception:' + str(e))
            return None

    def log(self, text):
        self.helper.log_add_text('camera', 'camera:' + str(text))

    def video_memory_write(self, frame):
        try:
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            b = np.ndarray(img_rgb.shape, dtype=img_rgb.dtype, buffer=self.shm_video.buf)
            b[:] = img_rgb[:]
        except Exception as e:
            self.log('video_memory_write:exception:' + str(e))
        return

    def detect_aruco(self, cap, duration=100):
        try:
            while duration >= 1:
                ret, frame = cap.read()
                (corners, ids, rejected) = cv2.aruco.detectMarkers(
                    frame, self.aruco_dict, parameters=self.parameters)
                if len(corners) > 0:
                    ids = ids.flatten()
                    for (markerCorner, aruco_id) in zip(corners, ids):
                        rvec, tvec, objp = aruco.estimatePoseSingleMarkers(corners, 3.5, self.mtx, self.dist)
                        corners = markerCorner.reshape((4, 2))
                        (topLeft, topRight, bottomRight, bottomLeft) = corners
                        corner_x = int((topLeft[0] + bottomRight[0]) / 2.0)
                        corner_y = int((topLeft[1] + bottomRight[1]) / 2.0)
                        distance = round(np.linalg.norm(tvec[0][0]), 2)
                        position = "{},{},{}".format(corner_x, corner_y, distance)
                        if aruco_id != 0:
                            self.m_modus['detect'] = {"id": str(aruco_id), "position": position}
                            if self.debug:
                                self.log("id:" + str(aruco_id) + " position:" + str(position))
                self.video_memory_write(frame)
                time.sleep(0.1)
                duration -= 1
        except Exception as e:
            self.log('detect_aruco:exception:' + str(e))
        return
