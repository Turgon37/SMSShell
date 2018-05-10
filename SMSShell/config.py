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

"""
"""

# System imports
import grp
import logging
import pwd
import re
import sys
from configparser import ConfigParser
from configparser import Error

# Project imports

# Global project declarations
g_logger = logging.getLogger('smsshell.config')


class MyConfigParser(ConfigParser):
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
        ConfigParser.__init__(self)

        # boolean that indicates if the configparser is available
        self.__is_config_loaded = False

    def load(self, path):
        """Try to load the configuration file

        @param path [str] : the path of the config file
        @return [boolean] : True if loading is sucess
        False if loading fail
        """
        # if file is defined
        if path is None:
            return False

        if path in self.read(path):
            self.__is_config_loaded = True
        return self.__is_config_loaded

    def isLoaded(self):
        """Return the load state of this config parser

        @return [boolean] : the boolean that indicates if the config
        file is loaded or not
        """
        return self.__is_config_loaded

    def getPidPath(self, default='/var/run/smsshell.pid'):
        """Return path to pid file option

        @param default [str] : the default value to return if nothing is found
        in the config file
        @return [str] : the logtarget
        """
        return self.get(self.MAIN_SECTION, 'pid', fallback=default)

    def getLogLevel(self, default='INFO'):
        """Return loglevel option from configuration file

        @param default [str] : the default value to return if nothing is found
        in the config file
        @return [str] : the loglevel
        """
        return self.__getValueInArray(self.MAIN_SECTION, 'log_level', self.LOGLEVEL_MAP, default)

    def getLogTarget(self, default='STDOUT'):
        """Return logtarget option

        @param default [str] : the default value to return if nothing is found
        in the config file
        @return [str] : the logtarget
        """
        return self.get(self.MAIN_SECTION, 'log_target', fallback=default)

    def getUid(self):
        """Return the uid (int) option from configfile

        @return [int/None]: integer : the numeric value of
            None: if group is not defined
        """
        user = self.get(self.MAIN_SECTION, 'user', fallback=None)
        if not user:
            return None
        try:
            return pwd.getpwnam(user).pw_uid
        except KeyError:
            g_logger.error("Incorrect username '%s' read in configuration file", user)
        return None

    def getGid(self):
        """Return the gid (int) option from configfile

        @return [int/None] : integer : the numeric value of group id
        None: if group is not defined
        """
        group = self.get(self.MAIN_SECTION, 'group', fallback=None)
        if not group:
            return None
        try:
            return grp.getgrnam(group).gr_gid
        except KeyError:
            g_logger.error("Incorrect groupname '%s' read in configuration file", group)
        return None

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
        else:
            return val
