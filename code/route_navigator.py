import networkx as nx

class RouteNavigator:
    def __init__(self, edges, pos, location, robot_facing_direction):
        """
        Initializes the positions of the nodes and the connection actions
        """
        self.edges = edges
        self.pos = pos
        self.location = location
        self.robot_facing_direction = robot_facing_direction
        self.G = nx.Graph()
        self.G.add_edges_from(self.edges)
    
    def get_turns(self, target, path=None):
        """
        Calculates the turns the robot as to do at every node to reach the target
        """
        if path is None:
            path = nx.shortest_path(self.G, source=self.location, target=target)
        directions = {}

        for i in range(len(path) - 1):
            current_node = path[i]
            next_node = path[i + 1]
            
            current_coordinates = self.pos[current_node]
            next_coordinates = self.pos[next_node]
            
            delta_x = next_coordinates[0] - current_coordinates[0]
            delta_y = next_coordinates[1] - current_coordinates[1]
            
            if delta_x > 0 and delta_y == 0:
                if self.robot_facing_direction == 0:
                    directions[current_node] = 0
                elif self.robot_facing_direction == 90:
                    directions[current_node] = -90
                    self.robot_facing_direction = 0
                elif self.robot_facing_direction == 180:
                    directions[current_node] = -180
                    self.robot_facing_direction = 0
                elif self.robot_facing_direction == 270:
                    directions[current_node] = 90
                    self.robot_facing_direction = 0

            elif delta_x < 0 and delta_y == 0:
                if self.robot_facing_direction == 0:
                    directions[current_node] = 180
                    self.robot_facing_direction = 180
                elif self.robot_facing_direction == 90:
                    directions[current_node] = 90
                    self.robot_facing_direction = 180
                elif self.robot_facing_direction == 180:
                    directions[current_node] = 0
                elif self.robot_facing_direction == 270:
                    directions[current_node] = -90
                    self.robot_facing_direction = 180

            elif delta_y > 0 and delta_x == 0:
                if self.robot_facing_direction == 0:
                    directions[current_node] = 90
                    self.robot_facing_direction = 90
                elif self.robot_facing_direction == 90:
                    directions[current_node] = 0
                elif self.robot_facing_direction == 180:
                    directions[current_node] = -90
                    self.robot_facing_direction = 90
                elif self.robot_facing_direction == 270:
                    directions[current_node] = -180
                    self.robot_facing_direction = 90

            elif delta_y < 0 and delta_x == 0:
                if self.robot_facing_direction == 0:
                    directions[current_node] = -90
                    self.robot_facing_direction = 270
                elif self.robot_facing_direction == 90:
                    directions[current_node] = 180
                    self.robot_facing_direction = 270
                elif self.robot_facing_direction == 180:
                    directions[current_node] = 90
                    self.robot_facing_direction = 270
                elif self.robot_facing_direction == 270:
                    directions[current_node] = 0
        self.location = target
        initial_turn = directions[path[0]] if path[0] in directions else 0
        return directions, initial_turn

    def getFacingDirection(self):
        """
        Returns the facing direction of the robot
        """
        return self.robot_facing_direction