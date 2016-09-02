# -*- coding: utf8 -*-

# This file is a part of SMSShell
#
# Copyright (c) 2016 Pierre GINDRAUD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Models/Session This class represent an user session

"""

# System imports
import datetime
import logging

# Global project declarations
g_logger = logging.getLogger('smsshell.models.session')


class Session(object):
  """An user session with all user's meta data
  """

  SESS_GUEST = 0
  SESS_LOGIN = 1
  SESS_AUTHENTICATED = 2
  SESS_LOGOUT = 4

  def __init__(self, subject, timetolive=600):
    """Constructor: Build a new session for the given subject

    @param sender [str] : session subject
    @param timetolive [int] OPTIONNAL : the number of second the session will be
              alive
    """
    self.subject = subject
    self.__created_at = datetime.datetime.today()
    self._access()
    self.ttl = timetolive
    self.state = Session.SESS_GUEST
    self.__prefix = None
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

  def _access(self):
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

  def _setPrefix(self, p):
    """Define the prefix to use for key-value store

    This allow to separate each command storage by namespace in the session
    @param p [str] : the prefix for key-value store
    """
    self.__prefix = p

  def get(self, key):
    fullkey = self.__prefix + key
    if fullkey in self.__storage:
      return self.__storage[fullkey]

  def set(self, key, value):
    """Set the given value in session storage

    @param key [str] the name of the key where to put the value
    @param
    """
    fullkey = self.__prefix + key
    self.__storage[fullkey] = value


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
