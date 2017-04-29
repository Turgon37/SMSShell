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

"""A JSON input parser
"""

# System imports
import logging
import json

# Project imports
from .exceptions import ParsingException
from .exceptions import BadMessageException
from ..models import Message
from . import AbstractParser

# Global project declarations
g_logger = logging.getLogger('smsshell.parsers.json')


class Parser(AbstractParser):
    """An JSON format parser
    """

    def parse(self, raw):
        """Parse the raw content

        @param raw the raw input content as string
        @return a Message instance
        """
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as d:
            raise ParsingException()
        sender = obj['smsnumber']
        content = obj['smstext']
        if sender is None or len(sender) < 1:
            raise BadMessageException("The sender field is null or too small")
        if content is None or len(content) < 1:
            raise BadMessageException("The content field is null or too small")
        return Message(sender, content)
