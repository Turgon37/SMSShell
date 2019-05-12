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

# System imports
import re

# Project imports
from .chain import Chain

__all__ = [
    'Regexp'
]


class ValidationException(Exception):
    """Base class for all exceptions relating to messages validation
    """
    pass


class AbstractValidator(object):
    """Base class for fields validators

    All validators must inherit this class
    """

    def __call__(self, data):
        """Data validation function
        """
        raise NotImplementedError("Your validator must implement the call method")


class ValidatorChain(Chain):
    """This class validate an object using validators per field's name
    """

    ABSTRACT_CLASS = AbstractValidator
    EXCEPTION = ValidationException


class Regexp(AbstractValidator):
    """Validates the field against a user provided regexp.

    Inspired by https://github.com/wtforms/wtforms
    Args:
        regex: The regular expression string to use.
                Can also be a compiled regular expression pattern.
        flags: The regexp flags to use, for example re.IGNORECASE.
                Ignored if `regex` is not a string.
        message: Error message to raise in case of a validation error.
    """

    def __init__(self, regex, flags=0, message='Data did not match the expression'):
        if isinstance(regex, str):
            regex = re.compile(regex, flags)
        self.regex = regex
        self.message = message

    def __call__(self, data):
        match = self.regex.match(data or '')
        if not match:
            raise ValidationException(self.message)
        return data
