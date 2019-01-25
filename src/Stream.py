from src.tools.simpletcp.tcpserver import TCPServer

from src.tools.Node import Node
import threading


class Stream:

    def __init__(self, ip, port):
        """
        The Stream object constructor.

        Code design suggestion:
            1. Make a separate Thread for your TCPServer and start immediately.


        :param ip: 15 characters
        :param port: 5 characters
        """

        self.ip = Node.parse_ip(ip)
        self.port = Node.parse_port(port)
        self.nodes_list = []
        self._server_in_buf = []

        def callback(address, queue, data):
            """
            The callback function will run when a new data received from server_buffer.

            :param address: Source address.
            :param queue: Response queue.
            :param data: The data received from the socket.
            :return:
            """
            queue.put(bytes('ACK', 'utf8'))
            self._server_in_buf.append(data)

        self.tcp_server = TCPServer(self.ip, int(self.port), callback)
        self.tcp_server.start()

    def get_server_address(self):
        """

        :return: Our TCPServer address
        :rtype: tuple
        """
        return self.ip, self.port

    def clear_in_buff(self):
        """
        Discard any data in TCPServer input buffer.

        :return:
        """
        self._server_in_buf.clear()

    def add_node(self, server_address, set_register_connection=False):
        """
        Will add new a node to our Stream.

        :param server_address: New node TCPServer address.
        :param set_register_connection: Shows that is this connection a register_connection or not.

        :type server_address: tuple
        :type set_register_connection: bool

        :return:
        """
        ip = server_address[0]
        port = server_address[1]
        found_node = self.get_node_by_server(ip, port)
        if found_node is not None:
            print("({}, {}) is a Duplicate node".format(ip, port))
        try:
            added_node = Node(server_address, set_register=set_register_connection)
            self.nodes_list.append(added_node)
        except ConnectionRefusedError:
            print("Nothing is bound to node's server address")

    def remove_node(self, node):
        """
        Remove the node from our Stream.

        Warnings:
            1. Close the node after deletion.

        :param node: The node we want to remove.
        :type node: Node

        :return:
        """
        self.nodes_list.remove(node)
        node.close()

    def get_node_by_server(self, ip, port):
        """

        Will find the node that has IP/Port address of input.

        Warnings:
            1. Before comparing the address parse it to a standard format with Node.parse_### functions.

        :param ip: input address IP
        :param port: input address Port

        :return: The node that input address.
        :rtype: Node
        """
        ip = Node.parse_ip(ip)
        port = Node.parse_port(port)
        for node in self.nodes_list:
            if node.server_ip == ip and node.server_port == port:
                return node
        return None

    def add_message_to_out_buff(self, address, message):
        """
        In this function, we will add the message to the output buffer of the node that has the input address.
        Later we should use send_out_buf_messages to send these buffers into their sockets.

        :param address: Node address that we want to send the message
        :param message: Message we want to send

        Warnings:
            1. Check whether the node address is in our nodes or not.

        :return:
        """
        ip = address[0]
        port = address[1]
        node = self.get_node_by_server(ip, port)
        if node is None:
            print("This stream doesn't have a node with ({},{}) address".format(ip, port))
            return
        node.add_message_to_out_buff(message)

    def read_in_buf(self):
        """
        Only returns the input buffer of our TCPServer.

        :return: TCPServer input buffer.
        :rtype: list
        """
        return self._server_in_buf

    def send_messages_to_node(self, node):
        """
        Send buffered messages to the 'node'

        Warnings:
            1. Insert an exception handler here; Maybe the node socket you want to send the message has turned off and
            you need to remove this node from stream nodes.

        :param node:
        :type node Node

        :return:
        """
        if node not in self.nodes_list:
            print("Node not found")
            return
        try:
            node.send_message()
        except:
            print("Node {} didn't work properly and got removed from stream".format(node))
            self.remove_node(node)

    def send_out_buf_messages(self, only_register=False):
        """
        In this function, we will send hole out buffers to their own clients.

        :return:
        """
        for node in self.nodes_list:
            if not only_register or node.is_registered:
                self.send_messages_to_node(node)
