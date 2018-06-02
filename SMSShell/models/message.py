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

"""Models/Message This class represent a incoming message in shell

Each message have a sender reference used to keep session consistency and a
content that will be analysed
"""

# Project imports
from ..exceptions import CommandBadImplemented


class Message(object):
    """A simple message with sender id
    """

    def __init__(self, sender, content):
        """Constructor: Build a new message object

        @param sender [str] : sender unique identifier
        @param content [str] : message content
        """
        self.__sender = None
        self.__content = None
        # database model
        self.sender = sender
        self.content = content

    @property
    def sender(self):
        """Return the sender id

        @return [str] the sender id
        """
        assert self.__sender is not None
        return self.__sender

    @sender.setter
    def sender(self, s):
        """Set the sender id

        @param s [str] : the sender id
        """
        self.__sender = s

    @property
    def content(self):
        """Return the content payload

        @return [str] the content
        """
        assert self.__content is not None
        return self.__content

    @content.setter
    def content(self, c):
        """Set the message content

        @param c [str] : the content
        """
        self.__content = c

    def asString(self):
        """Return the command argument vector associated with this message

        @return list of command argments
        """
        assert isinstance(self.content, str)
        return self.content


    # DEBUG methods
    def __str__(self):
        """[DEBUG] Produce a description string for this message

        @return [str] a formatted string
        """
        content = ("Message from(" + str(self.sender) + ")" +
                   "\n  CONTENT = " + str(self.content))
        return content

    def __repr__(self):
        """[DEBUG] Produce a list of attribute as string

        @return [str] a formatted string that describe this object
        """
        return "[M(" + str(self.sender) + ")]"
