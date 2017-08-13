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

        @return List<SessionRole>
        """
        raise CommandBadImplemented(str(self.__class__) + " must implement the inputStates function")

    def _argsProperties(self):
        """Private entry point for Shell
        """
        props = {'min': 0, 'max': -1}
        try:
            p = self.argsProperties()
        except NameError as e:
            raise CommandBadImplemented(str(self.__class__) + " argsProperties function encounter an error {}".format(e))
        if not isinstance(p, dict):
            raise CommandBadImplemented(str(self.__class__) + " argsProperties function must return a dict of properties")
        for k in p:
            props[k] = p[k]
        return props

    def argsProperties(self):
        """This function must return the list of session's state(s) from which
         the command can be run

        @return dict{}
        """
        raise CommandBadImplemented(str(self.__class__) + " must implement the argsProperties function")
