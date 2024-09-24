


from graph_options import GraphOptions
import sys
import os
from pprint import pprint
folder1_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'agv_software'))
sys.path.insert(0, folder1_path)

from path_planner import PathPlanner # type: ignore


class TimeCalculator:
    
    def __init__(self, option, durations, agent_locations):
        go = GraphOptions.OPTIONS
        edges = go[option]["edges"]
        pos = go[option]["positions"]
        self.durations = durations
        self.agent_locations = agent_locations
        self.path_planner = PathPlanner(edges, pos, durations)
    
    def schedule_task(self, start_node, end_node):
        options =  self.path_planner.plan_task(start_node, end_node, self.agent_locations)
        return options



option_number = 1
durations = {
        "MOVE_DURATION": 5,
        "PICKUP_DURATION": 13,
        "DROPOFF_DURATION": 13,
        "TURN_DURATION": 4
 }

run_all = False
possibility_count = 0

if run_all:
    all_nodes = GraphOptions.OPTIONS[option_number]["positions"].keys()

    for agent_1_location in all_nodes:
        for agent_2_location in all_nodes:
            if agent_1_location == agent_2_location:
                continue
            agents = {
                "192.168.1.10": {"node": agent_1_location, "facing_direction": 0},
                "192.168.1.20": {"node": agent_2_location, "facing_direction": 0},
                }
            t = TimeCalculator(option_number, durations, agents)
            for start_location in all_nodes:
                for end_location in all_nodes:
                    if start_location == end_location or start_location == agent_1_location or start_location == agent_2_location or end_location == agent_1_location or end_location == agent_2_location:
                        continue
                    possibility_count += 1
                    options = t.schedule_task(start_location, end_location)
                    task_eval = []
                    has_single_agv_option = False
                    for option in options:
                        agents_involved = len(list(set(t["name"] for t in options[option])))
                        task_eval.append({"agents_involved": agents_involved, "end_time": options[option][-1]["end_time"]})
                        if agents_involved == 1:
                            has_single_agv_option = True
                    min_end_time = float('inf')
                    agents_involved = 0
                    for option in task_eval:
                        if option["end_time"] < min_end_time:
                            min_end_time = option["end_time"]
                            agents_involved = option["agents_involved"]
                    
                    if agents_involved == len(agents.keys()) and has_single_agv_option:
                        print(task_eval)

                        print(f"Start: {start_location}, End: {end_location}, Agent 1 Start Location: {agent_1_location}, Agent 2 Start Location: {agent_2_location}, Agents Involved: {agents_involved}, Min End Time: {min_end_time}")

    print(possibility_count)
else:
    agents = {
                "192.168.1.10": {"node": "A", "facing_direction": 0},
                "192.168.1.20": {"node": "G", "facing_direction": 0},
                }
    t = TimeCalculator(option_number, durations, agents)
    options = t.schedule_task("B", "D")
    pprint(options)
    
                    
        
