import cv2
import cv2.aruco as aruco

class MarkerDetector:
    """
    The MarkerDetector class uses computer vision to recognize markers for navigating the AGV
    """
    def __init__(self):
        """
        A dictionary of all aruco markers ass well as the parameters are initialized
        """
        self.aruco_markers_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
        self.parameters = aruco.DetectorParameters()

    def detect(self, image):
        """
        Detects the markers if available on the image and returns its id together with the corners and the modified image
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_markers_dict, parameters=self.parameters)

        if ids is not None:
            image = aruco.drawDetectedMarkers(image, corners, ids)
            return ids, corners, image
        return None, None, image