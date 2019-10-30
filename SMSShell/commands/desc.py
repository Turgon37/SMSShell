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

"""Desc command

This command return a short description of what a command do
"""

from . import AbstractCommand, CommandException


class Desc(AbstractCommand):
    """Command class, see module docstring for help
    """

    def args_parser(self):
        parser = self.create_args_parser()
        parser.add_argument("command", help="The command's name")
        parser.add_argument("command_argv", nargs='*', default=[],
                            help="optional argument to pass to desc")
        return parser

    def usage(self, argv):
        return 'desc COMMAND'

    def description(self, argv):
        return 'Show commands short description'

    def main(self, argv, pargs):
        try:
            return self.shell.get_command(self.session,
                                          pargs.command).description(pargs.command_argv)
        except CommandException as ex:
            self.log.error("error during command execution : %s", str(ex))
            return 'command not available'
