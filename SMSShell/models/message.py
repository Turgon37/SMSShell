# -*- coding: utf8 -*-

# This file is a part of SMSShell
#
# Copyright (c) 2016-2017 Pierre GINDRAUD
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

"""Models/Message This class represent a incoming message in shell

Each message have a sender reference used to keep session consistency and a
content that will be analysed
"""


class Message(object):
  """A simple message with sender id
  """

  def __init__(self, sender, content):
    """Constructor: Build a new message object

    @param sender [str] : sender unique identifier
    @param content [str] : message content
    """
    self.__sender = None
    self.__content = None
    # database model
    self.sender = sender
    self.content = content

  @property
  def sender(self):
    """Return the sender id

    @return [str] the sender id
    """
    assert self.__sender is not None
    return self.__sender

  @sender.setter
  def sender(self, s):
    """Set the sender id

    @param s [str] : the sender id
    """
    self.__sender = s

  @property
  def content(self):
    """Return the content payload

    @return [str] the content
    """
    assert self.__content is not None
    return self.__content

  @content.setter
  def content(self, c):
    """Set the message content

    @param c [str] : the content
    """
    self.__content = c

  def getArgv(self):
    """Return the command argument vector associated with this message

    @return list of command argments
    """
    assert isinstance(self.content,str)
    return self.content.split(' ')


# DEBUG methods
  def __str__(self):
    """[DEBUG] Produce a description string for this message

    @return [str] a formatted string
    """
    content = ("Message from(" + str(self.sender) + ")" +
               "\n  CONTENT = " + str(self.content))
    return content

  def __repr__(self):
    """[DEBUG] Produce a list of attribute as string

    @return [str] a formatted string that describe this object
    """
    return ("[M(" + str(self.sender) + ")]")
