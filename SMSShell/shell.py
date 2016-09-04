# -*- coding: utf8 -*-

# This file is a part of SMSShell
#
# Copyright (c) 2016 Pierre GINDRAUD
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

__author__ = "Pierre GINDRAUD"
__copyright__ = "Copyright (C) 2016 Pierre GINDRAUD"
__license__ = "Public Domain"
__version__ = "1.0"

"""This module contains the main class of SMS Shell
"""

# System imports
import logging

# Project imports
from .exceptions import ShellException,CommandNotFoundException,CommandBadImplemented,CommandForbidden,BadCommandCall
from .models import Session
from .commands import AbstractCommand

# Global project declarations
g_logger = logging.getLogger('smsshell.shell')


class Shell(object):
  """Build a new instance a Shell
  """

  def __init__(self, configparser):
    """Constructor: Build a new message object

    @param sender [str] : sender unique identifier
    @param content [str] : message content
    """
    self.cp = configparser
    self.__sessions = dict()
    self.__commands = dict()

  def run(self, subject, argv):
    """Run the given arguments for the given subject

    @param subject [str]
    @param argv [list<str>]
    """
    if len(argv) < 1:
      raise ShellException('bad number of arguments')
    cmd = argv[0]
    if len(cmd) == 0:
      raise ShellException('empty command name')
    if len(subject) == 0:
      raise ShellException('empty subject name')
    sess = self.__getSessionForSubject(subject)
    g_logger.info("Subject {0} run command '{1}' with args : {2}".format(subject, cmd, str(argv[1:])))
    return self.__call(sess, cmd, argv[1:])

  def flushCommandCache(self):
    """Perform a flush of all command instance in local cache

    This cause that all next call to each command will require the
    re-instanciation of the command
    """
    self.__commands = dict()

  def __call(self, session, cmd, argv):
    """Execute the command with the given name

    @param session models.Session
    @param cmd [str]
    @param argv [List<str>]
    @return the command output
    """
    if cmd not in self.__commands:
      self.__loadCommand(cmd)
    c = self.__commands[cmd]
    session._setPrefix(cmd)
    # check command aceptance conditions
    if len(c._inputStates()) > 0 and session.state not in c._inputStates():
      raise CommandForbidden('You are not allowed to call this command from here')
    self.__checkArgv(argv, c._argsProperties())

    # refresh session
    session._access()
    c.session = session
    result = c.main(argv)
    c.session = None

    # handler class checking
    if not isinstance(result, str):
      raise CommandBadImplemented("Command '{0}' 's return object must be a str".format(name))
    return result


  def __checkArgv(self, argv, properties):
    """Check the given arguments according to the specifications

    @param argv List<Str> the lsit of arguments
    @param properties [dict]
    @throw ShellException
    """
    if len(argv) < properties['min']:
      raise BadCommandCall('This command require at least {0} arguments'.format(properties['min']))
    if properties['max'] != -1 and properties['max'] < len(argv):
      raise BadCommandCall('This command require at most {0} arguments'.format(properties['max']))


  def __loadCommand(self, name):
    """Try to load the given command into the cache dir

    @param name [str] the name of the command to load
    @return Command instance
    @throw ShellException
    """
    g_logger.debug("loading command handler with name '%s'", name)
    try:
      mod = __import__('SMSShell.commands.' + name, fromlist=['Command'])
    except ImportError as e:
      raise CommandNotFoundException("Command handler '{0}' cannot be found in commands/ folder.".format(name))

    try: # instanciate
      cmd = mod.Command(g_logger.getChild('com.' + name))
    except AttributeError as e:
      raise CommandBadImplemented("Error in command '{0}' : {1}.".format(name, str(e)))

    # handler class checking
    if not isinstance(cmd, AbstractCommand):
      g_sys_log.error("Command '%s' must extend AbstractCommand class", name)
      raise CommandBadImplemented()
    # register command into cache
    self.__commands[name] = cmd


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

    g_logger.debug('creating a new session for subject : ' + key)
    self.__sessions[key] = Session(key)
    self.__sessions[key].ttl = self.cp.get('standalone', 'session_ttl', fallback=600)
    return self.__sessions[key]
