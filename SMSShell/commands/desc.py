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

from . import AbstractCommand
from ..exceptions import CommandException


class Desc(AbstractCommand):

    def argsProperties(self):
        return dict(min=1, max=1)

    def usage(self, argv):
        return 'desc COMMAND'

    def description(self, argv):
        return 'Show commands short description'

    def main(self, argv):
        try:
            return self.shell.getCommand(self.session, argv[0]).description(argv[1:])
        except CommandException as e:
            self.log.error("error during command execution : " + str(e))
            return 'command not available'
