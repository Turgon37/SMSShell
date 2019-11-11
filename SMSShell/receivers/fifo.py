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

"""This receiver is based on a local fifo

This receiver create an input fifo on start, and read message from
it
"""

# System imports
import logging
import os
import stat

# Project import
from . import AbstractReceiver, AbstractClientRequest

# Global project declarations
G_LOGGER = logging.getLogger('smsshell.receivers.fifo')


class ClientRequest(AbstractClientRequest):
    """Client request for fifo receiver

    With a fifo we cannot identify a client from another
    so we cannot write any answer
    """

    def enter(self):
        pass

    def exit(self):
        pass


class Receiver(AbstractReceiver):
    """Receiver class, see module docstring for help
    """

    def __init__(self, *argv, **kwargs):
        """Init function
        """
        super().__init__(*argv, **kwargs)
        self.__path = self.get_config('path', fallback="/var/run/smsshell.fifo")

    def start(self):
        """Start the socket (FIFO) runner

        Init the fifo pipe

        Returns:
            a boolean that indicates the successful of the start operation
        """
        directory = os.path.dirname(self.__path)
        # check permissions
        if not (os.path.isdir(directory) and os.access(directory, os.X_OK)):
            G_LOGGER.fatal('Unsufficients permissions into socket directory')
            return False
        # check socket
        if os.path.exists(self.__path):
            if not stat.S_ISFIFO(os.stat(self.__path).st_mode):
                G_LOGGER.fatal('The path given is already a file but not a fifo')
                return False
            G_LOGGER.debug('using existing fifo')
        elif not os.path.exists(self.__path):
            # check directory write rights
            if not os.access(directory, os.X_OK|os.W_OK):
                G_LOGGER.fatal('Unsufficients permissions into the directory %s to create the fifo',
                               self.__path)
                return False
            G_LOGGER.debug('creating new fifo at %s', self.__path)
            os.mkfifo(self.__path, mode=0o620)
        return self

    def stop(self):
        """We just remove the fifo

        Returns:
            a boolean that indicates the successful of the stop operation
        """
        try:
            os.unlink(self.__path)
        except OSError:
            G_LOGGER.error('unable to delete fifo')
            return False
        return True

    def read(self):
        """Return a read blocking iterable object for each content in the fifo

        Return:
            Iterable
        """
        G_LOGGER.info('Reading from fifo %s', self.__path)
        while True:
            with open(self.__path) as fifo:
                yield ClientRequest(request_data=fifo.read())
