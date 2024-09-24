
class MockRobot:
    """
    The MockRobot class serves for testing and simulation purposes when no real robot is available
    
    """
    def __init__(self, log, edges, pos, location, robot_facing_direction):
        """
        Takes in the same parameters as the Robot class but only initializes the logger
        """
        self.log = log
    
    def prepare_move(self, target):
        """
        Logs a move
        """
        self.log(f"Move to {target}")  
    
    def prepare_pickup(self, target):
        """"
        Logs pick ups
        """
        self.log(f"Move to {target} and pick up")
    
    def prepare_dropoff(self, target):
        """"
        Logs drop offs
        """
        self.log(f"Move to {target} and drop off")
        