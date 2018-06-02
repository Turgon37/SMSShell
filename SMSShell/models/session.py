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

"""Models/Session This class represent an user session

"""

# System imports
import datetime
from enum import IntEnum, unique
import logging

# Global project declarations
g_logger = logging.getLogger('smsshell.models.session')


@unique
class SessionRole(IntEnum):
    """This enumeration reprensent the list of available roles
    """
    ROLE_GUEST = 0
    ROLE_LOGININPROGRESS = 1
    ROLE_USER = 2


class Session(object):
    """An user session with all user's meta data
    """

    # map of authorized session states transitions
    STATE_TRANSITION_MAP = {
        'ROLE_GUEST': ['ROLE_LOGININPROGRESS', 'ROLE_USER'],
        'ROLE_USER': ['ROLE_GUEST']
    }

    def __init__(self, subject, timetolive=600):
        """Constructor: Build a new session for the given subject

        @param sender [str] : session subject
        @param timetolive [int] OPTIONNAL : the number of second the session will be
                  alive
        """
        self.subject = subject
        self.ttl = timetolive
        self.state = SessionRole.ROLE_GUEST
        self.access()
        self.__prefix = None
        self.__created_at = datetime.datetime.today()
        self.__storage = dict()

    @property
    def subject(self):
        """Return the subject name

        @return [str] the subject id
        """
        assert self.__subject is not None
        return self.__subject

    @subject.setter
    def subject(self, s):
        """Set the subject id

        @param s [str] : the subject id
        @return self
        """
        self.__subject = s
        return self

    @property
    def state(self):
        """Return the current state

        @return [str] the subject id
        """
        assert self.__state is not None
        return self.__state

    @state.setter
    def state(self, s):
        """Set the session's state

        @param s [str] : the state constant
        @return self
        """
        assert isinstance(s, SessionRole)
        self.__state = s
        return self

    @property
    def created_at(self):
        """Return the created at datetime

        @return [Datetime] the datetime of the session creation
        """
        return self.__created_at

    @property
    def ttl(self):
        """Return the subject name

        @return [int] the subject id
        """
        assert self.__ttl is not None
        return int(self.__ttl.seconds)

    @ttl.setter
    def ttl(self, m):
        """Set the subject id

        @param m [int] : the number of minutes the session will be alive
        """
        self.__ttl = datetime.timedelta(seconds=int(m))

    @property
    def access_at(self):
        """Return the last access time

        @return [Datetime] the last access time
        """
        assert self.__access_at is not None
        return self.__access_at

    def access(self):
        """Refresh the access time of this session
        """
        self.__access_at = datetime.datetime.today()

    def isValid(self):
        """Check if this session is valid

        @return [bool] the validate status of this session
        """
        if (datetime.datetime.today() - self.access_at).seconds > self.ttl:
            g_logger.debug('session expired')
            return False
        return True

    def toRole(self, role):
        if not isinstance(role, SessionRole):
            raise CommandBadImplemented("The given role '{}' is not valid ".format(role))
        current = self.state.name
        assert current in Session.STATE_TRANSITION_MAP
        authorizeds = Session.STATE_TRANSITION_MAP[current]
        if role.name in authorizeds:
            self.state = role
            return True

    def setStoragePrefix(self, p):
        """Define the prefix to use for key-value store

        This allow to separate each command storage by namespace in the session
        @param p [str] : the prefix for key-value store
        """
        self.__prefix = p

    def get(self, key):
        """Retrieve the selected value from storage

        @param key [str] the name of the value to retrieve
        @return
        """
        fullkey = self.__prefix + key
        if fullkey in self.__storage:
            return self.__storage[fullkey]

    def set(self, key, value):
        """Set the given value in session storage

        @param key [str] the name of the key where to put the value
        @param value [str] the value to put into this place
        """
        fullkey = self.__prefix + key
        self.__storage[fullkey] = value
        return self

    def getSecureSession(self):
        """Return a secure wrapper of the session
        """
        class SessionWrapper(object):
            def __init__(self, session):
                self.__session = session
                self.subject = session.subject
                self.state = session.state

            def get(self, *args, **kw):
                return self.__session.get(*args, **kw)

            def set(self, *args, **kw):
                return self.__session.set(*args, **kw)

            def toRole(self, *args, **kw):
                return self.__session.toRole(*args, **kw)

        return SessionWrapper(self)

    # DEBUG methods
    def __str__(self):
        """[DEBUG] Produce a description string for this session

        @return [str] a formatted string
        """
        content = ("Session for(" + str(self.subject) + ")" +
                   "\n  Started At = " + str(self.created_at) +
                   "\n  Valid for = " + str(self.ttl) + " seconds")
        return content

    def __repr__(self):
        """[DEBUG] Produce a list of attribute as string

        @return [str] a formatted string that describe this object
        """
        return ("[S(" + str(self.subject) + ")]")
