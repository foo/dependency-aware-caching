class BinaryTree:
    def __init__(self, height):
        self.height = height
        root_node = Node(Node(None, 0, 0), 1, 1)
        self.nodes = [root_node,]
        self.create_tree()
        self.calculate_topo_order()

    def create_tree(self):
        node_counter = 2
        next_parents = [self.nodes[0], self.nodes[0]]
        while True:
            parent_node = next_parents.pop(0)
            if (parent_node.get_height() == self.height):
                break
            new_node = Node(parent_node, node_counter,
                            parent_node.get_height() + 1)
            parent_node.add_child(new_node)
            node_counter += 1
            next_parents.append(new_node)
            next_parents.append(new_node)
            self.nodes.append(new_node)

    def calculate_topo_order(self):
        n = len(self.nodes)
        for node in self.nodes:
            node.topo_order = n - node.idx

    def get_size(self):
        return len(self.nodes)


class Node:
    def __init__(self, parent_node, idx, height):
        self.parent_node = parent_node
        self.idx = idx
        self.height = height
        self.child_nodes = []
        self.topo_order = None
        self.size = 0

    def get_height(self):
        return self.height

    def add_child(self, node):
        self.child_nodes.append(node)
        return

    def get_subtree(self):
        T = [self]
        for child in self.child_nodes:
            T_child = child.get_subtree()
            T = T + T_child
        return T

    def get_size(self):
        if self.size != 0:
            return self.size
        else:
            self.size = len(self.get_subtree())
            return self.size

    def __str__(self):
        return f'<Node {self.idx}, Height: {self.height},\
                Parent Node: {self.parent_node.idx},\
                Child Nodes: {list(map(lambda x: x.idx, self.child_nodes))}>'

    def __repr__(self):
        return f'<Node {self.idx}, Height: {self.height},\
                Parent Node: {self.parent_node.idx},\
                Child Nodes: {list(map(lambda x: x.idx, self.child_nodes))}>'
