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

# System imports
import logging

# Project imports
from ..validators import ValidationException

# Global project declarations
g_logger = logging.getLogger('smsshell.message')


class Message(object):
    """This class represent a message with sender id and content
    """

    def __init__(self, number, content, attributes=None):
        """Constructor: Build a new message object

        Args:
            number : message number
            content : the message content as a string
        """
        self.__number = None
        self.__content = None
        self.__attributes = dict()
        self.__validators = dict()
        # database model
        if attributes is not None:
            assert isinstance(attributes, dict)
            self.attributes = attributes
        self.sender = number
        self.content = content

    @property
    def number(self):
        """Return this message number

        Returns:
            the sender id as a string
        """
        assert self.__number is not None
        return self.__number

    @property
    def sender(self):
        """Return the sender id

        Returns:
            the sender id as a string
        """
        return self.number

    @sender.setter
    def sender(self, send):
        """Set the sender id

        Args:
            send: the sender id as a string
        """
        self.__number = send

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

    def attribute(self, key, fallback=KeyError):
        """Return the optional message extra attributes

        Returns:
            a dict of message attributes
        """
        assert self.__attributes is not None
        assert isinstance(self.__attributes, dict)
        if key not in self.__attributes:
            if issubclass(fallback, Exception):
                raise fallback(key)
            return fallback
        return self.__attributes[key]

    @property
    def attributes(self):
        """Return the optional message extra attributes

        Returns:
            a dict of message attributes
        """
        assert self.__attributes is not None
        assert isinstance(self.__attributes, dict)
        return self.__attributes

    @attributes.setter
    def attributes(self, keys):
        """Set the message content

        Args:
            keys: the new keys value to add
        """
        self.__attributes.update(keys)

    def asString(self):
        """Return the message content and ensure it is a string

        Returns:
            ensure the returned message content is a string
        """
        assert isinstance(self.content, str)
        return self.content

    def loadValidatators(self, validators):
        """Initialize filters for this message

        Args:
            config_hash : the filters configuration hash
                            given by config parser
        Raise:
            ValidationException : if a filter raise an error
        """
        for field, filters in validators.items():
            if not hasattr(self, field):
                raise ValidationException(("Field '{}' does not exist in " +
                                           "message objects").format(field))
            if field not in self.__validators:
                self.__validators[field] = []
            for filter in filters:
                self.__validators[field].append(filter)

    def validate(self):
        """Validate this message using the defined validators
        """
        for field, validators in self.__validators.items():
            for v in validators:
                v(getattr(self, field))
        return True

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
