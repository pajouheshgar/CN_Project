from src.Stream import Stream
from src.Packet import Packet, PacketFactory
from src.UserInterface import UserInterface
from src.tools.Node import Node
from src.tools.NetworkGraph import NetworkGraph, GraphNode
import time
import datetime
import threading

"""
    Peer is our main object in this project.
    In this network Peers will connect together to make a tree graph.
    This network is not completely decentralised but will show you some real-world challenges in Peer to Peer networks.
    
"""


class Peer(threading.Thread):
    def __init__(self, server_ip, server_port, is_root=False, root_address=None):
        """
        The Peer object constructor.

        Code design suggestions:
            1. Initialise a Stream object for our Peer.
            2. Initialise a PacketFactory object.
            3. Initialise our UserInterface for interaction with user commandline.
            4. Initialise a Thread for handling reunion daemon.

        Warnings:
            1. For root Peer, we need a NetworkGraph object.
            2. In root Peer, start reunion daemon as soon as possible.
            3. In client Peer, we need to connect to the root of the network, Don't forget to set this connection
               as a register_connection.


        :param server_ip: Server IP address for this Peer that should be pass to Stream.
        :param server_port: Server Port address for this Peer that should be pass to Stream.
        :param is_root: Specify that is this Peer root or not.
        :param root_address: Root IP/Port address if we are a client.

        :type server_ip: str
        :type server_port: int
        :type is_root: bool
        :type root_address: tuple
        """
        super().__init__()
        self.server_ip = Node.parse_ip(server_ip)
        self.server_port = Node.parse_port(str(server_port))
        self.server_address = (self.server_ip, self.server_port)
        self.stream = Stream(self.server_ip, self.server_port)
        self.UI = UserInterface()

        self.is_root = is_root
        self.left_child_address, self.right_child_address, self.parent_address = None, None, None

        if self.is_root:
            self.registered_peers_address = {}
            self.root_ip, self.root_port = self.server_ip, self.server_port
            self.root_node = GraphNode((self.root_ip, self.root_port))
            self.graph = NetworkGraph(self.root_node)

        else:
            self.root_ip = Node.parse_ip(root_address[0])
            self.root_port = Node.parse_ip(str(root_address[1]))

        self.root_address = (self.root_ip, self.root_port)

        self.running = True
        self.registered = False
        self.advertised = False
        self.joined = False
        self.reunion_on_fly = False
        self.reunion_timer = 0
        self.counter = 0
        self.timer_interval = 0.2
        self.UI.start()
        self.start()

    def start_user_interface(self):
        """
        For starting UserInterface thread.

        :return:
        """
        self.print_function("FUCK KHAJE POOR")

    def handle_user_interface_buffer(self):
        """
        In every interval, we should parse user command that buffered from our UserInterface.
        All of the valid commands are listed below:
            1. Register:  With this command, the client send a Register Request packet to the root of the network.
            2. Advertise: Send an Advertise Request to the root of the network for finding first hope.
            3. SendMessage: The following string will be added to a new Message packet and broadcast through the network.

        Warnings:
            1. Ignore irregular commands from the user.
            2. Don't forget to clear our UserInterface buffer.
        :return:
        """
        for command in self.UI.buffer:
            self.handle_user_command(command)
        self.UI.clear_buffer()

    def handle_user_command(self, command):
        """

        :param command:
        :type command: str
        :return:
        """
        command = command.lower()
        if command.startswith("register"):
            if self.registered:
                self.print_function("You have been registered before and FUCK KHAJE POOR")
            else:
                register_req_packet = PacketFactory.new_register_packet(type='REQ',
                                                                        source_server_address=self.server_address,
                                                                        address=self.root_address)
                # Adding root node to peer's stream
                self.stream.add_node(server_address=self.root_address, set_register_connection=True)
                self.stream.add_message_to_out_buff(address=self.root_address, message=register_req_packet.buf)
                self.print_function("{} sent register request".format(self.server_address))
        elif command.startswith("advertise"):
            if not self.registered:
                self.print_function("{} must register first to advertise".format(str(self.server_address)))
            elif self.advertised:
                self.print_function("You have advertised before")
            else:
                advertise_req_packet = PacketFactory.new_advertise_packet(type='REQ',
                                                                          source_server_address=self.server_address)
                self.stream.add_message_to_out_buff(address=self.root_address, message=advertise_req_packet.buf)
                self.print_function("{} sent advertise packet".format(str(self.server_address)))

        elif command.startswith("message"):
            if self.joined:
                message = command[8:]
                broadcast_message_packet = PacketFactory.new_message_packet(message=message,
                                                                            source_server_address=self.server_address)
                self.print_function("{} is broadcasting message: {}".format(str(self.server_address), message))
                self.send_broadcast_packet(broadcast_message_packet, "FUCK KHAJE POOR")
            else:
                self.print_function("You must join the network before broadcasting a message")
        elif command.startswith('disconnect'):
            self.running = False
        else:
            self.print_function("Unknown command received: {}".format(command))

    def run(self):
        """
        The main loop of the program.

        Code design suggestions:
            1. Parse server in_buf of the stream.
            2. Handle all packets were received from our Stream server.
            3. Parse user_interface_buffer to make message packets.
            4. Send packets stored in nodes buffer of our Stream object.
            5. ** sleep the current thread for 2 seconds **

        Warnings:
            1. At first check reunion daemon condition; Maybe we have a problem in this time
               and so we should hold any actions until Reunion acceptance.
            2. In every situation checkout Advertise Response packets; even is Reunion in failure mode or not

        :return:
        """
        while True:
            if self.is_root:
                pass
            else:
                pass

            if self.counter > 0 or True:
                received_bufs = self.stream.read_in_buf()
                received_packets = [PacketFactory.parse_buffer(buf) for buf in received_bufs]
                for packet in received_packets:
                    self.handle_packet(packet)

                self.stream.clear_in_buff()
                self.stream.send_out_buf_messages()
                self.handle_user_interface_buffer()

            if self.reunion_timer == 0 and self.joined and not self.reunion_on_fly:
                self.reunion_on_fly = True
                reunion_req_packet = PacketFactory.new_reunion_packet(type='REQ', source_address=self.server_address,
                                                                      nodes_array=[self.server_address])
                self.stream.add_message_to_out_buff(address=self.parent_address, message=reunion_req_packet.buf)
                self.print_function("Sent Reunion Packet to Parent: " + str(self.parent_address))

            if not self.reunion_on_fly and self.reunion_timer > 0:
                self.reunion_timer -= self.timer_interval * 10

            self.counter += self.timer_interval * 10
            if self.counter == 4 * 10:
                self.counter = 0
            if self.is_root:
                for gnode in self.graph.nodes:
                    gnode.reunion_timer += self.timer_interval * 10
            time.sleep(self.timer_interval)

    def run_reunion_daemon(self):
        """

        In this function, we will handle all Reunion actions.

        Code design suggestions:
            1. Check if we are the network root or not; The actions are identical.
            2. If it's the root Peer, in every interval check the latest Reunion packet arrival time from every node;
               If time is over for the node turn it off (Maybe you need to remove it from our NetworkGraph).
            3. If it's a non-root peer split the actions by considering whether we are waiting for Reunion Hello Back
               Packet or it's the time to send new Reunion Hello packet.

        Warnings:
            1. If we are the root of the network in the situation that we want to turn a node off, make sure that you will not
               advertise the nodes sub-tree in our GraphNode.
            2. If we are a non-root Peer, save the time when you have sent your last Reunion Hello packet; You need this
               time for checking whether the Reunion was failed or not.
            3. For choosing time intervals you should wait until Reunion Hello or Reunion Hello Back arrival,
               pay attention that our NetworkGraph depth will not be bigger than 8. (Do not forget main loop sleep time)
            4. Suppose that you are a non-root Peer and Reunion was failed, In this time you should make a new Advertise
               Request packet and send it through your register_connection to the root; Don't forget to send this packet
               here, because in the Reunion Failure mode our main loop will not work properly and everything will be got stock!

        :return:
        """
        self.print_function("FUCK KHAJE POOR")

    def send_broadcast_packet(self, broadcast_packet, exclude_address):
        """

        For setting broadcast packets buffer into Nodes out_buff.

        Warnings:
            1. Don't send Message packets through register_connections.

        :param broadcast_packet: The packet that should be broadcast through the network.
        :type broadcast_packet: Packet

        :return:
        """
        if self.parent_address is not None and self.parent_address != exclude_address:
            self.stream.add_message_to_out_buff(self.parent_address, broadcast_packet.buf)
        if self.left_child_address is not None and self.left_child_address != exclude_address:
            self.stream.add_message_to_out_buff(self.left_child_address, broadcast_packet.buf)
        if self.right_child_address is not None and self.right_child_address != exclude_address:
            self.stream.add_message_to_out_buff(self.right_child_address, broadcast_packet.buf)

    def handle_packet(self, packet):
        """

        This function act as a wrapper for other handle_###_packet methods to handle the packet.

        Code design suggestion:
            1. It's better to check packet validation right now; For example Validation of the packet length.

        :param packet: The arrived packet that should be handled.

        :type packet Packet

        """
        packet_type = packet.get_type()
        # if self.is_root:
        #     self.print_function("root received type {} message".format(packet_type))
        if packet_type == 1:
            self.__handle_register_packet(packet)
        elif packet_type == 2:
            self.__handle_advertise_packet(packet)
        elif packet_type == 3:
            self.__handle_join_packet(packet)
        elif packet_type == 4:
            self.__handle_message_packet(packet)
        elif packet_type == 5:
            self.__handle_reunion_packet(packet)
        else:
            self.print_function("Unknown type of packet received {}".format(packet.get_body()))

    def __check_registered(self, source_address):
        """
        If the Peer is the root of the network we need to find that is a node registered or not.

        :param source_address: Unknown IP/Port address.
        :type source_address: tuple

        :return:
        """
        if source_address in self.registered_peers_address:
            return True
        return False

    def __handle_advertise_packet(self, packet):
        """
        For advertising peers in the network, It is peer discovery message.

        Request:
            We should act as the root of the network and reply with a neighbour address in a new Advertise Response packet.

        Response:
            When an Advertise Response packet type arrived we should update our parent peer and send a Join packet to the
            new parent.

        Code design suggestion:
            1. Start the Reunion daemon thread when the first Advertise Response packet received.
            2. When an Advertise Response message arrived, make a new Join packet immediately for the advertised address.

        Warnings:
            1. Don't forget to ignore Advertise Request packets when you are a non-root peer.
            2. The addresses which still haven't registered to the network can not request any peer discovery message.
            3. Maybe it's not the first time that the source of the packet sends Advertise Request message. This will happen
               in rare situations like Reunion Failure. Pay attention, don't advertise the address to the packet sender
               sub-tree.
            4. When an Advertise Response packet arrived update our Peer parent for sending Reunion Packets.

        :param packet: Arrived register packet

        :type packet Packet

        :return:
        """
        if self.is_root:
            self.__handle_advertise_packet_root(packet)
        else:
            self.__handle_advertise_packet_client(packet)

    def __handle_advertise_packet_root(self, packet):
        if packet.get_body()[:3] == "REQ":
            packet_source_address = packet.get_source_server_address()
            if not self.__check_registered(packet_source_address):
                self.print_function(
                    "Advertise request received from unregistered client {}".format(str(packet_source_address)))
            else:
                if self.graph.find_node(packet_source_address[0], packet_source_address[1]) is not None:
                    self.print_function(
                        "Advertise request received from a client in graph {}".format(str(packet_source_address)))
                else:
                    father_node = self.graph.find_live_node("FUCK KHAJE POOR")
                    print("Father found", father_node.address)
                    self.graph.add_node(ip=packet_source_address[0],
                                        port=packet_source_address[1],
                                        father_address=father_node.address)
                    self.graph.turn_on_node(packet_source_address)
                    register_response_packet = PacketFactory.new_advertise_packet(type='RES',
                                                                                  source_server_address=self.server_address,
                                                                                  neighbour=father_node.address)
                    self.stream.add_message_to_out_buff(address=packet_source_address,
                                                        message=register_response_packet.buf)
                    self.registered_peers_address[packet_source_address] = 1
                    self.print_function(
                        "Advertise request received from {} and register response sent".format(packet_source_address))
        else:
            self.print_function("Root received advertise response. Wtf? FUCK KHAJE POOR")

    def __handle_advertise_packet_client(self, packet):
        if packet.get_body()[:3] == 'RES':
            parent_address = (packet.get_body()[3:18], packet.get_body()[18:23])

            self.advertised = True
            if parent_address != self.root_address:
                self.stream.add_node(server_address=parent_address,
                                     set_register_connection=False)
            join_packet = PacketFactory.new_join_packet(source_server_address=self.server_address)
            self.stream.add_message_to_out_buff(address=parent_address,
                                                message=join_packet.buf)
            self.parent_address = parent_address
            self.joined = True
            self.print_function("Advertise response received from root. Client {} sent join request to {}".format(
                str(self.server_address), str(parent_address)))
        else:
            self.print_function("Client received advertise request. Wtf? FUCK KHAJE POOR")

    def __handle_register_packet(self, packet):
        """
        For registration a new node to the network at first we should make a Node with stream.add_node for'sender' and
        save it.

        Code design suggestion:
            1.For checking whether an address is registered since now or not you can use SemiNode object except Node.

        Warnings:
            1. Don't forget to ignore Register Request packets when you are a non-root peer.

        :param packet: Arrived register packet
        :type packet Packet
        :return:
        """
        if self.is_root:
            self.__handle_register_packet_root(packet)
        else:
            self.__handle_register_packet_client(packet)

    def __handle_register_packet_root(self, packet):
        if packet.get_body()[:3] == "REQ":
            packet_source_address = packet.get_source_server_address()
            if self.__check_registered(packet_source_address):
                self.print_function("Duplicate register request received from {}".format(str(packet_source_address)))
            else:
                self.stream.add_node(server_address=packet_source_address,
                                     set_register_connection=True)
                register_response_packet = PacketFactory.new_register_packet(type='RES',
                                                                             source_server_address=self.server_address)
                self.stream.add_message_to_out_buff(address=packet.get_source_server_address(),
                                                    message=register_response_packet.buf)
                self.registered_peers_address[packet_source_address] = 1
                self.print_function(
                    "Register request received from {} and register response sent".format(packet_source_address))
        else:
            self.print_function("Root received register response. Wtf? FUCK KHAJE POOR")

    def __handle_register_packet_client(self, packet):
        if packet.get_body()[:3] == "RES":
            self.registered = True
            self.print_function("Client {} received register response".format(self.server_address))
        else:
            self.print_function("Client received register request. Wtf? FUCK KHAJE POOR")

    def __check_neighbour(self, address):
        """
        It checks is the address in our neighbours array or not.

        :param address: Unknown address

        :type address: tuple

        :return: Whether is address in our neighbours or not.
        :rtype: bool
        """
        return address == self.parent_address or address == self.left_child_address or address == self.right_child_address

    def __handle_message_packet(self, packet):
        """
        Only broadcast message to the other nodes.

        Warnings:
            1. Do not forget to ignore messages from unknown sources.
            2. Make sure that you are not sending a message to a register_connection.

        :param packet: Arrived message packet

        :type packet Packet

        :return:
        """
        source_address = packet.get_source_server_address()
        if self.__check_neighbour(source_address):
            self.print_function("{} received broadcast message: {}".format(self.server_address, packet.get_body()))
            broadcast_message_packet = PacketFactory.new_message_packet(message=packet.get_body(),
                                                                        source_server_address=self.server_address)
            self.send_broadcast_packet(broadcast_message_packet, exclude_address=source_address)
        else:
            self.print_function("Broadcast packet received from KHAJE POOR. wut??")

    def __handle_reunion_packet(self, packet):
        """
        In this function we should handle Reunion packet was just arrived.

        Reunion Hello:
            If you are root Peer you should answer with a new Reunion Hello Back packet.
            At first extract all addresses in the packet body and append them in descending order to the new packet.
            You should send the new packet to the first address in the arrived packet.
            If you are a non-root Peer append your IP/Port address to the end of the packet and send it to your parent.

        Reunion Hello Back:
            Check that you are the end node or not; If not only remove your IP/Port address and send the packet to the next
            address, otherwise you received your response from the root and everything is fine.

        Warnings:
            1. Every time adding or removing an address from packet don't forget to update Entity Number field.
            2. If you are the root, update last Reunion Hello arrival packet from the sender node and turn it on.
            3. If you are the end node, update your Reunion mode from pending to acceptance.


        :param packet: Arrived reunion packet
        :return:
        """
        source_address = packet.get_source_server_address()
        if not self.__check_neighbour(source_address):
            self.print_function("Reunion packet received from KHAJE POOR. wut??")

    def __handle_reunion_packet_root(self, packet):
        body = packet.get_body()
        if body[:3] == "REQ":
            packet_source_address = packet.get_source_server_address()
            if self.graph.find_node(packet_source_address[0], packet_source_address[1]) is None:
                self.print_function("Root received reunion from {} which is not in graph".format(packet_source_address))
            nodes_address_list = []
            n_nodes = int(body[3:5])
            for i in range(n_nodes):
                ip = body[5 + 20 * i: 5 + 15 + 20 * i]
                port = body[20 + 20 * i: 20 + 5 + 20 * i]
                nodes_address_list.append((ip, port))
            reunion_sender_node = self.graph.find_node(nodes_address_list[0][0], nodes_address_list[0][1])
            self.print_function(
                "Root received Reunion from {} and reunion response sent".format(str(reunion_sender_node)))
            nodes_address_list.reverse()
            reunion_sender_node.reunion_timer = 0
            reunion_response_packet = PacketFactory.new_reunion_packet(type="RES", source_address=self.root_address,
                                                                       nodes_array=nodes_address_list)
            self.stream.add_message_to_out_buff(packet_source_address, message=reunion_response_packet.buf)

        else:
            self.print_function("Root received reunion response. Wtf? FUCK KHAJE POOR")

    def __handle_reunion_packet_client(self, packet):
        body = packet.get_body()
        if not self.joined:
            self.print_function("{} has no parent to redirect reunion request to".format(self.server_address))
            return
        if body[:3] == "REQ":
            nodes_address_list = []
            n_nodes = int(body[3:5])
            for i in range(n_nodes):
                ip = body[5 + 20 * i: 5 + 15 + 20 * i]
                port = body[20 + 20 * i: 20 + 5 + 20 * i]
                nodes_address_list.append((ip, port))
            reunion_sender_node = self.graph.find_node(nodes_address_list[0][0], nodes_address_list[0][1])
            nodes_address_list.append(self.server_address)
            reunion_response_packet = PacketFactory.new_reunion_packet(type="REQ", source_address=self.server_address,
                                                                       nodes_array=nodes_address_list)
            self.stream.add_message_to_out_buff(self.parent_address, message=reunion_response_packet.buf)
            self.print_function(
                "{} received Reunion from {} and reunion request sent to parent".format(str(self.server_address),
                                                                                        str(reunion_sender_node)))
        else:
            n_nodes = int(body[3:5])
            if n_nodes == 1:
                target_ip = body[5:20]
                target_port = body[20:25]
                if (target_ip, target_port) == self.server_address:
                    self.reunion_on_fly = False
                    self.reunion_timer = 4 * 10
            else:
                nodes_address_list = []
                n_nodes = int(body[3:5])
                for i in range(1, n_nodes):
                    nodes_address_list.append((body[5 + 20 * i:20 + 20 * i], body[20 + 20 * i:25 + 20 * i]))

                reunion_response_packet = PacketFactory.new_reunion_packet(type='RES',
                                                                           source_address=self.server_address,
                                                                           nodes_array=nodes_address_list)
                target_ip = body[25:40]
                target_port = body[40:45]
                target_address = (target_ip, target_port)
                self.stream.add_message_to_out_buff(target_address, reunion_response_packet.buf)
                self.print_function("{} redirected reunion response to {}".format(self.server_address, target_address))

    def __handle_join_packet(self, packet):
        """
        When a Join packet received we should add a new node to our nodes array.
        In reality, there is a security level that forbids joining every node to our network.

        :param packet: Arrived register packet.


        :type packet Packet

        :return:
        """
        join_request_source_address = packet.get_source_server_address()
        if self.right_child_address == join_request_source_address or self.left_child_address == join_request_source_address:
            self.print_function(
                "{} received join request from {} but they have been joined before".format(self.server_address,
                                                                                           join_request_source_address))

        if self.right_child_address is None:
            self.right_child_address = join_request_source_address
        elif self.left_child_address is None:
            self.left_child_address = join_request_source_address
        else:
            self.print_function(
                "Client {} received join from {} but has no free room for a new child".format(self.server_address,
                                                                                              join_request_source_address))
            return
        self.print_function("{} received join request from {}".format(self.server_address, join_request_source_address))

        if not self.is_root:
            self.stream.add_node(join_request_source_address, set_register_connection=False)

    def __get_neighbour(self, sender):
        """
        Finds the best neighbour for the 'sender' from the network_nodes array.
        This function only will call when you are a root peer.

        Code design suggestion:
            1. Use your NetworkGraph find_live_node to find the best neighbour.

        :param sender: Sender of the packet
        :return: The specified neighbour for the sender; The format is like ('192.168.001.001', '05335').
        """
        pass

    def print_function(self, message):
        print(message)
        self.UI.peer_log.log += "{}:\n\t{}\n".format(datetime.datetime.now(), message)
