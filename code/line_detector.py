import cv2
import numpy as np

class LineDetector:
    """
    The LineDetector class uses computer vision to recognize lines it has to follow.
    """
    def __init__(self):
        """
        Specifies the upper and lower color of the line that should be detected
        """
        self.lower_red = np.array([0, 120, 70])
        self.upper_red = np.array([10, 255, 255])

    def detect(self, image, min_size=100):
        """
        Masks the image and detects the line the robot has to move. It returns the image with the contours on it as well as the
        central coordinates of the line
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_red, self.upper_red)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            
            if cv2.contourArea(largest_contour) >= min_size:
                epsilon = 0.01 * cv2.arcLength(largest_contour, True)
                approx = cv2.approxPolyDP(largest_contour, epsilon, True)
                cv2.drawContours(image, [approx], -1, (0, 255, 0), 2)
                
                M = cv2.moments(largest_contour)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                else:
                    cx, cy = 0, 0
                
                return True, (cx, cy), image
        
        return False, (0, 0), image