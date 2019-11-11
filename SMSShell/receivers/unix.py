# -*- coding: utf8 -*-

# This file is a part of SMSShell
#
# Copyright (c) 2016-2018 Pierre GINDRAUD
#
# SMSShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SMSShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SMSShell. If not, see <http://www.gnu.org/licenses/>.

"""Message receiver from a local unix socket

This receiver open an unix socket locally on the local host
and listen for incoming message on it
"""

# System imports
import json
import logging
import os
import selectors
import socket
import stat

# Project import
from . import AbstractReceiver, AbstractClientRequest
from ..utils import group_to_gid

# Global project declarations
G_LOGGER = logging.getLogger('smsshell.receivers.unix')


class ClientRequest(AbstractClientRequest):
    """Client request for unix receiver
    """

    def __init__(self, receiver, client_socket, **kwargs):
        super().__init__(**kwargs)
        self.__receiver = receiver
        self.__client_socket = client_socket

    def enter(self):
        pass

    def exit(self):
        """Pop all answer data and send them to client
        """
        assert self.__client_socket
        response_data = self.pop_response_data()
        response_data['chain'] = self.get_treatment_chain()
        self.__receiver.write_to_client(self.__client_socket, json.dumps(response_data))


class Receiver(AbstractReceiver):
    # pylint: disable=R0902
    """Receiver class, see module docstring for help
    """

    def __init__(self, *argv, **kwargs):
        """Init function
        """
        super().__init__(*argv, **kwargs)
        # Keeps track of the peers currently connected. Maps socket fd to
        # peer name.
        self.__current_peers = dict()

        # Internal items that will be inits later
        self.__socket_selector = selectors.DefaultSelector()
        self.__server_socket = None
        self.__default_umask = 0o117

        # config
        self.__path = self.get_config('path', fallback="/var/run/smsshell.sock")
        self.__umask = self.get_config('umask', fallback='{:o}'.format(self.__default_umask))
        self.__group = self.get_config('group')
        try:
            self.__listen_queue = int(self.get_config('listen_queue', fallback=10))
        except ValueError:
            self.__listen_queue = 10
            G_LOGGER.error(("invalid integer parameter for option 'listen_queue',"
                            " fallback to default value 10"))

    def write_to_client(self, client_socket, data):
        """Write data to client

        Args:
            client_socket : the socket used to write data
            data : bytes or string to write to client
        """
        if not isinstance(data, bytes):
            data = data.encode()

        try:
            client_socket.send(data)
        except ConnectionError as ex:
            G_LOGGER.warning('client connection with FD %s raise connection error : %s',
                             client_socket.fileno(),
                             str(ex))
            self.__close_connection(client_socket)

    def __on_accept(self, server_socket, mask):
        # pylint: disable=W0613
        """Call each time a new client connection occur

        Args:
            server_socket : the server socket from which to get
                                    the socket to the new client
            mask : unused
        """
        # pylint: disable=W0612
        client_socket, addr = server_socket.accept()
        # disable blocking on client socket
        client_socket.setblocking(0)
        # Register incoming client with metadatas in tracking dict
        assert client_socket.fileno() not in self.__current_peers
        self.__current_peers[client_socket.fileno()] = dict(sock=client_socket)

        # register socket into the selector
        self.__socket_selector.register(fileobj=client_socket,
                                        events=selectors.EVENT_READ,
                                        data=self.__on_read)
        G_LOGGER.info('accepted new client with FD %d on unix socket', client_socket.fileno())

    def __on_read(self, client_socket, mask):
        # pylint: disable=W0613
        """Call each time a socket received an event

        Args:
            client_socket: the source client socket
        """
        try:
            request_data = client_socket.recv(1000)
        except ConnectionError as ex:
            G_LOGGER.warning('client connection with FD %s raise connection error : %s',
                             client_socket.fileno(),
                             str(ex))
            self.__close_connection(client_socket)
            return None

        # If there is no data, the socket must have been closed from client side
        if not request_data:
            self.__close_connection(client_socket)
            return None

        # if these is data, that mean client has send some bytes to read
        # receive the data
        G_LOGGER.info('get %d bytes of data from client socket with FD %d',
                      len(request_data),
                      client_socket.fileno())
        G_LOGGER.debug('get data from FD %d: %s',
                       client_socket.fileno(),
                       request_data)
        # decode data
        raw_request_data_length = len(request_data)
        if not isinstance(request_data, str):
            request_data = request_data.decode()

        # prepare client request context
        request = ClientRequest(receiver=self,
                                client_socket=client_socket,
                                request_data=request_data)
        # append a simple ACK to client next datas
        # to confirm all is OK
        G_LOGGER.debug('send ACK to FD %d for %d bytes of data',
                       client_socket.fileno(),
                       raw_request_data_length)
        request.add_response_data(received_length=raw_request_data_length)
        request.append_treatment_chain('received')

        return request

    def __close_connection(self, client_socket):
        """Call each time a socket is closed

        Flush and close properly client socket

        Args:
            client_socket: the client socket to close
        """
        # We can't ask conn for getpeername() here, because the peer may no
        # longer exist (hung up); instead we use our own mapping of socket
        # fds to peer names - our socket fd is still open.
        del self.__current_peers[client_socket.fileno()]
        self.__socket_selector.unregister(client_socket)
        G_LOGGER.info('closed client connection with FD %d', client_socket.fileno())
        client_socket.close()

    def start(self):
        """Start the unix socket receiver

        Init the socket

        Returns:
            a boolean that indicates the successful of the stop operation
        """
        directory = os.path.dirname(self.__path)
        # check permissions
        if not (os.path.isdir(directory) and os.access(directory, os.X_OK)):
            G_LOGGER.fatal('Unsufficients permissions into socket directory')
            return False
        # Make sure the socket does not already exist
        if os.path.exists(self.__path):
            # if the path correspond to a socket, try to remove it silently
            if stat.S_ISSOCK(os.stat(self.__path).st_mode):
                G_LOGGER.debug('overwrite existing unix socket file')
                try:
                    os.unlink(self.__path)
                except OSError:
                    if os.path.exists(self.__path):
                        G_LOGGER.fatal('The unix socket path already exists and cannot be removed')
                        return False
            else:
                # pylint: disable=W1201
                G_LOGGER.fatal('The unix socket path given is already a file' +
                               ' but not a unix socket. Please delete it manually')
                return False

        # check directory write rights
        if not os.access(directory, os.X_OK|os.W_OK):
            G_LOGGER.fatal('Unsufficients permissions into the directory %s to create the socket',
                           self.__path)
            return False
        G_LOGGER.debug('creating new server socket')

        # Create a TCP unix socket
        self.__server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        G_LOGGER.debug('configure new server socket to unblocking')
        self.__server_socket.setblocking(0)

        # Bind the socket to the port
        try:
            umask = int(self.__umask, 8)
        except ValueError:
            G_LOGGER.error("Invalid UMASK format '%s', fallback to default umask %s",
                           self.__umask,
                           self.__default_umask)
            umask = self.__default_umask
        G_LOGGER.debug('bind socket to path %s with umask %s', self.__path, oct(umask))

        # create socket file
        old_umask = os.umask(umask)
        self.__server_socket.bind(self.__path)
        os.umask(old_umask)

        # optionally change group of the socket
        if self.__group:
            try:
                os.chown(self.__path,
                         -1,
                         group_to_gid(self.__group))
                G_LOGGER.info("Switched socket group owner to '%s'",
                              self.__group)
            except KeyError:
                G_LOGGER.error("Incorrect group name '%s' for receiver, ignoring group directive",
                               self.__group)
            except PermissionError:
                # pylint: disable=W1201
                G_LOGGER.error("Cannot change group ownership, you are not member of " +
                               "group name '%s', ignoring group directive",
                               self.__group)

        # Listen for incoming connections
        G_LOGGER.debug('set socket to listening mode with listen queue size %d',
                       self.__listen_queue)
        self.__server_socket.listen(self.__listen_queue)
        G_LOGGER.info('Unix receiver ready to listen on %s FD %d',
                      self.__path,
                      self.__server_socket.fileno())

        ## Init sockets selector
        self.__socket_selector.register(fileobj=self.__server_socket,
                                        events=selectors.EVENT_READ,
                                        data=self.__on_accept)
        return True

    def stop(self):
        """Stop the unix socket receiver

        Returns:
            a boolean that indicates the successful of the stop operation
        """
        G_LOGGER.info('Closing unix receiver')
        G_LOGGER.debug('closing all unix sockets')
        for peer in self.__current_peers.values():
            peer['sock'].close()
        G_LOGGER.debug('closing server socket')
        self.__server_socket.close()
        self.__socket_selector.close()
        G_LOGGER.debug('remove server socket')
        try:
            os.unlink(self.__path)
        except OSError:
            G_LOGGER.error('unable to delete socket')
            return False
        return True

    def read(self):
        """Wait and receive data from network clients

        Returns:
            Iterable
        """
        G_LOGGER.info('Reading from unix socket %s', self.__path)
        while True:
            # Wait until some registered socket becomes ready.
            events = self.__socket_selector.select()

            # For each new event, dispatch to its handler
            for key, mask in events:
                # callback can be a function registered in selector
                # currently we have only
                # __onRead and __onAccept
                callback = key.data
                socket_data = callback(key.fileobj, mask)
                # yield only data read from client sockets
                # compare the data object with the onread function
                # pylint: disable=W0143
                if callback == self.__on_read and socket_data is not None:
                    yield socket_data
