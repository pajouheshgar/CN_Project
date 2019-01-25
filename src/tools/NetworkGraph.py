import time
import queue


class GraphNode:
    def __init__(self, address):
        """

        :param address: (ip, port)
        :type address: tuple

        """
        self.address = address
        self.left_child = None
        self.right_child = None
        self.parent = None
        self.alive = True
        self.reunion_timer = 0
        pass

    def set_parent(self, parent):
        self.parent = parent

    def set_address(self, new_address):
        self.address = new_address

    def __reset(self):
        print("FUCK KHAJE POOR")

    def add_child(self, child):
        if self.left_child is None:
            self.left_child = child
            child.set_parent(self)
        elif self.right_child is None:
            self.right_child = child
            child.set_parent(self)
        else:
            raise Exception(self, "has no free room for new child")

    def get_n_childs(self):
        n = 0
        if self.left_child is None:
            n += 1
        if self.right_child is None:
            n += 1
        return 2 - n

    def has_free_child(self):
        return self.get_n_childs() < 2

    def get_childs(self):
        childs = []
        if self.left_child is not None:
            childs.append(self.left_child)
        if self.right_child is not None:
            childs.append(self.right_child)
        return childs


class NetworkGraph:
    def __init__(self, root):
        self.root = root
        root.alive = True
        self.nodes = [root]

    def find_live_node(self, sender):
        """
        Here we should find a neighbour for the sender.
        Best neighbour is the node who is nearest the root and has not more than one child.

        Code design suggestion:
            1. Do a BFS algorithm to find the target.

        Warnings:
            1. Check whether there is sender node in our NetworkGraph or not; if exist do not return sender node or
               any other nodes in it's sub-tree.

        :param sender: The node address we want to find best neighbour for it.
        :type sender: tuple

        :return: Best neighbour for sender.
        :rtype: GraphNode
        """
        q = queue.Queue()
        q.put(self.root)
        while True:
            lq = q.get()
            if not lq.alive:
                continue
            if lq.has_free_child():
                return lq
            for clq in lq.get_childs():
                q.put(clq)

    def find_node(self, ip, port):
        for node in self.nodes:
            if node.address == (ip, port):
                return node
        return None

    def turn_on_node(self, node_address):
        node = self.find_node(node_address[0], node_address[1])
        if node is None:
            return
        node.alive = True

    def turn_off_node(self, node_address):
        node = self.find_node(node_address[0], node_address[1])
        if node is None:
            return
        node.alive = False
        node.parent = None
        for child_node in node.get_childs():
            self.turn_off_node(child_node.address)
            node.left_child = None
            node.right_child = None

    def remove_node(self, node_address):
        node_to_be_removed = self.find_node(node_address[0], node_address[1])
        if node_to_be_removed is None:
            return
        if node_to_be_removed.parent is not None:
            if node_to_be_removed == node_to_be_removed.parent.left_child:
                node_to_be_removed.parent.left_child = None
            else:
                node_to_be_removed.parent.right_child = None
        for child_node in node_to_be_removed.get_childs():
            self.remove_node(child_node.address)

        node_to_be_removed.parent = None
        self.nodes.remove(node_to_be_removed)

    def add_node(self, ip, port, father_address):
        """
        Add a new node with node_address if it does not exist in our NetworkGraph and set its father.

        Warnings:
            1. Don't forget to set the new node as one of the father_address children.
            2. Before using this function make sure that there is a node which has father_address.

        :param ip: IP address of the new node.
        :param port: Port of the new node.
        :param father_address: Father address of the new node

        :type ip: str
        :type port: int
        :type father_address: tuple


        :return:
        """
        check_node = self.find_node(ip, port)
        if check_node is not None:
            node = check_node
        else:
            node = GraphNode((ip, port))
        self.nodes.append(node)
        father_node = self.find_node(father_address[0], father_address[1])
        node.set_parent(father_node)
        father_node.add_child(node)

    def find_new_parent_for_node(self, node_address):
        node_to_be_readopted = self.find_node(node_address[0], node_address[1])
        if node_to_be_readopted is None:
            return
        self.remove_node(node_to_be_readopted)
        new_parent_node = self.find_live_node("FUCK KHAJE POOR")
        self.add_node(node_address[0], node_address[1], new_parent_node.address)
        return new_parent_node
