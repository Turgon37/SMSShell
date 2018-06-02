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

"""Help command

This command return some help string in function of the given input parameters

* If call without parameter : return the list of all available commands
* If call with a command name as first parameter, return the usage string of this function
  In this case you can pass some other parameter that will be send to command usage

"""

from . import AbstractCommand
from ..exceptions import CommandException


class Help(AbstractCommand):

    def argsProperties(self):
        return dict()

    def inputStates(self):
        return []

    def usage(self, argv):
        return 'help [COMMAND] [COMMAND ARGS]'

    def description(self, argv):
        return 'Show commands usage'

    def main(self, argv):
        # call usage function of the given command
        if len(argv) > 0:
            try:
                return self.shell.getCommand(self.session, argv[0]).usage(argv[1:])
            except CommandException as e:
                self.log.error("error during command execution : " + str(e))
                return 'command not available'
        # return the list of availables commands
        else:
            return ' '.join(self.shell.getAvailableCommands(self.session))
