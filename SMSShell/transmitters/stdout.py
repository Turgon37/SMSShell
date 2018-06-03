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

# Project imports
from . import AbstractTransmitter

# Global project declarations
g_logger = logging.getLogger('smsshell.transmitters.stdout')


class Transmitter(AbstractTransmitter):
    """Transmitter class, see module docstring for help
    """

    def start(self):
        return True

    def stop(self):
        return True

    def transmit(self, raw):
        print('TRANSMIT: {}'.format(raw))
