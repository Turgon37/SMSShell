# -*- coding: utf8 -*-

# This file is a part of SMSShell
#
# Copyright (c) 2016-2017 Pierre GINDRAUD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
