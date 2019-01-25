from src.tools.simpletcp.clientsocket import ClientSocket


class Node:
    def __init__(self, server_address, set_root=False, set_register=False):
        """
        The Node object constructor.

        This object is our low-level abstraction for other peers in the network.
        Every node has a ClientSocket that should bind to the Node TCPServer address.

        Warnings:
            1. Insert an exception handler when initializing the ClientSocket; when a socket closed here we will face to
               an exception and we should detach this Node and clear its output buffer.

        :param server_address:
        :param set_root:
        :param set_register:
        """
        self.is_root = set_root
        self.is_registered = set_register
        self.server_ip = Node.parse_ip(server_address[0])
        self.server_port = Node.parse_port(server_address[1])

        print("New Node Created\n\tServer Address: ", server_address)
        print(self.server_ip, self.server_port)

        try:
            self.client = ClientSocket(mode=server_address[0], port=int(server_address[1]), single_use='False')
        except:
            raise ConnectionRefusedError
        self.out_buff = []
        self.in_buff = []

    def send_message(self):
        """
        Final function to send buffer to the client's socket.

        :return:
        """
        for data in self.out_buff:
            rcvd_data = self.client.send(data)
            self.in_buff.append(rcvd_data)
        self.out_buff = []

    def add_message_to_out_buff(self, message):
        """
        Here we will add a new message to the server out_buff, then in 'send_message' will send them.

        :param message: The message we want to add to out_buff
        :return:
        """
        self.out_buff.append(message)

    def close(self):
        """
        Closing client's object.
        :return:
        """
        self.client.close()

    def get_server_address(self):
        """

        :return: Server address in a pretty format.
        :rtype: tuple
        """
        return self.server_ip, self.server_port

    @staticmethod
    def parse_ip(ip):
        """
        Automatically change the input IP format like '192.168.001.001'.
        :param ip: Input IP
        :type ip: str

        :return: Formatted IP
        :rtype: str
        """
        return '.'.join(str(int(part)).zfill(3) for part in ip.split('.'))

    @staticmethod
    def parse_port(port):
        """
        Automatically change the input IP format like '05335'.
        :param port: Input IP
        :type port: str

        :return: Formatted IP
        :rtype: str
        """
        return str(int(port)).zfill(5)


if __name__ == "__main__":
    N = Node(("127.0.0.1", "312"))
