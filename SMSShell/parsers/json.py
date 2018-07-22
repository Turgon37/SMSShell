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

"""A JSON input parser
"""

# System imports
import logging
import json

# Project imports
from . import DecodeException, BadMessageFormatException
from ..models import Message
from . import AbstractParser

# Global project declarations
g_logger = logging.getLogger('smsshell.parsers.json')


class Parser(AbstractParser):
    """A JSON format parser
    """

    def parse(self, raw):
        """Parse the raw content

        @param raw the raw input content as string
        @return a Message instance
        """
        try:
            obj = json.loads(raw)
        except ValueError as ex:
            g_logger.debug('bad JSON %s', str(ex))
            raise DecodeException('the received message was not a valid JSON object')
        except TypeError as ex:
            g_logger.debug('bad object type %s', str(ex))
            raise DecodeException('the received message was not a valid JSON object')

        if 'sms_number' not in obj:
            raise BadMessageFormatException('the sender field is missing')
        sender = obj['sms_number']
        if 'sms_text' not in obj:
            raise BadMessageFormatException('the text field is missing')
        content = obj['sms_text']
        if sender is None or len(sender) < 1:
            raise BadMessageFormatException('the sender field is null or too small')
        if content is None or len(content) < 1:
            raise BadMessageFormatException('the text field is null or too small')
        return Message(sender, content)
