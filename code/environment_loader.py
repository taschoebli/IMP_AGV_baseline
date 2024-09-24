import os
from dotenv import load_dotenv

class EnvironmentLoader:
    """
    The EnvironmentLoader loads all the environment variables specified in the .env file.
    """
    def __init__(self):
        load_dotenv()

    def getIsCoordinator(self):
        return os.getenv('IS_COORDINATOR', 'False').lower() == 'true'
    
    def getLocation(self):
        return os.getenv('LOCATION', '')
    
    def getUseMockRobot(self):
        return os.getenv('USE_MOCK_ROBOT', 'False').lower() == 'true'
    
    def getFacingDirection(self):
        return int(os.getenv('FACING_DIRECTION', '0'))
    
    def getEdges(self):
        edges = os.getenv('EDGES', '')
        return [tuple(edge.split(',')) for edge in edges.split(';')]
    
    def getPos(self):
        pos = {}
        for key, value in os.environ.items():
            if key.startswith('POS_'):
                node = key.replace('POS_', '')
                pos[node] = tuple(map(int, value.split(',')))
        return pos
    
    def getDurations(self):
        durations = {}
        durations["MOVE_DURATION"] = int(os.getenv('MOVE_DURATION', '1'))
        durations["PICKUP_DURATION"] = int(os.getenv('PICKUP_DURATION', '1'))
        durations["DROPOFF_DURATION"] = int(os.getenv('DROPOFF_DURATION', '1'))
        durations["TURN_DURATION"] = int(os.getenv('TURN_DURATION', '1'))
        return durations
    
    def getUseBestPath(self):
        return os.getenv('USE_BEST_PATH', 'True').lower() == 'true'
