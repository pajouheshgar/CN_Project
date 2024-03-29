import sys
import socket


class ClientSocket:
    def __init__(self, mode, port, received_bytes=2048, single_use=True):
        """

        Handle the socket's mode.
        The socket's mode determines the IP address it will attempt to connect to.
        mode can be one of two special values:
        localhost -> (127.0.0.1)
        public ->    (0.0.0.0)
        otherwise, mode is interpreted as an IP address.
        """

        if mode == "localhost":
            self.connect_ip = mode
        elif mode == "public":
            self.connect_ip = socket.gethostname()
        else:
            self.connect_ip = mode
        # Handle the port we're going to connect to.
        self.connect_port = port
        if type(self.connect_port) != int:
            print("port must be an integer", file=sys.stderr)
            raise ValueError
        # Actually create an INET, STREAMing socket.socket.
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Save the number of bytes to be read in response
        self.received_bytes = received_bytes
        # Save whether this socket is single-use or not.
        self.single_use = single_use
        # If this isn't a single-use socket, connect right away.
        if not self.single_use:
            self._socket.connect((self.connect_ip, self.connect_port))
            # Keep track of whether this socket has been closed.
            self.closed = False
        # Keep track of whether this socket has been used, so we can
        # warn single-use sockets not to send data twice.
        self.used = False

    def get_port(self):
        return self.connect_port

    def get_ip(self):
        return self.connect_ip

    def send(self, data):
        """

        This method takes one argument: data
        data is the data to be sent to the server at the address
        specified in this object's constructor.
        data must be either of type str or of type bytes.
        If data is of type str, then it will be implicitly converted
        to UTF-8 bytes.

        This method returns a string which is the response received
        from the server at the address specified in this object's
        constructor.
        It is "" if no response was received.

        If the socket is single-use, we need to connect now
        and then immediately close after our correspondence with
        the server we're talking to.

        """

        if self.single_use:
            # If the socket is single-use and we've already used it:
            if self.used:
                print("You cannot use a single-use socket twice", file=sys.stderr)
                raise RuntimeError
            # Otherwise, connect
            self._socket.connect((self.connect_ip, self.connect_port))
            # Keep track of whether this socket has been closed.
            self.closed = False
        # If data is a string, rather than bytes.
        if type(data) == str:
            # Turn it into UTF-8 bytes.
            data = bytes(data, "UTF-8")
        # If the data isn't bytes at this point, something went wrong.
        if type(data) != bytes:
            print("data must be a string or bytes", file=sys.stderr)
            raise ValueError
        # Everything is setup, now we must send the data.
        self._socket.send(data)
        # Keep track of the fact that we've sent data (or attempted to).
        self.used = True
        # Now read the response:
        response = self._socket.recv(self.received_bytes)
        # If this socket is single-use, destroy the connection.
        if self.single_use:
            self._socket.close()
            # Keep track of the fact that this is closed.
            self.closed = True
        # Return the response
        return response

    def close(self):
        # If the connection isn't already closed, close it.
        if not self.closed:
            self._socket.close()
            self.closed = True


if __name__ == "__main__":
    import time

    client = ClientSocket(mode='localhost', port=8765, single_use=False)
    response = client.send("FUCK OFF")
    print(response)
    response = client.send("FUCK OFF2")
    print(response)
    response = client.send("FUCK OFF3")
    print(response)
    # response = client.send("FUCK OFF4")
    # print(response)
    client.close()
