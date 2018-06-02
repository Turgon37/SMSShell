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

"""This module define all operations related Exceptions
"""

class SMSShellException(Exception):
    """Exception related to the global service
    """
    pass

class ShellInitException(Exception):
    """Base exception for shell initialization procedures

    Must be raise by parsers,transmitters,receivers on start() error
    """
    pass

#
# MESSAGES RELATED EXCEPTIONS
#

class SMSException(Exception):
    """Base exception relating to SMS messages error

    It is currently used by parsers
    """
    pass

#
# SHELL RELATED EXCEPTIONS
#

class ShellException(Exception):
    """Base exception relating to command execution exceptions

    Args:
        message: the standard full exception error message
        short: an optional short message that can be send back to the user
    """
    def __init__(self, message, short='general exeception'):
        super().__init__(message)
        self.short_message = short

class BadCommandCall(ShellException):
    """Raised when you call a command with bad arguments
    """
    def __init__(self, message, short='bad call, use help'):
        super().__init__(message, short)
