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

"""This package contains all available commands
"""

# Project imports
from ..exceptions import CommandBadImplemented


class AbstractCommand(object):
    """This is a abstract command, all user defined comand must inherit this one"""

    def __init__(self, logger, shell):
        """Build a new instance of the command

        @param [Logger] : the logger instance to use
        """
        self.log = logger
        self.shell = shell
        self.session = None

    @property
    def session(self):
        """Return the session associated with the request

        @return [models.Session] the session id
        """
        assert self.__session is not None
        return self.__session

    @session.setter
    def session(self, s):
        """Set the session's associated with the request

        @param s [str] : the session
        @return self
        """
        self.__session = s
        return self

    def main(self, argv):
        """The main running entry point of this command

        @param List<Str> the list of arguments
        """
        raise CommandBadImplemented(str(self.__class__) + " must implement the main function")

    def usage(self, argv):
        """This function must return a short usage message

        @param List<Str> the list of arguments
        """
        raise CommandBadImplemented(str(self.__class__) + " must implement the usage function")

    def description(self, argv):
        """This function must return a short description message of what the command do

        @param List<Str> the list of arguments
        """
        raise CommandBadImplemented(str(self.__class__) + " must implement the description function")

    def _inputStates(self):
        """Private entry point for Shell
        """
        l = self.inputStates()
        if not isinstance(l, list):
            raise CommandBadImplemented(str(self.__class__) + " inputStates function must return a list of session's states")
        return l

    def inputStates(self):
        """This function must return the list of session's state(s) from which
         the command can be run

        @return List<Session.SESS_*>
        """
        raise CommandBadImplemented(str(self.__class__) + " must implement the inputStates function")

    def _argsProperties(self):
        """Private entry point for Shell
        """
        props = {'min': 0, 'max': -1}
        p = self.argsProperties()
        if not isinstance(p, dict):
            raise CommandBadImplemented(str(self.__class__) + " argsProperties function must return a dict of properties")
        for k in p:
            props[k] = p[k]
        return props

    def argsProperties(self):
        """This function must return the list of session's state(s) from which
         the command can be run

        @return List<Session.SESS_*>
        """
        raise CommandBadImplemented(str(self.__class__) + " must implement the argsProperties function")
