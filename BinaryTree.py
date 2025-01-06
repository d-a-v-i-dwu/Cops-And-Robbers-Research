from Nodes import Node
import random
import networkx as nx 
import matplotlib.pyplot as plt

class BinaryTree():
    def __init__(self, height: int = 5, density: float = 1):
        self.root = Node()

        self.height = height

        self.visual = []
        self.tree_constructor(height, density)
    
    
    def tree_constructor(self, height: int, density: float):
        # The root is already generated with value 0 and depth 0
        current_value = 1
        current_depth = 1

        previous_row = [self.root]

        # If given height 0, only the root exists
        for row in range(0, height):
            new_row = []

            for node in previous_row:

                # Since the tree must be the given height, there will be one sequence of parent-child vertices that is that height. As it's arbitrary,
                # let it be the left-most sequence of nodes. The rest of the tree is generated randomly according to the density. 
                if node == previous_row[0] or random.random() < density:
                    l_child = Node(current_value, current_depth, node)
                    node.set_l_child(l_child)
                    self.visual.append([f"v:{node.get_value()} d:{node.get_depth()}", f"v:{l_child.get_value()} d:{l_child.get_depth()}"])
                    new_row.append(l_child)
                    current_value += 1

                if random.random() < density:
                    r_child = Node(current_value, current_depth, node)
                    node.set_r_child(r_child)
                    self.visual.append([f"v:{node.get_value()} d:{node.get_depth()}", f"v:{r_child.get_value()} d:{r_child.get_depth()}"])
                    new_row.append(r_child)
                    current_value += 1

            previous_row = new_row
            current_depth += 1


    def get_root(self) -> Node: return self.root
    def get_height(self) -> int: return self.height

    def visualize(self):
        G = nx.Graph() 
        G.add_edges_from(self.visual) 
        nx.draw_networkx(G) 
        plt.show() 