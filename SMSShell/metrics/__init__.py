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

    def normalize_name(self, name):
        """Normalize the metric name for the current handler

        Args:
            name: the initial name of the metric
        Returns:
            the normalized name of the metric
        """
        path = name.replace('.', self.SEPARATOR)
        if path[0:len(self.PREFIX)] != self.PREFIX:
            return self.SEPARATOR.join([self.PREFIX, path])
        return path

    def counter(self, name, *args, **kwargs):
        """Declare or increase this counter by the value

        Args:
            name: the name (the path) of the counter
            value: the value
            description: a description of the counter
              used in some handler, must be set on the first counter usage
            labels:
        Returns:
            mixed (self)
        """
        return self._counter(self.normalize_name(name), *args, **kwargs)

    def _counter(self, name, value=1, description=None, labels=None):
        """Abstract final function that must realize the metrics handling
        """
        raise NotImplementedError("You must implement the '_counter' method in metrics helper class")

    def gauge(self, name, *args, **kwargs):
        """Declare and manipulate a gauge

        Args:
            name: the name (the path) of the gauge
            value: increase/decrease the gauge by this value
            set: set the value of the gauge
            callback: optional callback function to use to compute metric
            description: a description of the gauge
              used in some handler, must be set on the first counter usage
        Returns:
            mixed (self)
        """
        return self._gauge(self.normalize_name(name), *args, **kwargs)

    def _gauge(self, name, value=None, set_to=None, callback=None, description=None, labels=None):
        """Abstract final function that must realize the metrics handling
        """
        raise NotImplementedError("You must implement the '_gauge' method in metrics helper class")
