import networkx as nx
#print(nx.__file__)
from route_navigator import RouteNavigator

class PathPlanner:
    """
    The PathPlanner class is responsible all path planning and task scheduling tasks.
    """

    def __init__(self, edges, pos, durations):
        """
        The duration of the moves, pickups and dropoffs are initialized for cost calulation. 
        The network graph with all its edges is initialiezed for path plannning.
        """
        self.MOVE_DURATION = durations["MOVE_DURATION"]
        self.PICKUP_DURATION = durations["PICKUP_DURATION"]
        self.DROPOFF_DURATION = durations["DROPOFF_DURATION"]
        self.TURN_DURATION = durations["TURN_DURATION"]
        self.agent_locations = {}
        self.edges = edges
        self.pos = pos
        self.G = nx.Graph()
        self.G.add_edges_from(self.edges)
    
    def find_path(self, start_node, end_node):
        """
        Finds a path in the network when available.
        """
        try:
            return nx.shortest_path(self.G, source=start_node, target=end_node)
        except nx.NetworkXNoPath:
            return []
        except nx.NodeNotFound:
            return []
        

    def find_closest_agent(self, start_node, agent_locations):
        """
        Given a start node and the locations of all agents the function returns the closest agent to the start node
        """
        closest_agent = None
        closest_distance = float('inf')
        for agent in agent_locations:
            path = self.find_path(agent_locations[agent]["node"], start_node)
            cost = self.calculate_closest_path_cost(path, agent_locations[agent])
            if cost < closest_distance:
                closest_distance = cost
                closest_agent = agent
        return closest_agent
    
    def calculate_closest_path_cost(self, path, agent_location):
        """
        Calculates the cost of the path for the agent
        """
        route_navigator = RouteNavigator(self.edges, self.pos, agent_location["node"], agent_location["facing_direction"])
        turns, _ = route_navigator.get_turns(path[-1], path)
        turn_time = 0
        real_turns = 0
        for i in range(len(path)-1):
            turn_time+=abs(turns[path[i]])/90*self.TURN_DURATION
            if abs(turns[path[i]])>0:
                real_turns+=1

        return (len(path)-1)*self.MOVE_DURATION + turn_time+ real_turns+0.1

    def plan_task(self, start_node, end_node, agent_locations):
        """
        Finds all the possible paths from start node to the end node and schedules multiple scenarios.
        """
        self.agent_locations = agent_locations
        all_possible_paths = nx.all_simple_paths(self.G, source=start_node, target=end_node)
        options= {}
        for i, path in enumerate(all_possible_paths):
            options[i] = self.schedule_agents(path, agent_locations)
        option_keys = list(options.keys())
        for option in option_keys:
            if len(options[option]) == 0:
                del options[option]
                
        return options
    
    def get_best_option(self, options):
        """
        Selects the cheapest option of all the possible subtask schedules regarding the time used.
        """
        min_end_time = float('inf')
        best_option = None
        for option in options:
            if len(options[option])>0 and options[option][-1]["end_time"] < min_end_time:
                min_end_time = options[option][-1]["end_time"]
                best_option = option
        return options[best_option]
    
    def get_worst_option(self, options):
        """
        Selects the most expensive option of all the possible subtask schedules regarding the time used.
        """
        max_end_time = 0
        worst_option = None
        for option in options:
            if len(options[option])>0 and options[option][-1]["end_time"] > max_end_time:
                max_end_time = options[option][-1]["end_time"]
                worst_option = option
        return options[worst_option]
    
    def get_conflict_agents(self, path, agent_locations, exclude):
        """
        Finds all agents that are an located on the specified path and pose an obstacle for the AGVs
        """
        conflict_agents = []
        for agent in agent_locations:
            if agent_locations[agent]["node"] in path and agent != exclude:
                conflict_index = path.index(agent_locations[agent]["node"])
                conflict_agents.append((agent, conflict_index))
        
        sorted_conflict_agents = sorted(conflict_agents, key=lambda x: x[1])
        return [a[1] for a in sorted_conflict_agents], [a[0] for a in sorted_conflict_agents]

    def schedule_agents(self, path, agent_locations):
        """
        Distributes the subtask between all the robots used for this scheduling option
        """
        start_node = path[0]
        tasks = []
        closest_agent = self.find_closest_agent(start_node, agent_locations)
        if start_node == agent_locations[closest_agent]["node"]:
            raise Exception("Agent is already at the start node")
        sorted_conflict_agents_idx, sorted_conflict_agents = self.get_conflict_agents(path, agent_locations, closest_agent)
        sorted_conflict_agents.insert(0, closest_agent)
        sorted_conflict_agents_idx.insert(0, 0)
        for i, agent in enumerate(sorted_conflict_agents):
            if i==len(sorted_conflict_agents)-1 and len(sorted_conflict_agents)==1:
                subpath = path[sorted_conflict_agents_idx[i]:]
            elif i==len(sorted_conflict_agents)-1:
                subpath = path[sorted_conflict_agents_idx[i]-1:]
            elif i==0:
                subpath = path[sorted_conflict_agents_idx[i]:sorted_conflict_agents_idx[i+1]]
            else:
                subpath = path[sorted_conflict_agents_idx[i]-1:sorted_conflict_agents_idx[i+1]]
            if len(subpath) <2:
                return []
            tasks.extend(self.schedule_single_agent(subpath, agent_locations[agent], agent))

        return self.add_timing(tasks)
    
    def schedule_single_agent(self, subpath, agent_location, agent_name):
        """
        Specifies where the agent has to do which kind of task at which node
        """
        subtask = []
        to_path = self.find_path(agent_location["node"], subpath[0])
        subtask.append({"name":agent_name, "task":"MOVE", "path":to_path})
        subtask.append({"name":agent_name, "task":"TRANSPORT", "path":subpath})
        #subtask.append({"name":agent_name, "task":"MOVE", "path":[subpath[-1], subpath[-2]]})
        return subtask

    
    def add_timing(self, tasks):
        """
        Adds timing for each step for cost evaluation.
        """
        start_time = 0
        for i, subtask in enumerate(tasks):
            if subtask["task"] == "MOVE":
                subtask["start_time"] = start_time
                turn_time, turn_time_per_node, last_facing_direction = self.get_turn_info(subtask["path"], subtask["name"])
                subtask["turn_time_per_node"] = turn_time_per_node
                subtask["last_facing_direction"] = last_facing_direction
                subtask["end_time"] = start_time + (len(subtask["path"])-1)*self.MOVE_DURATION + turn_time
                start_time = subtask["end_time"]
            if subtask["task"] == "TRANSPORT":
                subtask["start_time"] = start_time
                turn_time, turn_time_per_node, last_facing_direction = self.get_turn_info(subtask["path"], subtask["name"])
                subtask["turn_time_per_node"] = turn_time_per_node
                subtask["last_facing_direction"] = last_facing_direction
                subtask["end_time"] = start_time + (len(subtask["path"])-1)*self.MOVE_DURATION + self.PICKUP_DURATION + self.DROPOFF_DURATION + turn_time
                start_time = subtask["end_time"]
        return tasks
    
    def get_turn_info(self, path, agent_name):
        route_navigator = RouteNavigator(self.edges, self.pos, self.agent_locations[agent_name]["node"], self.agent_locations[agent_name]["facing_direction"])
        turns, _ = route_navigator.get_turns(path[-1], path)
        turn_time = 0
        turn_time_per_node = {}
        for i in range(len(path)-1):
            turn_time+=abs(turns[path[i]])/90*self.TURN_DURATION
            turn_time_per_node[path[i]] = abs(turns[path[i]])/90*self.TURN_DURATION
        last_facing_direction = route_navigator.getFacingDirection()
        return turn_time, turn_time_per_node, last_facing_direction
                
