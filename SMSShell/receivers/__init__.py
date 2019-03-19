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

"""This module contains abstract class for receivers
"""

# System import
import time

# Project imports
from ..abstract import AbstractModule


class AbstractReceiver(AbstractModule):
    """An abstract receiver
    Any valid receiver implementation must inherit this one
    """

    def start(self):
        """Prepare the receiver/init connections

        Returns:
            True if init has success, otherwise False
        """
        raise NotImplementedError("You must implement the 'start' method in receiver class")

    def stop(self):
        """Close properly the receiver, flush, close connections

        Returns:
            True if stop has success, otherwise False
        """
        raise NotImplementedError("You must implement the 'stop' method in receiver class")

    def read(self):
        """Return a read blocking iterable object for each content in the receiver

        Returns:
            Iterable
        """
        raise NotImplementedError("You must implement the 'read' method in receiver class")


class AbstractClientRequest(object):
    """This class is a wrapper to client request handling

    Any received must define class thaht inherit this one with enter and exit
    method implemented.
    This class use context to ensure that client request will always receive
    an answer
    """

    def __init__(self, request_data):
        """
        """
        # this it the treatment chain
        # one state is associated with the corresponding timestamp
        self.__treatment_chain = []
        self.__response_data = dict()
        self.__request_data = request_data
        self.__is_in_context = False

    #
    # PUBLIC METHODS
    #

    def appendTreatmentChain(self, state_name):
        """Append a state to the treatment chain

        This chain can be used to get a timeline of the request treatment to
        client
        """
        self.__treatment_chain.append((state_name, time.time()))

    def getTreatmentChain(self):
        return self.__treatment_chain

    def addResponseData(self, **kwargs):
        """Append data to optional answer
        """
        self.__response_data.update(**kwargs)

    def popResponseData(self):
        """
        """
        final = self.__response_data
        self.__response_data = dict()
        return final

    def getRequestData(self):
        """Return the initial client request data

        Only available in client contexte to ensure a proper answer to client
        """
        if not self.__is_in_context:
            raise RuntimeError("You cannot access client request's datas " +
                               "outside of the client request context.")
        return self.__request_data

    def enter(self):
        """This function is called when code entering client request context

        Put here, any initialization in response data or metrics
        """
        raise NotImplementedError("You must implement the 'enter' method in client request class")

    def exit(self):
        """This function is called when code leaving client request context

        Put here, any answer write procedure, or client buffer flush
        """
        raise NotImplementedError("You must implement the 'exit' method in client request class")

    #
    # PRIVATE PROPERTIES
    #

    def __enter__(self):
        self.__is_in_context = True
        self.enter()

    def __exit__(self, type, value, traceback):
        self.__is_in_context = False
        self.exit()
