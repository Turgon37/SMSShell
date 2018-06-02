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
"""

# System imports
import json
import logging
import os
import selectors
import socket
import stat

# Project import
from . import AbstractReceiver

# Global project declarations
g_logger = logging.getLogger('smsshell.receivers.unix')


class Receiver(AbstractReceiver):
    """A receiver class based on unix socket
    """

    def init(self):
        """Init function
        """
        # Keeps track of the peers currently connected. Maps socket fd to
        # peer name.
        self.__current_peers = dict()

        # Internal items that will be inits later
        self.__socket_selector = selectors.DefaultSelector()
        self.__server_socket = None
        self.__default_umask = 0o117


        # config
        self.__path = self.getConfig('path', fallback="/var/run/smsshell.sock")
        self.__umask = self.getConfig('umask', fallback=self.__default_umask)
        self.__listen_queue = int(self.getConfig('listen_queue', fallback=10))

    def __onAccept(self, server_socket, mask):
        client_socket, addr = server_socket.accept()
        client_socket.setblocking(0)
        # Register incoming client with metadatas
        assert client_socket.fileno() not in self.__current_peers
        self.__current_peers[client_socket.fileno()] = dict(size=None, )

        self.__socket_selector.register(fileobj=client_socket,
                                        events=selectors.EVENT_READ,
                                        data=self.__onRead)
        g_logger.info('accepted new client with FD %d on unix socket', client_socket.fileno())

    def __onRead(self, client_socket, mask):
        """Call each time a socket received an event

        @param socket client_socket the source socket
        """
        try:
            request_data = client_socket.recv(1000)
            # if these is data, that mean client has send some bytes to read
            if request_data:
                g_logger.info('get %d bytes of data from FD %d',
                              len(request_data),
                              client_socket.fileno())
                g_logger.debug('get data from FD %d: %s',
                               client_socket.fileno(),
                               request_data)
                # return a simple ACK to client with received size to confirm all is OK
                g_logger.debug('send ACK to FD %d', client_socket.fileno())
                response = dict(status=0, length=len(request_data))
                response_data = json.dumps(response)
                if not isinstance(response_data, bytes):
                    response_data = response_data.encode()
                client_socket.send(response_data)

                if not isinstance(request_data, str):
                    request_data = request_data.decode()
                return request_data
            # If there is no data, the socket must have been closed from client side
            else:
                self.__closeConnection(client_socket)
        except ConnectionError as ex:
            g_logger.warning('client connection with FD %s raise connection error : %s', client_socket.fileno(), str(ex))
            self.__closeConnection(client_socket)

    def __closeConnection(self, client_socket):
        """
        """
        # We can't ask conn for getpeername() here, because the peer may no
        # longer exist (hung up); instead we use our own mapping of socket
        # fds to peer names - our socket fd is still open.
        g_logger.info('closing connection to FD %d', client_socket.fileno())
        del self.__current_peers[client_socket.fileno()]
        self.__socket_selector.unregister(client_socket)
        client_socket.close()

    def start(self):
        """Start the unix socket receiver

        Init the socket
        @return self
        """
        directory = os.path.dirname(self.__path)
        # check permissions
        if not (os.path.isdir(directory) and os.access(directory, os.X_OK)):
            g_logger.fatal('Unsufficients permissions into socket directory')
            return False
        # Make sure the socket does not already exist
        if os.path.exists(self.__path):
            # if the path correspond to a socket, try to remove it silently
            if stat.S_ISSOCK(os.stat(self.__path).st_mode):
                g_logger.debug('overwrite existing unix socket file')
                try:
                    os.unlink(self.__path)
                except OSError:
                    if os.path.exists(self.__path):
                        g_logger.fatal('The unix socket path already exists and cannot be removed')
                        return False
            else:
                g_logger.fatal('The unix socket path given is already a file but not a unix socket. Please delete it manually')
                return False

        # check directory write rights
        if not os.access(directory, os.X_OK|os.W_OK):
            g_logger.fatal('Unsufficients permissions into the directory %s to create the socket',
                           self.__path)
            return False
        g_logger.debug('creating new server socket')

        # Create a TCP unix socket
        self.__server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        g_logger.debug('configure new server socket to unblocking')
        self.__server_socket.setblocking(0)

        # Bind the socket to the port
        try:
            umask = int(self.__umask, 8)
        except ValueError:
            g_logger.error('Invalid UMASK format, fallback to default umask %s', self.__default_umask)
            umask = self.__default_umask
        g_logger.debug('bind socket to path %s with umask %s', self.__path, oct(umask))

        old_umask = os.umask(umask)
        self.__server_socket.bind(self.__path)
        os.umask(old_umask)

        # Listen for incoming connections
        g_logger.debug('set socket to listening mode with listen queue size %d', self.__listen_queue)
        self.__server_socket.listen(self.__listen_queue)
        g_logger.info('Unix receiver ready to listen on %s FD %d', self.__path, self.__server_socket.fileno())

        ## Init sockets selector
        self.__socket_selector.register(fileobj=self.__server_socket,
                                        events=selectors.EVENT_READ,
                                        data=self.__onAccept)

        return True

    def stop(self):
        """Stop the unix socket receiver

        @return self
        """
        g_logger.info('Closing unix receiver')
        g_logger.debug('closing all unix sockets')
        for fd in self.__current_peers:
            fd.close()
        g_logger.debug('closing server socket')
        self.__server_socket.close()
        self.__socket_selector.close()

    def read(self):
        """Wait and receive data from network clients

        @return Iterable
        """
        while True:
            # Wait until some registered socket becomes ready.
            events = self.__socket_selector.select()

            # For each new event, dispatch to its handler
            for key, mask in events:
                callback = key.data
                socket_data = callback(key.fileobj, mask)
                # yield only data read from client sockets
                # compare the data object with the onread function
                if key.data == self.__onRead:
                    yield socket_data
