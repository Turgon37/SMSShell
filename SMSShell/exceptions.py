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

"""This module define all operations related Exceptions
"""


class SMSException(Exception):
    pass

class ShellInitException(Exception):
    pass

class ShellException(Exception):
    def __init__(self, message, short):
        super(ShellException, self).__init__(message)
        self.short_message = short


class CommandException(ShellException):
    def __init__(self, message, short='internal command error'):
        super(CommandException, self).__init__(message, short)


class CommandNotFoundException(CommandException):
    def __init__(self, message, short='command not found'):
        super(CommandNotFoundException, self).__init__(message, short)


class CommandBadImplemented(CommandException):
    pass


class CommandForbidden(CommandException):
    def __init__(self, message, short='command denied'):
        super(CommandForbidden, self).__init__(message, short)


class BadCommandCall(ShellException):
    def __init__(self, message, short='bad call, use help'):
        super(BadCommandCall, self).__init__(message, short)
