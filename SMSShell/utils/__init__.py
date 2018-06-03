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

"""This package contains some utilities
"""

# System imports
import grp
import pwd

# Project imports
from .gammusmsdparser import GammuSMSParser


def userToUid(user):
    """Convert an user name to it's uid if it exists

    If the user given is already an uid it is returned as is

    Args:
        user: the username or user uid
    Returns:
        the uid as integer
    Raises:
        KeyError: if the user name do not exists on the system
    """
    try:
        return int(user, 10)
    except ValueError:
        pass

    return pwd.getpwnam(user).pw_uid

def groupToGid(group):
    """Convert an group name to it's gid if it exists

    If the group given is already an gid it is returned as is

    Args:
        group: the group name or group gid
    Returns:
        the gid as integer
    Raises:
        KeyError: if the group name do not exists on the system
    """
    try:
        return int(group, 10)
    except ValueError:
        pass

    return grp.getgrnam(group).gr_gid
