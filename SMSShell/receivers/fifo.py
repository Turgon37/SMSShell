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
import stat

# Project import
from . import AbstractReceiver

# Global project declarations
g_logger = logging.getLogger('smsshell.receivers.fifo')


class Receiver(AbstractReceiver):
    """A fifo receiver class
    """

    def init(self):
        """Init
        """
        self.__path = self.getConfig('path', fallback="/var/run/smsshell")

    def start(self):
        """Start the socket (FIFO) runner

        Init the fifo pipe and wait for incoming contents
        @return self
        """
        directory = os.path.dirname(self.__path)
        # check permissions
        if not (os.path.isdir(directory) and os.access(directory, os.X_OK)):
            g_logger.fatal('Unsufficients permissions into socket directory')
            return False
        # check socket
        if os.path.exists(self.__path):
            if not stat.S_ISFIFO(os.stat(self.__path).st_mode):
                g_logger.fatal('The path given is already a file but not a fifo')
                return False
            g_logger.debug('using existing fifo')
        elif not os.path.exists(self.__path):
            # check directory write rights
            if not os.access(directory, os.X_OK|os.W_OK):
                g_logger.fatal('Unsufficients permissions into the directory %s to create the fifo',
                               self.__path)
                return False
            g_logger.debug('creating new fifo')
            os.mkfifo(self.__path, mode=0o620)
        return self

    def stop(self):
        """We don't need to stop a fifo
        """
        return True

    def read(self):
        """Return a read blocking iterable object for each content in the fifo

        @return Iterable
        """
        while True:
            with open(self.__path) as fifo:
                yield fifo.read()
