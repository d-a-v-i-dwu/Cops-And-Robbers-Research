from typing import Optional, Self
import random


class Node:
    def __init__(self, value: int = 0, depth: int = 0, parent: Self = None):
        self.value = value
        self.depth = depth
        self.parent = parent
        self.l_child = None
        self.r_child = None
    
    def get_value(self) -> int: return self.value

    def get_depth(self) -> int: return self.depth

    def get_parent(self) -> Optional[Self]: return self.parent

    def set_l_child(self, node: Self): self.l_child = node
    def get_l_child(self) -> Optional[Self]: return self.l_child

    def set_r_child(self, node: Self): self.r_child = node
    def get_r_child(self) -> Optional[Self]: return self.r_child

    def __str__(self):
        parent_value = self.parent.get_value() if self.parent else 'None'
        l_child_value = self.l_child.get_value() if self.l_child else 'None'
        r_child_value = self.r_child.get_value() if self.r_child else 'None'
        return f"(value: {self.value}, parent: {parent_value}, l_child: {l_child_value}, r_child: {r_child_value})"

    def __repr__(self):
        return str(self)


class InfinityNode():
    node_count = 0

    def __init__(self, neighbour: Self = None, max_degree: int = 3, min_degree: int = 3):
        self.value = InfinityNode.node_count
        InfinityNode.node_count += 1

        self.visited = False
        self.max_degree = max_degree
        self.min_degree = min_degree

        if not neighbour:
            self.neighbours = []
            self.visit()
        else:
            self.neighbours = [neighbour]

    def visit(self):
        if not self.visited:
            self.visited = True
            self.generate_neighbours()
    
    def generate_neighbours(self):
        for i in range(len(self.neighbours), random.randint(self.min_degree, max(self.min_degree, self.max_degree - len(self.neighbours) - 1))):
            self.neighbours.append(InfinityNode(self, self.max_degree, self.min_degree))
    
    def get_neighbours(self): return self.neighbours

    def __str__(self):
        return f"(value: {self.value}, neighbours: {self.get_neighbours()})"

    def __repr__(self):
        return str(self.value)