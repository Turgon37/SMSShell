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

"""This module contains all input parser classes
"""

# Project imports
from ..abstract import AbstractModule
from ..exceptions import SMSException


class ParsingException(SMSException):
    """Main class for parsing error

    All sub exception types must inherit this type
    """
    pass


class BadMessageException(ParsingException):
    """Raise when a message is not valid

    A message is considered as not valid when at least one of his field does not
    not follow the requirement
    """
    pass


class AbstractParser(AbstractModule):
    """An abstract message parser
    """

    def parse(self, raw):
        """Parse the raw content

        @param raw the raw input content as string
        @return a Message instance
        """
        raise NotImplementedError("You must implement the 'parse' method in parser")
