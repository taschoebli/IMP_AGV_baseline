#from robomaster import robot
import cv2
import threading
from marker_detector import MarkerDetector
from line_detector import LineDetector
from drive_controller import DriveController
from route_navigator import RouteNavigator
        

class State:
    """
    The robot is either in a FOLLOWING_LINE or MOVING_ON_NODE state.
    """
    FOLLOWING_LINE = 1
    MOVING_ON_NODE = 2

class Robot:
    def __init__(self, log, edges, pos, location, robot_facing_direction):
        """
        Initializes the computer vision modules LineDetector and MarkerDetector as well as the RouteNavigator module.
        """
        self.log = log
        #self.ep_robot = robot.Robot()
        self.line_detector = LineDetector()
        self.marker_detector = MarkerDetector()
        self.drive_controller = DriveController(self.ep_robot)
        self.state = State.FOLLOWING_LINE
        self.route_navigator = RouteNavigator(edges, pos, location, robot_facing_direction)
        self.turns = {}
        self.pickup_parcel = False
        self.dropoff_parcel = False
        self.mission_completed = False
        self.configure()

    def configure(self):
        """
        Establishes a connection to the robot through the Wi-Fi network and initializes the cmaera stream.
        """
        #self.ep_robot.initialize(conn_type="sta")
        #self.ep_camera = self.ep_robot.camera
        #self.ep_camera.start_video_stream(display=False)

    def prepare_move(self, target):
        """
        Prepares the robot for a move to the next node
        """
        self.log(f"Move to {target}")  
        self.target = target
        self.turns, self.initial_turn = self.route_navigator.get_turns(target)
        self.turns[target] = 0
        self.mission_completed = False
        self.pickup_parcel = False
        self.state = State.FOLLOWING_LINE
        self.execute()

    def prepare_pickup(self, target):
        """
        Prepares the robot for a pickup on the next node
        """
        self.log(f"Move to {target} and pick up")
        self.target = target
        self.turns, self.initial_turn = self.route_navigator.get_turns(target)
        self.turns[target] = 0
        self.mission_completed = False
        self.state = State.FOLLOWING_LINE
        self.pickup_parcel = True
        self.execute()

    def prepare_dropoff(self, target):
        """
        Prepares the robot for a dropoff on the next node
        """
        self.log(f"Move to {target} and drop off")
        self.target = target
        self.turns, self.initial_turn = self.route_navigator.get_turns(target)
        self.turns[target] = 0
        self.mission_completed = False
        self.state = State.FOLLOWING_LINE
        self.dropoff_parcel = True
        self.execute()

    def handle_line_detection(self, img_with_line, centroid):
        """
        Handles the event of a line detection and calculates the turn_angle 
        and passes it to the drive_controller for execution
        """
        img_center = img_with_line.shape[1] // 2
        error = centroid[0] - img_center
        turn_angle = error * 0.05
        self.drive_controller.drive(speed=0.2, turn_angle=turn_angle)

    def handle_marker_detection(self, ids, corners, img):
        """"
        Handles the event of a marker detection and takes according action
        """
        id = ids.flatten()[0]
        marker_letter = chr(64 + id)
        if self.pickup_parcel:
            self.drive_controller.pick_up_freight(corners, self.turns[marker_letter])
            self.pickup_parcel = False
            self.mission_completed = True
            return
        if self.dropoff_parcel:
            self.drive_controller.drop_off_freight(corners, self.turns[marker_letter])
            self.dropoff_parcel = False
            self.mission_completed = True
            return
        elif id >= 1 and id <= 12:
            if marker_letter in self.turns:
                self.drive_controller.navigate_to_marker(corners,self.turns[marker_letter])
        if marker_letter == self.target:
            self.mission_completed = True
            return
        self.state = State.FOLLOWING_LINE
    

    def execute(self):
        """
        The function processes the camera images from the robot and based on the state either followes the detected line
        or follows a marker when detected.
        """
        self.drive_controller.turn(self.initial_turn)
        img_counter=0
        try:
            while True:
                img = self.ep_camera.read_cv2_image(strategy='newest')
                marker_image = img[img.shape[0]//2:,img.shape[1]//3:img.shape[1]*2//3]

                line_img = img[:, img.shape[1]//3:img.shape[1]*2//3]

                line_detected, centroid, img_with_line = self.line_detector.detect(line_img)
                ids, corners, img_with_markers = self.marker_detector.detect(marker_image)

                threads = []

                if ids is not None and self.state == State.FOLLOWING_LINE:
                    self.state = State.MOVING_ON_NODE
                    marker_thread = threading.Thread(target=self.handle_marker_detection, args=(ids, corners, img_with_markers))
                    threads.append(marker_thread)

                elif line_detected and self.state == State.FOLLOWING_LINE:

                    self.handle_line_detection(img_with_line, centroid)

                for thread in threads:
                    thread.start()

                cv2.imwrite(f"images/image_{self.target}_{img_counter}.jpg", img)
                img_counter += 1

                #cv2.imshow("RoboMaster Camera Feed", img)
                if self.mission_completed:
                    break
        except KeyboardInterrupt:
            print("Stopping the application...")