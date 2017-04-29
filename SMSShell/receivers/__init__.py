# -*- coding: utf8 -*-

# This file is a part of SMSShell
#
# Copyright (c) 2016-2017 Pierre GINDRAUD
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

"""This module contains all input parser classes
"""

# Project imports
from ..abstract import AbstractModule


class AbstractReceiver(AbstractModule):
    """An abstract receiver
    """

    def start(self):
        """Prepare the receiver

        @return bool : True if init has success, otherwise False
        """
        raise NotImplementedError("You must implement the 'start' method in receiver class")

    def read(self):
        """Return a read blocking iterable object for each content in the fifo

        @return Iterable
        """
        raise NotImplementedError("You must implement the 'read' method in receiver class")
