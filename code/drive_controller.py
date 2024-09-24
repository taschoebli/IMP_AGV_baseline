import time
import numpy as np

class DriveController:
    """
    The DriveController encapsulates the driving capabilities of the DJI Robomaster EP Core with a facade pattern.
    """
    def __init__(self, robot):
        """
        The robot object is passed by the robot class to the DriveController
        """
        self.robot = robot
        self.stopped = False

    def drive(self, speed, turn_angle, timeout=0.1):
        """
        Moves the robot with the specified speed and angle into the x direction for a specified time
        """
        self.robot.chassis.drive_speed(x=speed, z=turn_angle, timeout=timeout)
    
    def navigate_to_marker(self, corners, turn_angle):
        """
        Based on the corners, the distance is calculated and moves the robot to the location
        """
        angle, distance = self.calculate_marker_distance_and_angle(corners)
        time.sleep(.1)
        self.turn(angle)
        self.robot.chassis.move(x=distance, y=0, z=0, xy_speed=0.6).wait_for_completed()
        time.sleep(.1)
        self.turn(turn_angle)
    
    def pick_up_freight(self, corners, turn_angle):
        """
        Adjusts the robot into the direction of the marker and picks up the freight
        """
        angle, distance = self.calculate_marker_distance_and_angle(corners)
        self.turn(angle)
        time.sleep(1)
        self.robot.gripper.open()
        time.sleep(2)
        self.robot.robotic_arm.move(x=130, y=0).wait_for_completed()
        self.robot.robotic_arm.move(x=0, y=-120).wait_for_completed()
        self.robot.chassis.move(x=2*distance/3, y=0, z=0, xy_speed=0.6, z_speed=0).wait_for_completed()
        self.robot.gripper.close()
        time.sleep(2)
        self.robot.robotic_arm.move(x=0, y=120).wait_for_completed()
        self.robot.robotic_arm.move(x=-130, y=0).wait_for_completed()
        time.sleep(0.5)
        self.robot.chassis.move(x=distance/3, y=0, z=0, xy_speed=0.6, z_speed=0).wait_for_completed()
        self.turn(turn_angle)

    def drop_off_freight(self, corners, turn_angle):
        """
        Adjusts the robot into the direction of the marker and drops off the freight
        """
        angle, distance = self.calculate_marker_distance_and_angle(corners)
        self.turn(angle)
        time.sleep(1)
        self.robot.robotic_arm.move(x=130, y=0).wait_for_completed()
        self.robot.robotic_arm.move(x=0, y=-120).wait_for_completed()
        self.robot.chassis.move(x=2*distance/3, y=0, z=0, xy_speed=0.6, z_speed=0).wait_for_completed()
        self.robot.gripper.open()
        time.sleep(2)
        self.robot.robotic_arm.move(x=0, y=120).wait_for_completed()
        self.robot.robotic_arm.move(x=-130, y=0).wait_for_completed()
        time.sleep(0.5)
        self.robot.gripper.close()
        time.sleep(2)
        self.robot.chassis.move(x=-2*distance/3, y=0, z=0, xy_speed=0.6, z_speed=0).wait_for_completed()
        self.turn(turn_angle)

    
    def turn(self, angle):
        """
        Rotates the robot in the specified angle
        """
        self.robot.chassis.move(x=0, y=0, z=angle, xy_speed=0.5).wait_for_completed()

    def stop(self):
        """
        Stops the movement of the robot
        """
        if self.stopped:
            return
        self.robot.chassis.drive_speed(x=0, y=0, z=0)
        self.robot.chassis.stop()
        self.stopped = True
    
    def calculate_marker_distance_and_angle(self, corners):
        """
        Callculates the distance and the angle the robot has to move to move on the marker
        """
        corners_array_data = np.array(corners[0][0])

        marker_center_x = np.mean(corners_array_data[:, 0])
        marker_center_y = np.mean(corners_array_data[:, 1])

        image_center_x = 1280 / 2 /3
        image_bottom_y = 720

        delta_x = marker_center_x - image_center_x
        delta_y = image_bottom_y - marker_center_y 

        angle = np.arctan2(delta_y, delta_x) * 180 / np.pi

        distance = np.sqrt(delta_x**2 + delta_y**2)
        
        return -1 * (90-angle), (distance)/650+0.05
