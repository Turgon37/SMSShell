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

"""A dummy metrics exporter, drop all metrics given to it
"""

# System imports
import logging

# Project imports
from . import AbstractMetricsHelper

# Global project declarations
g_logger = logging.getLogger('smsshell.metrics.none')


class MetricsHelper(AbstractMetricsHelper):
    """The base class for all metrics helpers
    """

    def init(self):
        """Init function
        """
        g_logger.info('Using dummy metrics helper')

    def start(self):
        """Do nothing

        Returns:
            True
        """
        return True

    def stop(self):
        """Do nothing

        Returns:
            True
        """
        return True

    def _counter(self, name, value=1, description=None, labels=None):
        """Do nothing

        Returns:
            mixed (self)
        """
        return self

    def _gauge(self, name, value=None, set=None, callback=None, description=None, labels=None):
        """Do nothing

        Returns:
            mixed (self)
        """
        return self
