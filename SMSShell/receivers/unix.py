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

"""
"""

# System imports
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
        """Init
        """
        self.__path = self.getConfig('path', fallback="/var/run/smsshell.sock")
        self.__listen_queue = int(self.getConfig('listen_queue', fallback=10))
        # Keeps track of the peers currently connected. Maps socket fd to
        # peer name.
        self.__current_peers = dict()

        # Internal items that will be inits later
        self.__socket_selector = None
        self.__server_socket = None

    def __on_accept(self, server_socket, mask):
        client_socket, addr = server_socket.accept()
        client_socket.setblocking(0)
        # Register incoming client with metadatas
        assert client_socket.fileno() not in self.__current_peers
        self.__current_peers[client_socket.fileno()] = dict(size=None, )

        self.__socket_selector.register(fileobj=client_socket,
                                        events=selectors.EVENT_READ,
                                        data=self.__on_read)
        g_logger.info('accepted new client with FD %d on unix socket', client_socket.fileno())

    def __on_read(self, client_socket, mask):
        try:
            data = client_socket.recv(1000)
            if data:
                g_logger.info('get data length {} from {}'.format(len(data), client_socket.fileno()))
                g_logger.debug('get data from {}: {!r}'.format(client_socket.fileno(), data))
                # Assume for simplicity that send() won't block
                client_socket.send(data)
                return data
            else:
                self.__close_connection(client_socket)
        except ConnectionError:
            g_logger.warning('client connection with FD %s raise an connection error', client_socket.fileno())
            self.__close_connection(client_socket)

    def __close_connection(self, client_socket):
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
                    if os.path.exists(server_address):
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
        g_logger.debug('creating new socket')

        # Create a TCP unix socket
        self.__server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        g_logger.debug('configure new socket to unblocking')
        self.__server_socket.setblocking(0)

        # Bind the socket to the port
        g_logger.debug('bind socket to path %s', self.__path)
        self.__server_socket.bind(self.__path)

        # Listen for incoming connections
        g_logger.debug('set socket to listening mode with listen queue size %d', self.__listen_queue)
        self.__server_socket.listen(self.__listen_queue)
        g_logger.info('Unix receiver ready to listen on FD {}'.format(self.__server_socket.fileno()))

        ## Init sockets selector
        self.__socket_selector = selectors.DefaultSelector()
        self.__socket_selector.register(fileobj=self.__server_socket,
                                        events=selectors.EVENT_READ,
                                        data=self.__on_accept)

        return True

    def stop(self):
        """Stop the unix socket receiver

        @return self
        """
        g_logger.debug('closing all unix sockets')
        for fd in self.__current_peers:
            fd.close()
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
                if key.data == self.__on_read:
                    yield socket_data
