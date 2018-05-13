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

"""Some parsing utilities to decode GammuSMSD messages
"""

import os

# These environnement variables are available
#  Global variables
#    SMS_MESSAGES      Number of physical messages received.
#    DECODED_PARTS     Number of decoded message parts.
#
#  Per message variables
#    The variables further described as SMS_1_...  are  generated  for  each
#    physical message, where 1 is replaced by current number of message.
#
#    SMS_1_CLASS       Class of message.
#    SMS_1_NUMBER      Sender number.
#    SMS_1_TEXT        Message text. Text is not available for 8-bit binary messages.
#
#  Per part variables
#    The variables further described as DECODED_1_... are generated for each
#    message part, where 1 is replaced by current number of  part.  Set  are
#    only those variables whose content is present in the message.
#
#    DECODED_1_TEXT          Decoded long message text.
#    DECODED_1_MMS_SENDER    Sender of MMS indication message.
#    DECODED_1_MMS_TITLE     Title of MMS indication message.
#    DECODED_1_MMS_ADDRESS   Address (URL) of MMS from MMS indication message.
#    DECODED_1_MMS_SIZE      Size of MMS as specified in MMS indication message.


class GammuSMSParser(object):

    @staticmethod
    def createEmptyMessage():
        # template of output string
        return dict(
            sms_text='',
            sms_class=None,
            sms_number=None,
            errors=[],
        )

    @staticmethod
    def setUniqueValueInSMS(sms, key, value):
        """Set a value with unique constraint into SMS object
        """
        if (sms[key] is None):
            sms[key] = value
        else:
            # if the class if already set, compare it with the previous value
            if (sms[key] != value):
                sms['errors'].append('Two or more differents values for {0}'.format(key))

    @staticmethod
    def decodeFromEnv():
        """Extract SMS content from the current environment
        """
        sms = GammuSMSParser.createEmptyMessage()
        # Decode SMS messages
        sms_parts = int(os.getenv('SMS_MESSAGES', 0))
        sms_text = ''
        if sms_parts > 0:
            for i in range(1, sms_parts + 1):
                sms_text += os.getenv('SMS_{}_TEXT'.format(i), '')

                # fill sms class
                sms_class = os.getenv('SMS_{}_CLASS'.format(i), None)
                if sms_class:
                    GammuSMSParser.setUniqueValueInSMS(sms, 'sms_class', sms_class)

                # fill SMS NUMBER
                sms_number = os.getenv('SMS_{}_NUMBER'.format(i), None)
                if sms_number:
                    GammuSMSParser.setUniqueValueInSMS(sms, 'sms_number', sms_number)

        # Decode SMS parts
        decoded_parts = int(os.getenv('DECODED_PARTS', 0))
        decoded_text = ''
        if decoded_parts > 0:
            for i in range(0, decoded_parts):
                decoded_text += os.getenv("DECODED_{0}_TEXT".format(i), '')

        if sms_parts == 0 and decoded_parts == 0:
            sms['errors'].append('no message content')

        if decoded_parts > 0:
            sms['sms_text'] = decoded_text
            if decoded_text != sms_text:
                sms['errors'].append('SMS text differ from decoded part, keeping decoded part')
        else:
            sms['sms_text'] = sms_text
        return sms
