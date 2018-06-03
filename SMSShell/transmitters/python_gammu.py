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

"""A simple file output transmitter
"""

# System imports
import logging
import os

# Project imports
from . import AbstractTransmitter
from ..models import Message

# Global project declarations
g_logger = logging.getLogger('smsshell.transmitters.python_gammu')


class Transmitter(AbstractTransmitter):
    """Transmitter class, see module docstring for help
    """

    def init(self):
        """Init function
        """
        self.__smsd = None
        self.__default_umask = 0o117

        # configuration
        self.__config = self.getConfig('smsdrc_configuration', fallback='/etc/gammu-smsdrc')

        # config
        self.__path = self.getConfig('path', fallback="/var/run/smsshell.sock")

        # parse umask
        try:
            self.__umask = int(self.getConfig('umask', fallback='{:o}'.format(self.__default_umask)),
                               8)
        except ValueError:
            g_logger.error("Invalid UMASK format '%s', fallback to default umask %s",
                           self.__umask,
                           self.__default_umask)
            self.__umask = self.__default_umask

    def start(self):
        try:
            import gammu.smsd
        except ImportError as ex:
            g_logger.critical("Cannot import module 'gammu' because : %s", str(ex))
            return False

        # fetch configuration file
        if not os.path.isfile(self.__config):
            g_logger.critical("The gammu-smsd configuration does not exist at '%s'", self.__config)
            return False
        elif not os.access(self.__config, os.R_OK):
            g_logger.critical("The gammu-smsd configuration is not readable at '%s'", self.__config)
            return False

        g_logger.debug('creating gammu smsd client instance')
        try:
            self.__smsd = gammu.smsd.SMSD(self.__config)
        except gammu.GSMError as ex:
            g_logger.critical("Cannot create smsd client instance: %s", str(ex))
            return False
        g_logger.info('Gammu SMSD client instance seems to be ready to transmit')

        return True

    def stop(self):
        self.__smsd = None
        return True

    def transmit(self, answer):
        assert isinstance(answer, Message)
        message = {
            'Text': answer.asString(),
            'SMSC': {
                'Location': 1
            },
            'Number': answer.sender,
        }

        # change umask before to create outbox file
        old_umask = os.umask(self.__umask)
        self.__smsd.InjectSMS([message])
        os.umask(old_umask)
