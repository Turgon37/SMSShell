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
import glob
import importlib
import importlib.util
import inspect
import logging
import re
import os
import shlex

# Project imports
from .exceptions import (ShellException,
                         BadCommandCall,
                         ShellImmediateAnswerException)
from .models import Session, SessionStates
from .commands import (AbstractCommand,
                       CommandForbidden,
                       CommandNotFoundException,
                       CommandBadImplemented,
                       CommandBadConfiguredException,
                       CommandException)

# Global project declarations
G_LOGGER = logging.getLogger('smsshell.shell')


class Shell():
    """This class is the execution core of the shell

    It manage all available command, handle sessions, distribute
    command execution over commands instance
    """
    # regex use to split a sentence in word
    WORD_REGEX_PATTERN = re.compile("[^A-Za-z]+")
    # regex use to validate command name
    NAME_REGEX_PATTERN = re.compile("^[a-z]+")
    # list of folder where to search for commands
    COMMANDS_PACKAGES = ['SMSShell']
    # prefix to apply on command module name
    COMMANDS_MODULE_PREFIX = '.commands'

    def __init__(self, configparser, metrics):
        """Constructor: Build a new shell object

        Args:
            configparser: the program configparser
            metrics : The general metrics handler
        """
        self.configparser = configparser
        self.__metrics = metrics
        self.__sessions = dict()
        self.__commands = dict()
        # declare metrics
        self.__metrics.counter('commands.loaded.total',
                               labels=['status'],
                               description='Number of loaded commands per status')
        self.__metrics.counter('sessions.activity.total',
                               labels=['status'],
                               description='Total used session per state')
        self.__metrics.gauge('sessions.objects.count',
                             callback=lambda: len(self.__sessions),
                             description='Current number of session in sessions directory')
        self.__metrics.counter('commands.call.total',
                               labels=['status', 'name'],
                               description='Number of commands call per name and status')

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

        G_LOGGER.info("Subject '%s' run command '%s' with args : %s", subject, cmd, str(argv[1:]))
        if as_role is not None:
            assert isinstance(as_role, SessionStates)
            sess = Session(subject, time_to_live=0)
            sess.force_state(as_role)
            G_LOGGER.info("Subject '%s' run command '%s' as forced role : %s",
                          subject, cmd, as_role.name)
        else:
            sess = self.__get_session_for_subject(subject)

        try:
            return self.__call(sess, cmd, argv[1:]).strip()
        except ShellImmediateAnswerException as ex:
            return str(ex)

    def flush_command_cache(self):
        """Perform a flush of all command instance in local cache

        This cause that all next call to each command will require the
        re-instanciation of the command
        """
        self.__commands = dict()

    def get_command(self, session, name):
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
        com = self.__get_command(name)
        if not Shell.has_session_access_to_command(session, com):
            raise CommandForbidden('You are not allowed to call this command from here')
        return com

    def __get_command(self, name):
        """Return the command instance of the given command name

        Args:
            name: the name of the command to retrieve
        Returns:
            commands.Command instance
        """
        if not self.NAME_REGEX_PATTERN.match(name):
            raise ShellException(("Command name '{0}' is invalid" +
                                  " be found in any package").format(name))

        load_package = None
        for pack in self.COMMANDS_PACKAGES:
            pack_spec = importlib.util.find_spec(pack)
            if pack_spec is None:
                G_LOGGER.debug("ignore non existent import package '%s'", pack)
                continue

            if not pack_spec.has_location:
                G_LOGGER.debug("ignore import package '%s' without location", pack)
                continue

            for pack_path in pack_spec.submodule_search_locations:
                test_basedir = os.path.realpath(
                    os.path.join(
                        pack_path,
                        self.COMMANDS_MODULE_PREFIX.replace('.', os.path.sep).lstrip('/'),
                    )
                )

                # first pass with absolute command name
                test_fullpath = os.path.join(test_basedir, name + '.py')
                if os.path.isfile(test_fullpath):
                    load_package = pack
                else:
                    test_globpath = os.path.join(test_basedir, name + '*.py')
                    match_globpath = glob.glob(test_globpath)
                    if len(match_globpath) == 1:
                        name, _ = os.path.splitext(os.path.basename(match_globpath[0]))
                        load_package = pack
                    elif len(match_globpath) > 1:
                        proposals = list(
                            map(
                                lambda x: os.path.splitext(os.path.basename(x))[0],
                                match_globpath
                            )
                        )
                        raise ShellImmediateAnswerException(
                            '#Tip: commands matches : {}'.format(' '.join(proposals))
                        )

        if not load_package:
            self.__metrics.counter('commands.loaded.total', labels=dict(status='error'))
            raise CommandNotFoundException(("Command handler '{0}' cannot" +
                                            " be found in any package").format(name))

        if name not in self.__commands:
            self.__load_command(name, load_package)
        return self.__commands[name]

    def __load_command(self, name, load_package):
        """Try to load the given command into the cache dir

        Args:
            name: the name of the command to load
        Returns:
            commands.Command instance
        Raises:
            CommandNotFoundException if the command do not exists
        """
        G_LOGGER.debug("loading command handler with name '%s'", name)

        try:
            module_name = self.COMMANDS_MODULE_PREFIX + '.' + name
            mod = importlib.import_module(module_name, package=load_package)
            # if final class was already imported, recompile it
            if importlib.util.find_spec(module_name, package=load_package) is not None:
                importlib.reload(mod)
        except ImportError:
            self.__metrics.counter('commands.loaded.total', labels=dict(status='error'))
            raise CommandNotFoundException(("Command handler '{}' cannot" +
                                            " be found in '{}' package").format(name, load_package))

        cls_name = Shell.to_camel_case(name)
        try: # instanciate
            class_obj = getattr(mod, cls_name)
            cmd = class_obj(G_LOGGER.getChild('command.' + name),
                            self.get_secure_shell(),
                            self.configparser.get_section_or_empty('command.' + name),
                            self.__metrics)
        except AttributeError as ex:
            self.__metrics.counter('commands.loaded.total', labels=dict(status='error'))
            raise CommandBadImplemented("Error in command '{0}' : {1}.".format(name, str(ex)))

        # handler class checking
        if not isinstance(cmd, AbstractCommand):
            self.__metrics.counter('commands.loaded.total', labels=dict(status='error'))
            raise CommandBadImplemented("Command " +
                                        "'{0}' must extend AbstractCommand class".format(name))

        # check configuration of the command
        if not cmd.check_config():
            self.__metrics.counter('commands.loaded.total', labels=dict(status='error'))
            raise CommandBadConfiguredException(("Command '{0}' is misconfigured. "
                                                 "Check the command doc to add missing "
                                                 "'command.{0}' section").format(name))
        G_LOGGER.debug("command '%s' config ok", name)

        # register command into cache
        self.__commands[name] = cmd
        self.__metrics.counter('commands.loaded.total', labels=dict(status='ok'))

    def get_available_commands(self, session):
        """Return the list of available command for the given session

        @param models.Session the session to use as subject
        @return List<Str> the list of command name
        """
        all_commands = []
        self.load_all_commands()
        for key in self.__commands:
            if Shell.has_session_access_to_command(session, self.__commands[key]):
                all_commands.append(key)
        return all_commands

    def load_all_commands(self):
        """Load all availables command into the cache dir
        """
        for com in os.listdir(os.path.dirname(__file__) + "/commands"):
            if not com.startswith('_') and com.endswith(".py"):
                try:
                    self.__get_command(os.path.splitext(com)[0])
                    # intercept exception to prevent command execution stop
                except CommandException as ex:
                    G_LOGGER.error(str(ex))

    def __call(self, session, cmd_name, argv):
        """Execute the command with the given name

        Args:
            session: models.Session the session object to use
            cmd_name: the name of the command to call
            argv: the list of string arguments to pass to the command
        Returns:
            the command output
        """
        com = self.__get_command(cmd_name)
        # set the prefix to separate session's namespaces
        session.set_storage_prefix(cmd_name)
        # check command aceptance conditions
        if not Shell.has_session_access_to_command(session, com):
            self.__metrics.counter('commands.call.total',
                                   labels=dict(status='error', name=cmd_name))
            raise CommandForbidden('You are not allowed to call this command from here')

        # parse arguments
        args = [argv]
        parser = com._args_parser()
        if parser:
            try:
                args.append(parser.parse_args(argv))
            except argparse.ArgumentError as ex:
                self.__metrics.counter('commands.call.total',
                                       labels=dict(status='error', name=cmd_name))
                raise BadCommandCall('Error with command arguments: {}'.format(str(ex)))

        # check command signature
        sig = inspect.signature(com.main)
        if len(sig.parameters) != len(args):
            self.__metrics.counter('commands.call.total',
                                   labels=dict(status='error', name=cmd_name))
            raise CommandBadImplemented(("main() function of command '{0}' "
                                         "must take {1} arguments").format(cmd_name, len(args)))

        # refresh session
        session.access()
        com.session = session.get_secure_session()
        result = com.main(*args)
        com.session = None

        # handler class checking
        if not isinstance(result, str):
            raise CommandBadImplemented(("Command '{0}' 's return object "
                                         "must be a str").format(cmd_name))
        self.__metrics.counter('commands.call.total', labels=dict(status='ok', name=cmd_name))
        return result

    @staticmethod
    def has_session_access_to_command(session, command):
        """Check if the given session has access to the given command

        Args:
            session: a models.Session instance
            command: a commands.Command instance
        Returns:
            True if the given session is allowed to run the given command,
            false otherwise
        """
        states = command.input_states()
        if not isinstance(states, list):
            raise CommandBadImplemented(str(command.__class__) + ' inputStates function must return'
                                        " a list of session's states")
        for state in states:
            if not isinstance(state, SessionStates):
                raise CommandBadImplemented(str(command.__class__) + ' inputStates function must'
                                            ' return a list of valid SessionStates objects')

        if states and session.state not in states:
            return False
        return True

    def __get_session_for_subject(self, key):
        """Retrieve the session associated with this user

        @param str the name of the subject
        @return Session
        """
        if key in self.__sessions:
            sess = self.__sessions[key]
            if sess.is_valid():
                G_LOGGER.debug('using existing session')
                self.__metrics.counter('sessions.activity.total', labels=dict(status='reused'))
                return sess
            self.__metrics.counter('sessions.activity.total', labels=dict(status='expired'))

        self.__sessions[key] = Session(key)
        self.__sessions[key].ttl = self.configparser.get_mode_config('session_ttl', fallback=600)
        G_LOGGER.debug('creating a new session for subject : %s with ttl %d',
                       key,
                       self.__sessions[key].ttl)
        self.__metrics.counter('sessions.activity.total', labels=dict(status='created'))
        return self.__sessions[key]

    def get_secure_shell(self):
        """Return a secure wrapper of the shell

        Returns:
            instance of shell wrapper
        """
        class ShellWrapper():
            # pylint: disable=R0903
            """This class if a wrapper for Shell

            It prevent some shell attributes to be accessed directly
            """
            ALLOWED_ATTRIBUTES = [
                'flush_command_cache',
                'get_available_commands',
                'get_command'
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
    def to_camel_case(cls, string):
        """Convert a string into camelcase
        """
        words = ' '.join(cls.WORD_REGEX_PATTERN.split(string))
        return ''.join(x for x in words.title() if not x.isspace())
