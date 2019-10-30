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

"""This module contains all output handlers
"""

# Project imports
from ..abstract import AbstractModule
from ..models import Message


class AbstractTransmitter(AbstractModule):
    """An abstract transmistter
    """

    def start(self):
        """Prepare the transmitter

        Returns:
            True if init has success, otherwise False
        """
        raise NotImplementedError("You must implement the 'start' method in transmitter class")

    def stop(self):
        """Close properly the transmitter

        Returns:
            True if stop has success, otherwise False
        """
        raise NotImplementedError("You must implement the 'stop' method in receiver class")

    def transmit(self, answer):
        # pylint: disable=R0201
        """Forward the message to end user

        Args:
            answer : the Message instance of the message to transmit to end user
        """
        assert isinstance(answer, Message)
        raise NotImplementedError("You must implement the 'transmit' method in transmitter class")
