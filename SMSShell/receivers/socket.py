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
import os
import stat

# Global project declarations
g_logger = logging.getLogger('smsshell.socket')


class SocketReceiver(object):
  """
  """

  def __init__(self, config):
    """Constructor :

    @param config[ConfigParser] : the config parser
    """
    self.cp = config
    self.__path = config.get('standalone', 'path', fallback="/var/run/smsshell")

  def start(self):
    """Start the socket (FIFO) runner

    Init the fifo pipe and wait for incoming contents
    """
    directory = os.path.dirname(self.__path)
    # check permissions
    if not (os.path.isdir(directory) and os.access(directory, os.X_OK)):
      g_logger.fatal('Unsufficients permissions into socket directory')
      return False
    # check socket
    if os.path.exists(self.__path):
      if not stat.S_ISFIFO(os.stat(self.__path).st_mode):
        g_logger.fatal('The path given is already a file but not a fifo')
        return False
      g_logger.debug('using existing fifo')
    elif not os.path.exists(self.__path):
      # check directory write rights
      if not os.access(directory, os.X_OK|os.W_OK):
        g_logger.fatal('Unsufficients permissions into the directory to create the fifo')
        return False
      os.mkfifo(self.__path, mode=0o620)

  def read(self):
    """Return a read blocking iterable object for each content in the fifo

    @return Iterable
    """
    while True:
      with open(self.__path) as fifo:
        yield fifo.read()
