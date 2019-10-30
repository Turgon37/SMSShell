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
import logging

# Project imports
from ..exceptions import ShellException, BadCommandCall
from ..models import SessionStates


#
# COMMANDS RELATED EXCEPTIONS
#

class CommandException(ShellException):
    """Base class for all exceptions relating to command execution
    """
    def __init__(self, message, short='internal command error'):
        super().__init__(message, short)


class CommandNotFoundException(CommandException):
    """Exception use when a command does not exist
    """
    def __init__(self, message, short='command not found'):
        super().__init__(message, short)


class CommandBadImplemented(CommandException):
    """Exception raised when a command class does not implement the required methods
    """


class CommandForbidden(CommandException):
    """Raised when you tried to run a command not available from the current state
    """
    def __init__(self, message, short='command denied'):
        super().__init__(message, short)


class CommandBadConfiguredException(CommandException):
    """Exception use when a command do not validate it's configuration
    """
    def __init__(self, message, short='command not configured'):
        super().__init__(message, short)


class AbstractCommand():
    """This is a abstract command, all user defined comand must inherit this class
    """

    class ArgParser(argparse.ArgumentParser):
        """Customized argparser class

        This class should be instanciated using the createArgsParser() method
        """

        def __init__(self, *args, **kwargs):
            """Override default constructors
            """
            kwargs['add_help'] = False
            super().__init__(*args, **kwargs)

        def error(self, message):
            """Raise custom exception on parse error

            Args:
                message: The error message

            Raises:
                BadCommandCall with the original message
            """
            raise BadCommandCall(message)

    def __init__(self, logger, shell, config, metrics):
        """Build a new instance of the command

        Args:
            logger: the logger instance to use for this command
            Shell: the caller shell instance
            dict: the config dict specific for this command
        """
        self.__session = None

        assert isinstance(logger, logging.Logger)
        self.log = logger
        self.shell = shell
        self.config = config
        self.metrics = metrics
        self.session = None

    #
    # PUBLIC PROPERTIES
    #

    @property
    def name(self):
        """Return this command name

        Returns:
            Command name as String
        """
        return self.__class__.__name__.lower()

    @property
    def session(self):
        """Return the session associated with the request

        Returns:
            models.Session the session of the current run of this command

            Each time this command is run, the session is replaced by
                the session of the current user
        """
        assert self.__session is not None
        return self.__session

    @session.setter
    def session(self, sess):
        """Set the session's associated with the request

        Args:
            sess: the new session
        Returns:
            self the instance of this command
        """
        self.__session = sess
        return self

    #
    # PUBLIC METHODS
    #

    def argsParser(self):
        # pylint: disable=R0201
        """Return the argparser that the command will use to validate it's arguments

        The usage of an arg parser is optionnal. It allow the user's command
        to be more complicated in the manner it takes arguments

        Returns:
            must return an instance of AbstractCommand.ArgParser,
            use createArgsParser() to create a new and customize it before
            return it
        """
        return None

    def checkConfig(self):
        """Validates the configuration required by the command

        Returns:
            A boolean, true if the configuration is reported as valid,
            false otherwise
        """
        assert self
        return True

    def createArgsParser(self):
        """Build helper for new arguments parser

        Returns:
            a new instance of an empty AbstractCommand.ArgParser
        """
        return AbstractCommand.ArgParser(description=self.description([]),
                                         prog=self.name)

    def description(self, argv):
        """This function must return a short description message of what the command do

        Args:
            argv: List<String> the list of arguments if the user send it
                    It may be used to customize the help message with
                    the already send arguments
        Returns:
            The description of this command as a string
        """
        raise CommandBadImplemented(str(self.__class__) +
                                    " must implement the description function")

    def inputStates(self):
        # pylint: disable=R0201
        """This function must return the list of session's state(s) from which
         the command can be reacheable

        Returns:
            List<SessionStates> the list of SessionStates from which the user
            can run this command
        """
        return []

    def main(self, argv):
        """The main running entry point of this command

        Args:
            argv: List<String> the list of arguments
        Returns:
            Optional output that will be send back to original user
        """
        raise CommandBadImplemented(str(self.__class__) + " must implement the main function")

    def usage(self, argv):
        """This function must return a short usage message

        It is use to help the user to type command line.
        By default, is an argument parser is set, it will be used to produce
        an usage string

        Args:
            argv: List<String> the list of arguments if the user send it
                    It may be used to customize the help message with
                    the already send arguments
        Returns:
            the usage help as a String
        """
        parser = self._argsParser()
        if parser:
            parser.parse_known_args(argv)
            return parser.format_usage()
        raise CommandBadImplemented(str(self.__class__) + " must implement the usage function")

    #
    # PRIVATE PROPERTIES
    #

    def _inputStates(self):
        """Private entry point for Shell

        Returns:
            the list of input states formatted and validated for shell usage
        """
        states = self.inputStates()
        if not isinstance(states, list):
            raise CommandBadImplemented(str(self.__class__) + ' inputStates function must return'
                                        " a list of session's states")
        for state in states:
            if not isinstance(state, SessionStates):
                raise CommandBadImplemented(str(self.__class__) + ' inputStates function must'
                                            ' return a list of valid SessionStates objects')
        return states

    def _argsParser(self):
        """Private entry point for Shell

        Returns:
            The argparser formatted and validated for Shell usage
        """
        try:
            parser = self.argsParser()
        except BaseException as ex:
            raise CommandBadImplemented(str(self.__class__) +
                                        " argsParser function encounter an error {}".format(ex))
        if parser:
            if not isinstance(parser, AbstractCommand.ArgParser):
                raise CommandBadImplemented(str(self.__class__) + 'argsParser function ' +
                                            "must return a instance of ArgumentParser")
            if parser.add_help:
                raise CommandBadImplemented(str(self.__class__) + ' your argparser'
                                            " must not contains predefined help option")
        return parser
