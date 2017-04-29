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

"""This module define all operations related Exceptions
"""


class SMSException(Exception):
    """Base exception relating to SMS messages error
    """
    pass


class ShellInitException(Exception):
    """Base exception for all shell inits
    """
    pass


class ShellException(Exception):
    """Base exception relating to command execution exceptions
    """
    def __init__(self, message, short):
        super(ShellException, self).__init__(message)
        self.short_message = short


class CommandException(ShellException):
    """Base class for all exceptions relating to command execution
    """
    def __init__(self, message, short='internal command error'):
        super(CommandException, self).__init__(message, short)


class CommandNotFoundException(CommandException):
    """Exception use when a command does not exist
    """
    def __init__(self, message, short='command not found'):
        super(CommandNotFoundException, self).__init__(message, short)


class CommandBadImplemented(CommandException):
    """Exception raised when a command class does not implement the required methods
    """
    pass


class CommandForbidden(CommandException):
    """Raised when you tried to run a command not available from the current state
    """
    def __init__(self, message, short='command denied'):
        super(CommandForbidden, self).__init__(message, short)


class BadCommandCall(ShellException):
    """Raised when you call a command with bad arguments
    """
    def __init__(self, message, short='bad call, use help'):
        super(BadCommandCall, self).__init__(message, short)
