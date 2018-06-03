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


class Message(object):
    """This class represent a message with sender id and content
    """

    def __init__(self, sender, content):
        """Constructor: Build a new message object

        Args:
            sender: sender's unique identifier
            content: the message content as a string
        """
        self.__sender = None
        self.__content = None
        # database model
        self.sender = sender
        self.content = content

    @property
    def sender(self):
        """Return the sender id

        Returns:
            the sender id as a string
        """
        assert self.__sender is not None
        return self.__sender

    @sender.setter
    def sender(self, send):
        """Set the sender id

        Args:
            send: the sender id as a string
        """
        self.__sender = send

    @property
    def content(self):
        """Return the message content

        Returns:
            the message content as a string
        """
        assert self.__content is not None
        return self.__content

    @content.setter
    def content(self, cont):
        """Set the message content

        Args:
            cont: the raw message content
        """
        self.__content = cont

    def asString(self):
        """Return the message content and ensure it is a string

        Returns:
            ensure the returned message content is a string
        """
        assert isinstance(self.content, str)
        return self.content


    # DEBUG methods
    def __str__(self):
        """[DEBUG] Produce a description string for this message

        Returns:
            a formatted description of this message and his content
        """
        content = ("Message from(" + str(self.sender) + ")" +
                   "\n  CONTENT = " + str(self.content))
        return content

    def __repr__(self):
        """[DEBUG] Produce a list of attribute as string

        @return [str] a formatted string that describe this object
        """
        return "[M(" + str(self.sender) + ")]"
