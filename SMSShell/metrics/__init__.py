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

"""This module contains abstract class for metrics helpers
"""

# Project imports
from ..abstract import AbstractModule


class AbstractMetricsHelper(AbstractModule):
    """An abstract metrics helper
    """
    PREFIX = 'smsshell'
    SEPARATOR = '.'

    def start(self):
        """Prepare the receiver/init connections

        Returns:
            True if init has success, otherwise False
        """
        raise NotImplementedError("You must implement the 'start' method in metrics helper class")

    def stop(self):
        """Close properly the receiver, flush, close connections

        Returns:
            True if stop has success, otherwise False
        """
        raise NotImplementedError("You must implement the 'stop' method in metrics helper class")

    def normalizeName(self, name):
        """Normalize the metric name for the current handler

        Args:
            name: the initial name of the metric
        Returns:
            the normalized name of the metric
        """
        path = name.replace('.', self.SEPARATOR)
        if path[0:len(self.PREFIX)] != self.PREFIX:
            return self.PREFIX + self.SEPARATOR + path
        return path

    def counter(self, name, value=1, description=None, labels=None):
        """Increase the given counter name by the given value

        Args:
            name: the name (the path) of the counter
            value: the value
            description: a description of the counter
              used in some handler, must be set on the first counter usage
        Returns:
            mixed (self)
        """
        return self._counter(self.normalizeName(name), value, description, labels)

    def _counter(self, name, value=1, description=None):
        """
        """
        raise NotImplementedError("You must implement the '_counter' method in metrics helper class")
