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

"""
"""

# System imports
import logging

# Project imports
from .exceptions import ShellException,CommandNotFoundException
from .models import Session

# Global project declarations
g_logger = logging.getLogger('smsshell.shell')


class Shell(object):
  """
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
    @param argv [list]
    """
    if len(argv) < 1:
      raise ShellException('bad number of arguments')
    cmd = argv[0]
    if len(cmd) == 0:
      raise ShellException('empty command name')
    if len(subject) == 0:
      raise ShellException('empty subject name')
    sess = self.__getSessionForSubject(subject)
    return self.__call(sess, cmd, argv[2:])

  def __call(self, session, cmd, argv):
    """
    """
    if cmd not in self.__commands:
      self.__loadCommand(cmd)
    return self.__commands[cmd].main(argv)

  def __loadCommand(self):
    pass

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
