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

"""This package contains all available commands
"""

# system imports
import argparse

# Project imports
from ..exceptions import CommandBadImplemented, BadCommandCall


class AbstractCommand(object):
    """This is a abstract command, all user defined comand must inherit this one"""

    class ArgParser(argparse.ArgumentParser):
        def __init__(self, *args, **kw):
            kw['add_help'] = False
            super().__init__(*args, **kw)

        def error(self, message):
            raise BadCommandCall(message)

    def __init__(self, logger, shell, config):
        """Build a new instance of the command

        @param [logging.Logger] : the logger instance to use
        @param [Shell] : the logger instance to use
        @param [dict] : the config dict
        """
        self.log = logger
        self.shell = shell
        self.config = config
        self.session = None

    @property
    def name(self):
        return self.__class__.__name__.lower()

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

    def checkConfig(self):
        """Validates the configuration required by the command
        """
        return True

    def main(self, argv, args=None):
        """The main running entry point of this command

        @param List<Str> the list of arguments
        @param dict OPTIONAL the dict that contains arg parser results
        """
        raise CommandBadImplemented(str(self.__class__) + " must implement the main function")

    def usage(self, argv):
        """This function must return a short usage message

        @param List<Str> the list of arguments
        @return str the string usage
        """
        if self._argsParser():
            parser = self._argsParser()
            parser.parse_known_args(argv)
            return parser.format_usage()
        raise CommandBadImplemented(str(self.__class__) + " must implement the usage function")

    def description(self, argv):
        """This function must return a short description message of what the command do

        @param List<Str> the list of arguments
        @return str the string description
        """
        raise CommandBadImplemented(str(self.__class__) + " must implement the description function")

    def _inputStates(self):
        """Private entry point for Shell

        @return the list of input states formatted and validated for shell usage
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
        return []

    def _argsProperties(self):
        """Private entry point for Shell

        @return the properties array formatted and validated for Shell usage
        """
        props = {'min': 0, 'max': -1}
        try:
            p = self.argsProperties()
        except BaseException as e:
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
        return dict()

    def newArgsParser(self):
        """Build helper for new arguments parser

        @return AbstractCommand.ArgParser new instance
        """
        return AbstractCommand.ArgParser(description=self.description([]), prog=self.name)

    def _argsParser(self):
        """Private entry point for Shell

        @return the argparser formatted and validated for Shell usage
        """
        try:
            parser = self.argsParser()
        except BaseException as e:
            raise CommandBadImplemented(str(self.__class__) + " argsParser function encounter an error {}".format(e))
        if parser:
            if not isinstance(parser, AbstractCommand.ArgParser):
                raise CommandBadImplemented(str(self.__class__) + " argsParser function must return a instance of ArgumentParser")
            if parser.add_help == True:
                raise CommandBadImplemented(str(self.__class__) + " your argparser must not contains predefined help option")
        return parser

    def argsParser(self):
        """Return the argparser that the command will use

        The usage of an arg parser is optionnal. It allow the user's command
        to be more complicated in the manner it takes arguments

        @return AbstractCommand.ArgParser
        """
        return None
