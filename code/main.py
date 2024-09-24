from agent import Agent
from environment_loader import EnvironmentLoader

"""
Load all the environment variables
"""
envl = EnvironmentLoader()
is_coordinator = envl.getIsCoordinator()
location = envl.getLocation()
pos = envl.getPos()
edges = envl.getEdges()
use_mock_robot = envl.getUseMockRobot()
robot_facing_direction = envl.getFacingDirection()
durations = envl.getDurations()
use_best_path = envl.getUseBestPath()

"""
Initializes an Agent object 
"""

a = Agent(location, is_coordinator, pos, edges, use_mock_robot, robot_facing_direction, durations, use_best_path)