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
from threading import RLock

# Project imports
from .exceptions import (ShellException,
                         CommandForbidden,
                         CommandNotFoundException,
                         CommandBadImplemented,
                         CommandBadConfiguredException,
                         CommandException,
                         BadCommandCall)
from .models import Session, SessionRole
from .commands import AbstractCommand

# Global project declarations
g_logger = logging.getLogger('smsshell.shell')


class Shell(object):
    """Build a new instance a Shell
    """
    word_regex_pattern = re.compile("[^A-Za-z]+")

    def __init__(self, configparser):
        """Constructor: Build a new message object

        @param sender [str] : sender unique identifier
        @param content [str] : message content
        """
        self.cp = configparser
        self.__lock = RLock()
        self.__sessions = dict()
        self.__commands = dict()

    def synchronizedMethod(func):
        """Synchronize a method execution

        This decorator make a method synchronized
        @param method the method to be synchronized
        """
        def _synchronized(self, *args, **kw):
            with self.__lock:
                return func(self, *args, **kw)
        return _synchronized

    @synchronizedMethod
    def exec(self, subject, cmdline, role=None):
        """Run the given arguments for the given subject

        @param subject [str]
        @param argv [list<str>]
        """
        argv = shlex.split(cmdline)
        if len(argv) < 1:
            raise ShellException('bad number of arguments')
        cmd = argv[0]
        if not cmd:
            raise ShellException('empty command name')
        if not subject:
            raise ShellException('empty subject name')
        sess = self.__getSessionForSubject(subject)
        g_logger.info("Subject %s run command '%s' with args : %s", subject, cmd, str(argv[1:]))
        return self.__call(sess, cmd, argv[1:], role).strip()

    @synchronizedMethod
    def flushCommandCache(self):
        """Perform a flush of all command instance in local cache

        This cause that all next call to each command will require the
        re-instanciation of the command
        """
        self.__commands = dict()

    @synchronizedMethod
    def getCommand(self, session, name):
        """Return the command instance of the given command name

        @param [Str] the name of the command to retrieve
        @return Command instance
        """
        com = self.__getCommand(name)
        if not Shell.hasSessionAccessToCommand(session, com):
            raise CommandForbidden('You are not allowed to call this command from here')
        return com

    def __getCommand(self, name):
        """Return the command instance of the given command name

        @param [Str] the name of the command to retrieve
        @return Command instance
        """
        if name not in self.__commands:
            self.__loadCommand(name)
        return self.__commands[name]

    def __loadCommand(self, name):
        """Try to load the given command into the cache dir

        @param str name  the name of the command to load
        @return Command instance
        @throw ShellException
        """
        g_logger.debug("loading command handler with name '%s'", name)
        try:
            mod = importlib.import_module('.commands.' + name, package='SMSShell')
            if importlib.util.find_spec('.commands.' + name, package='SMSShell') is not None:
                importlib.reload(mod)
            #mod = __import__('SMSShell.commands.' + name, fromlist=['Command'])
        except ImportError:
            raise CommandNotFoundException("Command handler '{0}' cannot be found in commands/ folder.".format(name))

        cls_name = Shell.toCamelCase(name)
        try: # instanciate
            class_obj = getattr(mod, cls_name)
            cmd = class_obj(g_logger.getChild('command.' + name), self.getSecureShell(), self.cp.getSectionOrEmpty('command.' + name))
        except AttributeError as ex:
            raise CommandBadImplemented("Error in command '{0}' : {1}.".format(name, str(ex)))

        # handler class checking
        if not isinstance(cmd, AbstractCommand):
            raise CommandBadImplemented("Command '{0}' must extend AbstractCommand class".format(name))

        # check configuration of the command
        if not cmd.checkConfig():
            raise CommandBadConfiguredException("Command '{0}' is misconfigured. Check the command doc to add missing 'command.{0}' section".format(name))
        else:
            g_logger.debug("command '%s' config ok", name)

        # register command into cache
        self.__commands[name] = cmd

    @synchronizedMethod
    def getAvailableCommands(self, session):
        """Return the list of available command for the given session

        @param models.Session the session to use as subject
        @return List<Str> the list of command name
        """
        ls = []
        self.loadAllCommands()
        for key in self.__commands:
            if Shell.hasSessionAccessToCommand(session, self.__commands[key]):
                ls.append(key)
        return ls

    @synchronizedMethod
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

    @synchronizedMethod
    def __call(self, session, cmd_name, argv, role=None):
        """Execute the command with the given name

        @param models.Session session
        @param str the name of the command
        @param list<str> argv the command's arguments
        @return the command output
        """
        com = self.__getCommand(cmd_name)
        # set the prefix to separate session's namespaces
        session.setStoragePrefix(cmd_name)
        # check command aceptance conditions
        if not Shell.hasSessionAccessToCommand(session, com):
            raise CommandForbidden('You are not allowed to call this command from here')
        args = self.__checkArgv(argv, com)

        # refresh session
        session.access()
        com.session = session.getSecureSession()
        if role and isinstance(role, SessionRole):
            g_logger.info('override session role with %s', role.name)

        sig = inspect.signature(com.main)
        if com._argsParser() and args:
            if len(sig.parameters) != 2:
                raise CommandBadImplemented("Command '{0}' 's main() function must take two arguments".format(cmd_name))
            result = com.main(argv, args)
        else:
            if len(sig.parameters) != 1:
                raise CommandBadImplemented("Command '{0}' 's main() function must take two arguments".format(cmd_name))
            result = com.main(argv)
        com.session = None

        # handler class checking
        if not isinstance(result, str):
            raise CommandBadImplemented("Command '{0}' 's return object must be a str".format(cmd_name))
        return result

    @staticmethod
    def __checkArgv(argv, command):
        """Check the given arguments according to the specifications

        @param argv List<Str> the lsit of arguments
        @param properties [dict]
        @throw ShellException
        """
        if hasattr(command, 'argsParser') and command._argsParser():
            parser = command._argsParser()
            try:
                args = parser.parse_args(argv)
            except argparse.ArgumentError:
                raise BadCommandCall('This command require at least {0} arguments'.format('min'))
            return args

        properties = command._argsProperties()
        if len(argv) < properties['min']:
            raise BadCommandCall('This command require at least {0} arguments'.format(properties['min']))
        if properties['max'] != -1 and properties['max'] < len(argv):
            raise BadCommandCall('This command require at most {0} arguments'.format(properties['max']))

    @staticmethod
    def hasSessionAccessToCommand(sess, com):
        """Check if the given session has access to the given command

        @param models.Session the session to test
        @param Command the command to test access for
        @return [bool] the access status
        """
        if com._inputStates() and sess.state not in com._inputStates():
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
        self.__sessions[key].ttl = self.cp.getModeConfig('session_ttl', fallback=600)
        g_logger.debug('creating a new session for subject : %s with ttl %d', key, self.__sessions[key].ttl)
        return self.__sessions[key]


    def getSecureShell(self):
        """Return a secure wrapper of the shell
        """
        class ShellWrapper(object):
            def __init__(self, shell):
                self.__shell = shell

            def getAvailableCommands(self, *args, **kw):
                return self.__shell.getAvailableCommands(*args, **kw)

            def getCommand(self, *args, **kw):
                return self.__shell.getCommand(*args, **kw)

            def flushCommandCache(self, *args, **kw):
                return self.__shell.flushCommandCache(*args, **kw)

        return ShellWrapper(self)

    @classmethod
    def toCamelCase(cls, string):
        words = ' '.join(cls.word_regex_pattern.split(string))
        return ''.join(x for x in words.title() if not x.isspace())
