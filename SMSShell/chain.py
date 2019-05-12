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

"""This module contains data validators
"""

# Project imports
from .exceptions import ShellInitException


class Chain(object):
    """This class validate an object using validators per field's name
    """

    ABSTRACT_CLASS = object
    EXCEPTION = Exception
    ASSIGN_RETURN = False

    def __init__(self):
        """Init a new empty chain
        """
        self.__field_links = dict()

    def addFieldLink(self, field, link):
        """Append a link object for specific field

        Args:
            field: the field's name
            link: the AbstractValidator validator instance
        Raise:
            ShellInitException if validator is not instance of AbstractValidator
        """
        if (self.__class__.ABSTRACT_CLASS and
                not isinstance(link, self.__class__.ABSTRACT_CLASS)):
            raise ShellInitException('Object {} is not an instance of {}'.format(
                repr(link),
                self.__class__.ABSTRACT_CLASS.__name__.lower()))

        if field not in self.__field_links:
            self.__field_links[field] = []
        self.__field_links[field].append(link)

    def addLinksFromDict(self, field_links_map):
        """Initialize filters for this message

        Args:
            field_links_map : the filters configuration hash
                            given by config parser
        """
        for field, links in field_links_map.items():
            for l in links:
                self.addFieldLink(field, l)

    def callChainOnObject(self, obj):
        """Validate message using the defined validators

        Args:
            obj: the object with fields to validate
        Return:
            True if chain successful
        Raise:
            Some Exception if chain fail
        """
        for field, links in self.__field_links.items():
            if not hasattr(obj, field):
                raise self.__class__.EXCEPTION(("Field '{}' does not exist in " +
                                                "message").format(field))
            for l in links:
                r = l(getattr(obj, field))
                if self.__class__.ASSIGN_RETURN:
                    setattr(obj, field, r)
        return True
