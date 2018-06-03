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

"""This module contains the personalised config parser for smsshell
"""

# System imports
import configparser
import logging

# Project imports
from .utils import userToUid, groupToGid

# Global project declarations
g_logger = logging.getLogger('smsshell.config')


class MyConfigParser(configparser.ConfigParser):
    """(extend ConfigParser) Set specific function for configuration file parsing

    Refer to the config file provide some function to parse directly the config
    file as project's needed. This class give highlevel configuration file reading
    """

    # CLASS CONSTANTS
    # list of logging level available by configuration file
    LOGLEVEL_MAP = ['ERROR', 'WARN', 'INFO', 'DEBUG']
    MODE_MAP = ['DAEMON', 'STANDALONE']
    MAIN_SECTION = 'main'

    def __init__(self):
        """Constructor : init a new config parser
        """
        configparser.ConfigParser.__init__(self)

        # boolean that indicates if the configparser is available
        self.__is_config_loaded = False

    def load(self, path):
        """Try to load the configuration file

        @param path [str] : the path of the config file
        @return [boolean] : True if loading is sucess
        False if loading fail
        """
        assert path is not None
        msg = 'ok'
        try:
            if path in self.read(path):
                self.__is_config_loaded = True
        except configparser.Error as ex:
            msg = 'Unable to load the configuration file because of error : {}'.format(str(ex))
        return self.__is_config_loaded, msg

    def isLoaded(self):
        """Return the load state of this config parser

        @return [boolean] : the boolean that indicates if the config
        file is loaded or not
        """
        return self.__is_config_loaded

    def getLogLevel(self, section=MAIN_SECTION, item='log_level', default='INFO'):
        """A log level option from configparser

        Ensure the returned value is a valid log level acceptable by logging module

        Args:
            section: the section name from which to pick up the value
                            Default to main section
            item: the name of the item from which to pick up the value
                            Default to 'log_level'
            default: the fallback value to return if the item is not found
                        or if the item value is not valid
        Returns:
            the validated log level as a string or the default's value
        """
        return self.__getValueInArray(section, item, self.LOGLEVEL_MAP, default)

    def getUid(self, section=MAIN_SECTION, item='user', default=None):
        """Return the uid corresponding to a value in configuration file

        Args:
            section: the section name from which to pick up the value
                        Default to main section
            item: the name of the item from which to pick up the value
                        Default to 'user'
            default: the fallback value to return if the item is not found
                    or if the item value is not valid
        Returns:
            the uid as integer object or the default's value
        """
        user = self.get(section, item, fallback=None)
        if not user:
            return default
        try:
            return userToUid(user)
        except KeyError:
            g_logger.error(("Incorrect user name '%s' read in configuration"
                            " file at section %s and key %s"), user, section, item)
        return default

    def getGid(self, section=MAIN_SECTION, item='group', default=None):
        """Return the gid corresponding to a value in configuration file

        Args:
            section: the section name from which to pick up the value
                        Default to main section
            item: the name of the item from which to pick up the value
                        Default to 'group'
            default: the fallback value to return if the item is not found
                    or if the item value is not valid
        Returns:
            the gid as integer object or the default's value
        """
        group = self.get(section, item, fallback=None)
        if not group:
            return default
        try:
            return groupToGid(group)
        except KeyError:
            g_logger.error(("Incorrect group name '%s' read in configuration"
                            " file at section %s and key %s"), group, section, item)
        return default

    def getMode(self):
        """Return the main mode of this application

        @return str : the current mode if it belong to the availables values
                        an empty string otherwise
        """
        return self.__getValueInArray(self.MAIN_SECTION, 'mode', self.MODE_MAP, 'DAEMON')

    def getModeConfig(self, key, fallback=None):
        """Return a configuration option of the current mode

        @param str key the name of the configuration
        @param fallback the default value to return
        @return mixed
        """
        return self.get(self.getMode().lower(), key, fallback=fallback)

    def getSectionOrEmpty(self, name):
        """Return all options in a section if exists or empty dict if not

        @param str the name the section
        @return dict the dict which contains all options of the section
        """
        if self.has_section(name):
            return dict(self.items(name))
        return dict()

    def __getValueInArray(self, section, key, array, default=None):
        """Test if a value is in an array

        @param str section the name of the sections
        @param str key the name of the configuration option
        @param list array of the possible values
        @param mixed default
        @return mixed the value if it is in the range or the default value
        """
        val = self.get(section, key, fallback=default)
        if val not in array:
            g_logger.error("Incorrect %s : '%s' must be in %s", key, val, array)
            return default
        return val
