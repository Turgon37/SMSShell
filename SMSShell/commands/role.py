# -*- coding: utf8 -*-

# This file is a part of SMSShell
#
# Copyright (c) 2016-2017 Pierre GINDRAUD
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

"""Role command

This command return the current role name
"""

from . import AbstractCommand


class Role(AbstractCommand):

    def argsProperties(self):
        return dict()

    def inputStates(self):
        return []

    def usage(self, argv):
        return 'role'

    def description(self, argv):
        return 'print current role'

    def main(self, argv):
        return str(self.session.state.name)
