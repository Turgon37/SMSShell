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

# Project imports
from ..exceptions import ShellException

# Global project declarations
g_logger = logging.getLogger('smsshell.models.session')

class SessionException(ShellException):
    """Base class for all exceptions relating to command execution
    """
    def __init__(self, message, short='internal session error'):
        super().__init__(message, short)


class BadStateTransitionException(SessionException):
    """Raise when someone try to follow a state transition that is not allowed
    """
    pass


@unique
class SessionStates(IntEnum):
    """This enumeration reprensent the list of available roles
    """
    STATE_GUEST = 0
    STATE_LOGININPROGRESS = 1
    STATE_USER = 2


class Session(object):
    """An user session with all user's meta data
    """

    # map of authorized session states transitions
    STATE_TRANSITION_MAP = {
        'STATE_GUEST': [
            'STATE_LOGININPROGRESS',
            'STATE_USER',
        ],
        'STATE_LOGININPROGRESS': [
            'STATE_USER',
            'STATE_GUEST',
        ],
        'STATE_USER': [
            'STATE_GUEST',
        ]
    }

    def __init__(self, subject, time_to_live=600):
        """Constructor: Build a new session for the given subject

        Args:
            subject: the session subject
                        this value is used to identify the owner of the session
            time_to_live: integer OPTIONNAL
                        the number of second the session will be alive
                        Once this time is elapsed, this session is destroyed
                        and a new empty one is created
        """
        # internal attributes
        self.__subject = None
        self.__ttl = None
        self.__prefix = ''
        self.__state = None
        self.__created_at = datetime.datetime.today()
        self.__storage = dict()

        # init attributes with values
        self.subject = subject
        self.ttl = time_to_live
        self.forceState(SessionStates.STATE_GUEST)
        self.access()


    @property
    def subject(self):
        """Return the subject name

        Returns:
            the subject as a string
        """
        assert self.__subject is not None
        return self.__subject

    @subject.setter
    def subject(self, sub):
        """Set the subject id

        Args:
            sub: the new subject as a string
        """
        self.__subject = sub

    @property
    def state(self):
        """Return the current state of this session

        Returns:
            the current state value
        """
        assert self.__state is not None
        return self.__state

    @state.setter
    def state(self, new_state):
        """Perform a transition from current state to the given state

        Args:
            new_state: the targeted new state
        """
        if not isinstance(new_state, SessionStates):
            raise BadStateTransitionException("The given new state " +
                                              "'{}' is not valid".format(str(new_state)))
        current = self.state.name
        assert current in Session.STATE_TRANSITION_MAP

        allowed = Session.STATE_TRANSITION_MAP[current]
        if new_state.name not in allowed:
            raise BadStateTransitionException("You are not allowed to switch from state " +
                                              "'{}' to state '{}'".format(current, new_state.name))

        self.__state = new_state

    def forceState(self, new_state):
        """
        """
        if not isinstance(new_state, SessionStates):
            raise BadStateTransitionException("The given new state " +
                                              "'{}' is not valid".format(str(new_state)))
        self.__state = new_state

    @property
    def created_at(self):
        """Return the created at datetime

        Returns:
            return the datetime at which this session has been created
        """
        return self.__created_at

    @property
    def ttl(self):
        """Return the current time to live

        Returns:
            the current session time to live
        """
        assert self.__ttl is not None
        return int(self.__ttl.seconds)

    @ttl.setter
    def ttl(self, seconds):
        """Set the time to live in seconds

        Args:
            seconds: the number of minutes the session will be alive
        """
        self.__ttl = datetime.timedelta(seconds=int(seconds))

    @property
    def access_at(self):
        """Return the last access time

        Returns:
            the last time this session has been used
        """
        assert self.__access_at is not None
        return self.__access_at

    def access(self):
        """Refresh the access time of this session

        Returns:
            self
        """
        self.__access_at = datetime.datetime.today()
        return self

    def isValid(self):
        """Check if this session is valid

        Returns:
            true if the session is still valid, false otherwise
        """
        if (datetime.datetime.today() - self.access_at).seconds >= self.ttl:
            g_logger.debug('session for %s is expired', self.subject)
            return False
        return True

    def setStoragePrefix(self, prefix):
        """Define the prefix to use for key-value store

        This allow to separate each command storage by namespace in the session
        Args:
            prefix: the prefix for key-value store as a string
        """
        self.__prefix = prefix

    def get(self, key, fallback=None):
        """Retrieve the selected value from storage

        Args:
            key: the name of the value you want
            fallback: optional fallback value if key do not exists in session
                        storage
        Returns:
            mixed: the requested value or fallback if it do not exits
        """
        fullkey = self.__prefix + key
        if fullkey in self.__storage:
            return self.__storage[fullkey]
        return fallback

    def set(self, key, value):
        """Set the given value in session storage

        Args:
            key: the name of the key where to put the value
            value: the value to put into this place
        Returns:
            self
        """
        fullkey = self.__prefix + key
        self.__storage[fullkey] = value
        return self

    def getSecureSession(self):
        """Return a secure wrapper of the session

        Returns:
            a new session wrapper for this session
        """

        class SessionWrapper(object):
            """Simple session wrapper to restrict usage of some
            attribute into commands
            """
            def __init__(self, session):
                """Build a new wrapper around this session

                Args:
                    session: the real wrapper session object
                """
                self.__session = session
                self.subject = session.subject
                self.state = session.state

            def get(self, *args, **kw):
                """See Session.get
                """
                return self.__session.get(*args, **kw)

            def set(self, *args, **kw):
                """See Session.set
                """
                return self.__session.set(*args, **kw)

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
        return "[S(" + str(self.subject) + ")]"
