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

import datetime
import os
import time

try:
    import gammu
except ImportError:
    gammu = None

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
    """This class contains some utility to decode SMS from gammusmsd
    """

    # Mapping between SMSBackup format value and final values
    BACKUPFILE_SMS_TYPE_MAPPING = dict({
        'Deliver': 'message',
        'Submit': 'message',
        'Status_Report': 'delivery_report',
    })
    BACKUPFILE_SMS_FIELD_MAPPING = dict({
        'Class': 'sms_class',
        'Number': 'sms_number',
    })

    @staticmethod
    def createEmptyMessage():
        # template of output string
        return dict(
            type=None,
            timestamp=None,
            sms_text='',
            sms_class=None,
            sms_number=None,
            sms_type=None, # in 'message', 'delivery_report'
            mms_address='',
            mms_title='',
            mms_number=None,
            errors=[],
        )

    @staticmethod
    def setUniqueValueInMessage(message, key, value):
        """Set a value with unique constraint into SMS object
        """
        if (message[key] is None):
            message[key] = value
        else:
            # if the class if already set, compare it with the previous value
            if (message[key] != value):
                message['errors'].append('Two or more differents values for {0}'.format(key))

    @classmethod
    def decodeFromEnv(cls):
        """Extract SMS content from the current environment
        """
        message = cls.createEmptyMessage()
        # Decode SMS messages
        sms_parts = int(os.getenv('SMS_MESSAGES', 0))
        sms_text = ''
        if sms_parts > 0:
            message['type'] = 'SMS'
            for i in range(1, sms_parts + 1):
                sms_text += os.getenv('SMS_{}_TEXT'.format(i), '')

                # fill sms class
                sms_class = os.getenv('SMS_{}_CLASS'.format(i), None)
                if sms_class:
                    cls.setUniqueValueInMessage(message, 'sms_class', sms_class)

                # fill SMS NUMBER
                sms_number = os.getenv('SMS_{}_NUMBER'.format(i), None)
                if sms_number:
                    cls.setUniqueValueInMessage(message, 'sms_number', sms_number)

        # Decoded SMS parts
        decoded_parts = int(os.getenv('DECODED_PARTS', 0))
        decoded_text = ''
        if decoded_parts > 0:
            for i in range(0, decoded_parts):
                decoded_text += os.getenv("DECODED_{0}_TEXT".format(i), '')

                # MMS
                sender = os.getenv("DECODED_{0}_MMS_SENDER".format(i+1), None)
                if sender:
                    message['type'] = 'MMS'
                    sender_parts = sender.split('/')
                    if len(sender_parts) > 1:
                        GammuSMSParser.setUniqueValueInMessage(message, 'mms_number', sender_parts[0])
                    message['mms_title'] = os.getenv("DECODED_{0}_MMS_TITLE".format(i+1), '')
                    message['mms_address'] = os.getenv("DECODED_{0}_MMS_ADDRESS".format(i+1), '')

        if sms_parts == 0 and decoded_parts == 0:
            message['errors'].append('no message content')

        if decoded_parts > 0:
            message['sms_text'] = decoded_text
            if decoded_text != sms_text:
                message['errors'].append('SMS text differ from decoded part, keeping decoded part')
        else:
            message['sms_text'] = sms_text
        return message

    @classmethod
    def decodeFromBackupFilePath(cls, path):
        """
        """
        message = cls.createEmptyMessage()

        # checks
        if not os.path.exists(path) or not os.path.isfile(path):
            message['errors'].append("the file '{}' do not exists".format(path))
            return message
        if not os.access(path, os.R_OK):
            message['errors'].append("the file '{}' is not readable".format(path))
            return message
        if not gammu:
            message['errors'].append('the gammu package is not available to decode backup format')
            return message

        raw_message = gammu.ReadSMSBackup(path)
        text = ''
        for raw_part in raw_message:
            # simple mapped fields
            for backup_key, message_key in cls.BACKUPFILE_SMS_FIELD_MAPPING.items():
                if backup_key in raw_part and raw_part[backup_key]:
                    cls.setUniqueValueInMessage(message, message_key, raw_part[backup_key])

            if 'Type' in raw_part and raw_part['Type'] in cls.BACKUPFILE_SMS_TYPE_MAPPING:
                   cls.setUniqueValueInMessage(message, 'sms_type', cls.BACKUPFILE_SMS_TYPE_MAPPING[raw_part['Type']])

            if 'Text' in raw_part and raw_part['Text']:
                text += raw_part['Text']

            if 'DateTime' in raw_part and isinstance(raw_part['DateTime'], datetime.datetime):
                message['timestamp'] = time.mktime(raw_part['DateTime'].timetuple())

        message['sms_text'] = text
        message['type'] = 'SMS'
        return message
