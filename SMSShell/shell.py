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

"""This module contains the main class of SMS Shell
"""

# System imports
import argparse
import importlib
import importlib.util
import inspect
import logging
import re
import os
import shlex

# Project imports
from .exceptions import ShellException, BadCommandCall
from .models import Session, SessionStates
from .commands import (AbstractCommand,
                       CommandForbidden,
                       CommandNotFoundException,
                       CommandBadImplemented,
                       CommandBadConfiguredException,
                       CommandException)

# Global project declarations
g_logger = logging.getLogger('smsshell.shell')


class Shell(object):
    """This class is the execution core of the shell

    It manage all available command, handle sessions, distribute
    command execution over commands instance
    """
    WORD_REGEX_PATTERN = re.compile("[^A-Za-z]+")

    def __init__(self, configparser, metrics):
        """Constructor: Build a new shell object

        Args:
            configparser: the program configparser
        """
        self.configparser = configparser
        self.__metrics = metrics
        self.__sessions = dict()
        self.__commands = dict()

    def exec(self, subject, cmdline, as_role=None):
        """Run the given arguments for the given subject

        Args:
            subject: an identifier of the command launcher
            cmdline: the raw command line
        """
        try:
            argv = shlex.split(cmdline)
        except ValueError as ex:
            raise ShellException('Command line parsing failed because of bad syntax: ' + str(ex),
                                 'bad syntax: ' + str(ex).lower().strip())
        if not argv:
            raise ShellException('Not enough arguments in arguments vector',
                                 'bad number of arguments')

        cmd = argv[0]
        if not cmd:
            raise ShellException('Cannot extract command name from shell command line')

        if not subject:
            raise ShellException('The passed subject is empty')

        g_logger.info("Subject '%s' run command '%s' with args : %s", subject, cmd, str(argv[1:]))
        if as_role is not None:
            assert isinstance(as_role, SessionStates)
            sess = Session(subject, time_to_live=0)
            sess.forceState(as_role)
            g_logger.info("Subject '%s' run command '%s' as forced role : %s",
                          subject, cmd, as_role.name)
        else:
            sess = self.__getSessionForSubject(subject)
        return self.__call(sess, cmd, argv[1:]).strip()

    def flushCommandCache(self):
        """Perform a flush of all command instance in local cache

        This cause that all next call to each command will require the
        re-instanciation of the command
        """
        self.__commands = dict()

    def getCommand(self, session, name):
        """Return the command instance of the given command name as the session

        Args:
            session: the session that is trying to access the command
            name: the command name to retrieve
        Returns:
            commands.Command the command instance
        Raises:
            CommandForbidden is the given session is not allowed to run
            the requested command
        """
        com = self.__getCommand(name)
        if not Shell.hasSessionAccessToCommand(session, com):
            raise CommandForbidden('You are not allowed to call this command from here')
        return com

    def __getCommand(self, name):
        """Return the command instance of the given command name

        Args:
            name: the name of the command to retrieve
        Returns:
            commands.Command instance
        """
        if name not in self.__commands:
            self.__loadCommand(name)
        return self.__commands[name]

    def __loadCommand(self, name):
        """Try to load the given command into the cache dir

        Args:
            name: the name of the command to load
        Returns:
            commands.Command instance
        Raises:
            CommandNotFoundException if the command do not exists
        """
        g_logger.debug("loading command handler with name '%s'", name)
        try:
            mod = importlib.import_module('.commands.' + name, package='SMSShell')
            if importlib.util.find_spec('.commands.' + name, package='SMSShell') is not None:
                importlib.reload(mod)
        except ImportError:
            raise CommandNotFoundException(("Command handler '{0}' cannot" +
                                            " be found in commands/ folder.").format(name))

        cls_name = Shell.toCamelCase(name)
        try: # instanciate
            class_obj = getattr(mod, cls_name)
            cmd = class_obj(g_logger.getChild('command.' + name),
                            self.getSecureShell(),
                            self.configparser.getSectionOrEmpty('command.' + name),
                            self.__metrics)
        except AttributeError as ex:
            raise CommandBadImplemented("Error in command '{0}' : {1}.".format(name, str(ex)))

        # handler class checking
        if not isinstance(cmd, AbstractCommand):
            raise CommandBadImplemented("Command " +
                                        "'{0}' must extend AbstractCommand class".format(name))

        # check configuration of the command
        if not cmd.checkConfig():
            raise CommandBadConfiguredException(("Command '{0}' is misconfigured. "
                                                 "Check the command doc to add missing "
                                                 "'command.{0}' section").format(name))
        g_logger.debug("command '%s' config ok", name)

        # register command into cache
        self.__commands[name] = cmd

    def getAvailableCommands(self, session):
        """Return the list of available command for the given session

        @param models.Session the session to use as subject
        @return List<Str> the list of command name
        """
        all_commands = []
        self.loadAllCommands()
        for key in self.__commands:
            if Shell.hasSessionAccessToCommand(session, self.__commands[key]):
                all_commands.append(key)
        return all_commands

    def loadAllCommands(self):
        """Load all availables command into the cache dir
        """
        for com in os.listdir(os.path.dirname(__file__) + "/commands"):
            if not com.startswith('_') and com.endswith(".py"):
                try:
                    self.__getCommand(os.path.splitext(com)[0])
                    # intercept exception to prevent command execution stop
                except CommandException as ex:
                    g_logger.error(str(ex))

    def __call(self, session, cmd_name, argv):
        """Execute the command with the given name

        Args:
            session: models.Session the session object to use
            cmd_name: the name of the command to call
            argv: the list of string arguments to pass to the command
        Returns:
            the command output
        """
        com = self.__getCommand(cmd_name)
        # set the prefix to separate session's namespaces
        session.setStoragePrefix(cmd_name)
        # check command aceptance conditions
        if not Shell.hasSessionAccessToCommand(session, com):
            raise CommandForbidden('You are not allowed to call this command from here')

        # parse arguments
        args = [argv]
        parser = com._argsParser()
        if parser:
            try:
                args.append(parser.parse_args(argv))
            except argparse.ArgumentError as ex:
                raise BadCommandCall('Error with command arguments: {}'.format(str(ex)))

        # check command signature
        sig = inspect.signature(com.main)
        if len(sig.parameters) != len(args):
            raise CommandBadImplemented(("main() function of command '{0}' "
                                         "must take {1} arguments").format(cmd_name, len(args)))

        # refresh session
        session.access()
        com.session = session.getSecureSession()
        result = com.main(*args)
        com.session = None

        # handler class checking
        if not isinstance(result, str):
            raise CommandBadImplemented(("Command '{0}' 's return object "
                                         "must be a str").format(cmd_name))
        return result

    @staticmethod
    def hasSessionAccessToCommand(session, command):
        """Check if the given session has access to the given command

        Args:
            session: a models.Session instance
            command: a commands.Command instance
        Returns:
            True if the given session is allowed to run the given command,
            false otherwise
        """
        states = command._inputStates()
        if states and session.state not in command._inputStates():
            return False
        return True

    def __getSessionForSubject(self, key):
        """Retrieve the session associated with this user

        @param str the name of the subject
        @return Session
        """
        if key in self.__sessions:
            sess = self.__sessions[key]
            if sess.isValid():
                g_logger.debug('using existing session')
                return sess

        self.__sessions[key] = Session(key)
        self.__sessions[key].ttl = self.configparser.getModeConfig('session_ttl', fallback=600)
        g_logger.debug('creating a new session for subject : %s with ttl %d',
                       key,
                       self.__sessions[key].ttl)
        return self.__sessions[key]


    def getSecureShell(self):
        """Return a secure wrapper of the shell

        Returns:
            instance of shell wrapper
        """
        class ShellWrapper(object):
            """This class if a wrapper for Shell

            It prevent some shell attributes to be accessed directly
            """
            ALLOWED_ATTRIBUTES = [
                'flushCommandCache',
                'getAvailableCommands',
                'getCommand'
            ]

            def __init__(self, shell):
                """Build a new shell wrapper

                Args:
                    shell: the initial shell instance
                """
                self.__shell = shell

            def __getattr__(self, name):
                """Allow some shell's functions to be accessed through shell wrapper

                Args:
                    name: the attribute's name
                Returns:
                    the shell attribute
                Raise:
                    ShellException if attribute is not allowed
                """
                if name in ShellWrapper.ALLOWED_ATTRIBUTES:
                    return getattr(self.__shell, name)
                raise ShellException('attribute {} is not reachable using shell wrapper'.format(name))

        return ShellWrapper(self)

    @classmethod
    def toCamelCase(cls, string):
        """Convert a string into camelcase
        """
        words = ' '.join(cls.WORD_REGEX_PATTERN.split(string))
        return ''.join(x for x in words.title() if not x.isspace())
