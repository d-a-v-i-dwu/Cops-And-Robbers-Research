from Nodes import Node, InfinityNode
from collections import deque
import random

class Player:
    def __init__(self, starting_node, tipsiness, tree_height):
        self.current_node = starting_node
        self.tipsiness = tipsiness
        self.tree_height = tree_height
    
    def get_node(self) -> Node: return self.current_node
    def set_node(self, node: Node): self.current_node = node

    def find_other_player(self, target_node: Node):
        q = deque()
        visited = [None for i in range(2 ** self.tree_height - 1)]

        visited[self.current_node.get_value()] = -1
        q.append(self.current_node)

        not_found = True

        while q and not_found:
            temp_node = q.popleft()
            # temp_node_val = temp_node.get_value()
            # print(f"temp val {temp_node_val}")
            
            if temp_node.get_parent():
                parent = temp_node.get_parent()

                # print(f"parent {parent.get_value()}")
                
                not_found = self.node_checker(parent, target_node, temp_node, q, visited)
            
            l_child = temp_node.get_l_child()
            if l_child and not_found:
                
                # print(f"l_child {l_child.get_value()}")

                not_found = self.node_checker(l_child, target_node, temp_node, q, visited)

            r_child = temp_node.get_r_child()
            if r_child and not_found:
                
                # print(f"r_child {r_child.get_value()}")
                
                not_found = self.node_checker(r_child, target_node, temp_node, q, visited)

        path = [target_node]
        curr = visited[target_node.get_value()]

        while curr != -1:
            curr_idx = curr.get_value()
            path.append(curr)
            curr = visited[curr_idx]
        
        return path[::-1][1:]

    def node_checker(self, node: Node, target_node: Node, prev_node: Node, q: deque, visited: list) -> bool:
        node_val = node.get_value()
        if visited[node_val] == None:
            visited[node_val] = prev_node
            if node == target_node:
                return False
            q.append(node)
        return True

    def drunken_move(self):
        neighbouring_nodes = [node for node in [self.current_node.get_parent(), self.current_node.get_l_child(), self.current_node.get_r_child()] if node is not None]
        self.current_node = neighbouring_nodes[random.randrange(0, len(neighbouring_nodes))]


class Cop(Player):
    def __init__(self, starting_node: Node, tipsiness: float = 0, tree_height: int = 5):
        super().__init__(starting_node, tipsiness, tree_height)
    
    def greedy_move(self, target_node: Node) -> bool:
        if random.random() < self.tipsiness:
            self.drunken_move()

            if self.current_node == target_node:
                return True
            return False

        path = self.find_other_player(target_node)
        if len(path) > 1:
            self.current_node = path[0]
            return False
        else:
            if path:
                self.current_node = path[0]
            return True

class Robber(Player):
    def __init__(self, starting_node: Node, tipsiness: float = 0, tree_height: int = 5):
        super().__init__(starting_node, tipsiness, tree_height)
    
    def greedy_move(self, cop_node: Node) -> bool:
        if random.random() < self.tipsiness:
            self.drunken_move()

            if self.current_node == cop_node:
                return True
            return False

        self.current_node = self.current_node.get_l_child() if self.current_node.get_l_child() else self.current_node
        return False

    def optimal_move(self, cop_node: Node) -> bool:
        if random.random() < self.tipsiness:
            self.drunken_move()

            if self.current_node == cop_node:
                return True
            return False
        
        path = self.find_other_player(cop_node)

        current_parent = self.current_node.get_parent()

        if current_parent and path[0] != current_parent:
            self.current_node = current_parent


        # If at the root and the cop is two moves away, stay at the root. Otherwise move to the other child.
        if not current_parent:
            if len(path) <= 1:
                self.current_node = self.current_node.get_r_child() if path[0] == self.current_node.get_l_child() else self.current_node.get_l_child()

        # If not at the root and the distance is within two, move down the tree.
        elif len(path) <= 2 and path[0] == current_parent:
            self.current_node = self.current_node.get_l_child() if self.current_node.get_l_child() else self.current_node

        # If not at the root and the distance is greater than two, move up the tree.
        else:
            self.current_node = current_parent
        
        return False




class InfinityPlayer():
    def __init__(self, starting_node: InfinityNode, tipsiness: float = 0):
        self.current_node = starting_node
        self.tipsiness = tipsiness

    def get_node(self) -> InfinityNode: return self.current_node
    def set_node(self, node: InfinityNode): self.current_node = node

    def find_other_player(self, target_node: InfinityNode):
        nodes = [self.current_node]
        predecessors = [-1]

        idx = 0
        not_found = True

        while idx <= len(nodes) and not_found:
            temp_node = nodes[idx]
            temp_neighbours = temp_node.get_neighbours()

            predecessor = idx

            for node in temp_neighbours:
                if node not in nodes:
                    nodes.append(node)
                    predecessors.append(predecessor)

                    if node == target_node:
                        not_found = False
                        break
            
            idx += 1

        path_indices = [predecessors[-1]]
        while predecessors[path_indices[-1]] != -1:
            path_indices.append(predecessors[path_indices[-1]])
        
        path = []

        for i in path_indices:
            path.append(nodes[i])

        path = path[::-1][1:]
        path.append(nodes[-1])

        return path
    
    def drunken_move(self):
        neighbours = self.current_node.get_neighbours()
        self.current_node = neighbours[random.randint(0, len(neighbours) - 1)]
        self.current_node.visit()


class InfinityCop(InfinityPlayer):
    def __init__(self, starting_node: InfinityNode, tipsiness: float = 0):
        super().__init__(starting_node, tipsiness)
    
    def greedy_move(self, robber_node: InfinityNode):
        if random.random() < self.tipsiness:
            self.drunken_move()

            if self.current_node == robber_node:
                return True
            return False

        path = self.find_other_player(robber_node)

        if len(path) > 1:
            self.current_node = path[0]
            self.current_node.visit()
            return False
        else:
            if path:
                self.current_node = path[0]
            return True


class InfinityRobber(InfinityPlayer):
    def __init__(self, starting_node: InfinityNode, tipsiness: float = 0):
        super().__init__(starting_node, tipsiness)
    
    def greedy_move(self, cop_node: InfinityNode):
        if random.random() < self.tipsiness:
            self.drunken_move()

            if self.current_node == cop_node:
                return True
            return False

        path = self.find_other_player(cop_node)
        
        for neighbour in self.current_node.get_neighbours():
            if neighbour != path[0]:
                self.current_node = neighbour
                self.current_node.visit()
                break