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

"""Help command

This command return some help string in function of the given input parameters

* If call without parameter : return the list of all available commands
* If call with a command name as first parameter, return the usage string of this function
  In this case you can pass some other parameter that will be send to command usage

"""

from . import AbstractCommand
from ..exceptions import CommandException

class Command(AbstractCommand):

  def argsProperties(self):
    return dict(max=1)

  def inputStates(self):
    return []

  def usage(self, argv):
    return 'help [command] [command args]'

  def main(self, argv):
    # call usage function of the given command
    if len(argv) > 0:
      try:
        return self.shell.getCommand(self.session, argv[0]).usage(argv[1:])
      except CommandException:
        return 'command not available'
    # return the list of availables commands
    else:
      return ' '.join(self.shell.getAvailableCommands(self.session))
