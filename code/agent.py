from communication_handler import CommunicationHandler
from path_planner import PathPlanner
from robot import Robot
from mock_robot import MockRobot
import time

class Agent:
    """
    The class serves as the Agent of the AGV which brings all modules together and coordinates communication, path planning and
    task execution
    """

    def __init__(self, location, is_coordinator, pos, edges, use_mock_robot, robot_facing_direction, durations, use_best_path):
        """
        Initializes all the Modules like the PathPlanner, Robot or MockRobot and the Communication handler. The Agent class
        also subscribes to multiple events related to the AGV communication.
        """
        self.is_coordinator = is_coordinator
        self.location = location
        self.robot_facing_direction = robot_facing_direction
        self.all_locations = {}
        self.MOVE_DURATION = durations["MOVE_DURATION"]
        self.PICKUP_DURATION = durations["PICKUP_DURATION"]
        self.DROPOFF_DURATION = durations["DROPOFF_DURATION"]
        self.TURN_DURATION = durations["TURN_DURATION"]
        self.scheduled_tasks = []
        self.next_agent = None
        self.next_agent_start_time = None
        self.use_best_path = use_best_path
        if use_mock_robot:
            self.robot = MockRobot(self.log, edges, pos, location, robot_facing_direction)
        else:
            self.robot = Robot(self.log, edges, pos, location, robot_facing_direction)
        self.clock = 0
        self.count_clock = True
        self.comm_handler = CommunicationHandler(self.handle_discover_peer)
        self.comm_handler.subscribe("LOCATION_REQUEST", self.send_location_info)
        self.comm_handler.subscribe("LOCATION_RESPONSE", self.handle_location_info)
        self.comm_handler.subscribe("TASK_REQUEST", self.handle_task_request)
        self.comm_handler.subscribe("TASK_DISTRIBUTION", self.handle_task_distribution)
        self.comm_handler.subscribe("EXECUTE_TASK", self.handle_task_completion)
        self.comm_handler.subscribe("MESSAGE", self.handle_message)
        self.comm_handler.subscribe("ECHO", self.handle_echo)
        self.comm_handler.start()
        self.all_locations[self.comm_handler.ip] = {"node": self.location, "facing_direction": self.robot_facing_direction}
        self.path_planner = PathPlanner(edges, pos, durations)
        self.log("Agent initialized.")
        
    
    def get_peers(self):
        """
        Getter for peer list
        """
        return self.comm_handler.get_peers()
    
    def log(self, message):
        """
        Logs messages to the console with specifying the own local ip
        """
        print(f"{self.comm_handler.ip}: {message}")
    
    def handle_discover_peer(self, ip):
        """
        When a agent is discovered a a request is sent to get the location of the other peer.
        Additionally the own location is passed.
        """
        self.comm_handler.send(ip, "LOCATION_REQUEST", self.all_locations[self.comm_handler.ip])
    
    def send_location_info(self, type, message, ip):
        """
        Upon a location request by a peer, the agent answers with its own location.
        """
        self.comm_handler.send(ip, "LOCATION_RESPONSE", self.all_locations[self.comm_handler.ip])
    
    def handle_location_info(self, type, location_and_facing_direction, ip):
        """
        Upon receiving location information from a peer the location is stored in a dictionary with the ip
        address as the key
        """
        self.all_locations[ip] = location_and_facing_direction

    def handle_task_request(self, type, task, ip):
        """
        Handles a request my the WMS and passes information to the path_planer to split the task in
        multiple subtask to distribute it between robots.
        """
        options = self.path_planner.plan_task(task["start_node"], task["end_node"], self.all_locations)
        if self.use_best_path:
            selected_option = self.path_planner.get_best_option(options)
        else:
            selected_option = self.path_planner.get_worst_option(options)
        self.comm_handler.send_multicast("TASK_DISTRIBUTION", selected_option)
        time.sleep(1)
        self.comm_handler.send(selected_option[0]["name"], "EXECUTE_TASK", True)
        return selected_option
    
    def handle_task_distribution(self, type, task_list, ip):
        """
        Stores subtasks assigned by the coordinator in the cell
        """
        last_task_index = 0
        for i, task in enumerate(task_list):
            if task["name"] == self.comm_handler.ip:
                self.scheduled_tasks.append(task)
                last_task_index = i
        if last_task_index == len(task_list) - 1:
            self.next_agent = ip
            self.next_agent_start_time = task_list[last_task_index]["end_time"]-1
        else:
            self.next_agent = task_list[last_task_index + 1]["name"]
            self.next_agent_start_time = task_list[last_task_index + 1]["start_time"]
    
    def handle_task_completion(self, type, payload, ip):
        """
        Upon notification from another agent the agent porcesses its subtask and passes commands to the robot.
        """
        self.log(f"Received task completion from {ip}")
        if len(self.scheduled_tasks) == 0 and self.is_coordinator:
            self.log("All tasks completed.")
        for task_idx, task in enumerate(self.scheduled_tasks):
            self.clock = task["start_time"]
            if task["task"]=="MOVE":
                pointer = 0
                while pointer<len(task["path"])-1:
                    if pointer==len(task["path"])-2 and len(self.scheduled_tasks)>task_idx+1 and self.scheduled_tasks[task_idx+1]["task"]=="TRANSPORT":
                        self.robot.prepare_pickup(task["path"][pointer+1])
                    else:
                        self.robot.prepare_move(task["path"][pointer+1])
                    self.all_locations[self.comm_handler.ip] = {"node": task["path"][pointer+1], "facing_direction": task["last_facing_direction"]}
                    self.increase_clock(self.MOVE_DURATION + task["turn_time_per_node"][task["path"][pointer]])
                    pointer += 1
            if task["task"]=="TRANSPORT":
                self.increase_clock(self.PICKUP_DURATION)
                pointer = 0
                while pointer<len(task["path"])-1:
                    if pointer==len(task["path"])-2:
                        self.robot.prepare_dropoff(task["path"][pointer+1])
                        self.all_locations[self.comm_handler.ip] = {"node": task["path"][pointer], "facing_direction": task["last_facing_direction"]}
                    else:
                        self.robot.prepare_move(task["path"][pointer+1])
                        self.all_locations[self.comm_handler.ip] = {"node": task["path"][pointer+1], "facing_direction": task["last_facing_direction"]}
                    self.increase_clock(self.MOVE_DURATION + task["turn_time_per_node"][task["path"][pointer]])
                    pointer += 1
                self.increase_clock(self.DROPOFF_DURATION)
        self.scheduled_tasks = []

    def handle_message(self, type, message, ip):
        """
        Logs messages received from other agents for testing and debugging.
        """
        #self.log(f"Response: {time.time()}")
        self.log(f"Received message from {ip}: {message}")
    
    def handle_echo(self, type, message, ip):
        """
        Upon receiving a message the agent returns the same message to the sender for testing and debugging
        """
        if ip == self.comm_handler.ip:
            return
        self.log(f"Received echo from {ip}: {message}")
        self.comm_handler.send(ip, "MESSAGE", message)
    
    def increase_clock(self, duration):
        """
        Keeps track of the agents clock
        """
        self.clock += duration
        time.sleep(duration)
        if self.count_clock and self.clock >= self.next_agent_start_time:
            self.count_clock = False
            self.comm_handler.send(self.next_agent, "EXECUTE_TASK", True)
    
    
    def send_multicast(self, type, message):
        """
        Sends a message to all the peers in the multicast group
        """
        self.comm_handler.send_multicast(type, message)
    

