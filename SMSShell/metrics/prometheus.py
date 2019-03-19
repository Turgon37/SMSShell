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

"""A Prometheus metrics exporter
"""

# System imports
import logging
import prometheus_client

# Project imports
from . import AbstractMetricsHelper

# Global project declarations
g_logger = logging.getLogger('smsshell.metrics.prometheus')


class MetricsHelper(AbstractMetricsHelper):
    """The base class for all metrics helpers
    """

    # set prometheus metrics separator
    SEPARATOR = '_'

    def init(self):
        """Init function
        """
        try:
            self.__port = int(self.getConfig('listen_port', fallback=8000))
        except ValueError:
            self.__port = 8000
            g_logger.error(("invalid integer parameter for option 'listen_port'"
                            ", fallback to default value 8000"))
        self.__address = self.getConfig('listen_address', fallback='')
        # initialized counters
        self.__counters = dict()

    def start(self):
        """Prepare the receiver/init connections

        Returns:
            True if init has success, otherwise False
        """
        g_logger.info('Prometheus metrics exporter started on %s:%d',
                      self.__address,
                      self.__port)
        prometheus_client.start_http_server(self.__port, self.__address)
        return True

    def stop(self):
        """Stop the prometheus handler

        Returns:
            True if init has success, otherwise False
        """
        return True

    def _counter(self, name, value=1, description=None):
        """Declare or increase a counter

        The counter is initialized on first usage, if you want to set
        its value to 0 on the beginning of the program, set value to 0

        Args:
            name: the name (the path) of the counter
            value: the value
            description: a description of the counter,
              required on first usage
        Returns:
            mixed (self)
        """
        if name not in self.__counters:
            # ensure description
            if not description:
                g_logger.warning(("First usage of count metric '%s' require a description,"
                                  " metric is discarded"), name)
                return self
            # create counter
            self.__counters[name] = prometheus_client.Counter(name, description)
        counter = self.__counters[name]
        assert counter

        if value > 0:
            counter.inc(value)
        return self
