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

"""This module contains some abstracts classes
"""


class AbstractModule():
    """This abstract class is used to defined common base feature for modules
    """

    def __init__(self, config=None, metrics=None):
        """Constructor :

        Args:
            config : dict config all available configuration keys
            metrics : the metrics handler
        """
        if not config:
            config = dict()
        self.config = config
        self.metrics = metrics
        self.init()

    def get_config(self, key, fallback=None):
        """Return a configuration value or a default value if not found

        @param str key the name of the configuration value
        @param mixed fallback the default value to return if the key don't
                        exit in the configuration store
        """
        if key in self.config:
            return self.config[key]
        return fallback

    def init(self):
        """Put here some specific initialisations features
        """
