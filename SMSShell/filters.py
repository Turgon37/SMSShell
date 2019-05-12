# -*- coding: utf8 -*-

# This file is a part of SMSShell
#
# Copyright (c) 2016-2019 Pierre GINDRAUD
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

"""This module contains data filters
"""

# System imports
import re

# Project imports
from .exceptions import ShellInitException
from .chain import Chain

__all__ = [
    'RegexpReplace'
]


class FilterException(Exception):
    """Base class for all exceptions relating to messages filtering
    """
    pass


class AbstractFilter(object):
    """Base class for fields filters

    All filters must inherit this class
    """

    def __call__(self, data):
        """Data validation function
        """
        raise NotImplementedError("Your filter must implement the call method")


class FilterChain(Chain):
    """This class validate an object using validators per field's name
    """

    ABSTRACT_CLASS = AbstractFilter
    EXCEPTION = FilterException
    ASSIGN_RETURN = True


class LowerCase(AbstractFilter):
    """Make the left part of the message lowercase

    Args:
        length: the number of letter to pass into lowercase
        start: the position of the first letter to lowercase
    """

    def __init__(self, length, start=0):
        try:
            self.length = int(length)
            self.start = int(start)
        except ValueError as ex:
            raise ShellInitException(str(ex))

    def __call__(self, data):
        return data[self.start:self.length].lower() + data[(self.start+self.length):]
