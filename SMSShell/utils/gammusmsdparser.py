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


class GammuSMSParser():
    """This class contains some utility to decode SMS from gammusmsd
    """

    # Mapping between SMSBackup format value and final values
    BACKUPFILE_SMS_TYPE_MAPPING = dict({
        'Deliver': 'message',
        'Submit': 'message',
        'Status_Report': 'status_report',
    })
    BACKUPFILE_SMS_FIELD_MAPPING = dict({
        'Class': 'sms_class',
        'Number': 'sms_number',
    })

    ERROR_DUPLICATE_VALUE = 'DUPLICATE_VALUE'
    ERROR_NO_CONTENT = 'NO_CONTENT'
    ERROR_INCONSISTENCY = 'INCONSISTENCY'
    ERROR_BACKUP_FILE = 'BACKUP_FILE'
    ERROR_PYTHON = 'PYTHON'
    ERROR_IMPLEMENTATION = 'IMPLEMENTATION'

    @staticmethod
    def create_empty_message():
        """Return an empty message template
        """
        # template of output string
        return dict(
            type=None,
            timestamp=None,
            sms_text=None,
            sms_class=None,
            sms_number=None,
            sms_type=None, # in 'message', 'delivery_report'
            mms_address=None,
            mms_title=None,
            mms_number=None,
            errors=[],
        )

    @staticmethod
    def append_error(message, error_type, error_message: str):
        """Append error messages to the given sms message

        Args:
            message : the sms message
            error_type : the type of error
            error_message : the error string
        """
        message['errors'].append((error_type, error_message))

    @staticmethod
    def set_unique_value_in_message(message, key, value):
        """Set a value with unique constraint into SMS object
        """
        if message[key] is None:
            message[key] = value
        else:
            # if the class if already set, compare it with the previous value
            if message[key] != value:
                GammuSMSParser.append_error(message,
                                            GammuSMSParser.ERROR_DUPLICATE_VALUE,
                                            'Two or more differents values for {0}'.format(key))

    @classmethod
    def decode_from_env(cls):
        """Extract SMS content from the current environment
        """
        message = cls.create_empty_message()
        # Decode SMS messages
        sms_parts = int(os.getenv('SMS_MESSAGES', '0'))
        sms_text = ''
        if sms_parts > 0:
            message['type'] = 'SMS'
            for i in range(1, sms_parts + 1):
                sms_text += os.getenv('SMS_{}_TEXT'.format(i), '')

                # fill sms class
                sms_class = os.getenv('SMS_{}_CLASS'.format(i), None)
                if sms_class:
                    cls.set_unique_value_in_message(message, 'sms_class', sms_class)

                # fill SMS NUMBER
                sms_number = os.getenv('SMS_{}_NUMBER'.format(i), None)
                if sms_number:
                    cls.set_unique_value_in_message(message, 'sms_number', sms_number)

        # Decoded SMS parts
        decoded_parts = int(os.getenv('DECODED_PARTS', '0'))
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
                        GammuSMSParser.set_unique_value_in_message(message,
                                                                   'mms_number',
                                                                   sender_parts[0])
                    message['mms_title'] = os.getenv("DECODED_{0}_MMS_TITLE".format(i+1), '')
                    message['mms_address'] = os.getenv("DECODED_{0}_MMS_ADDRESS".format(i+1), '')

        if sms_parts == 0 and decoded_parts == 0:
            cls.append_error(message, cls.ERROR_NO_CONTENT, 'no message content')

        if decoded_parts > 0:
            message['sms_text'] = decoded_text
            if decoded_text != sms_text:
                cls.append_error(message,
                                 cls.ERROR_INCONSISTENCY,
                                 'SMS text differ from decoded part, keeping decoded part')
        else:
            message['sms_text'] = sms_text
        return message

    @classmethod
    def decode_from_backup_file_path(cls, backup_file_path):
        # pylint: disable=R0914,R0912,R1702
        """Extract gammu message from a backup file

        Args:
            backup_file_path : the path to the backup file
        """
        message = cls.create_empty_message()

        # checks
        if not os.path.exists(backup_file_path) or not os.path.isfile(backup_file_path):
            cls.append_error(message,
                             cls.ERROR_BACKUP_FILE,
                             "the file '{}' do not exists".format(backup_file_path))
            return message
        if not os.access(backup_file_path, os.R_OK):
            cls.append_error(message,
                             cls.ERROR_BACKUP_FILE,
                             "the file '{}' is not readable".format(backup_file_path))
            return message
        if not gammu:
            cls.append_error(message,
                             cls.ERROR_PYTHON,
                             'the gammu package is not available to decode backup format')
            return message

        backup = gammu.ReadSMSBackup(backup_file_path)

        # Make nested array
        backup_messages = [[backup_message] for backup_message in backup]
        raw_messages = gammu.LinkSMS(backup_messages)

        if not raw_messages:
            cls.append_error(message,
                             cls.ERROR_NO_CONTENT,
                             'the backup file do not contains any message')
            return message

        if len(raw_messages) > 1:
            cls.append_error(message,
                             cls.ERROR_IMPLEMENTATION,
                             'the backup file contains more than one message')

        for raw_message in raw_messages:
            decoded_message = gammu.DecodeSMS(raw_message)
            part = raw_message[0]

            # extract meta datas
            for backup_key, message_key in cls.BACKUPFILE_SMS_FIELD_MAPPING.items():
                if backup_key in part and part[backup_key]:
                    cls.set_unique_value_in_message(message, message_key, part[backup_key])

            if 'Type' in part and part['Type'] in cls.BACKUPFILE_SMS_TYPE_MAPPING:
                cls.set_unique_value_in_message(message,
                                                'sms_type',
                                                cls.BACKUPFILE_SMS_TYPE_MAPPING[part['Type']])

            if 'DateTime' in part and isinstance(part['DateTime'], datetime.datetime):
                message['timestamp'] = time.mktime(part['DateTime'].timetuple())

            # extract message body
            if decoded_message is None:
                # exploit the SMS Object
                # https://wammu.eu/docs/manual/python/objects.html#sms-obj
                message['sms_text'] = part['Text']
                message['type'] = 'SMS'
            else:
                # exploit the multipart object
                # https://wammu.eu/docs/manual/python/objects.html#sms-info-obj
                for entry in decoded_message['Entries']:
                    # Use ID to exploit the entry
                    if 'ID' in entry and entry['ID']:
                        entry_id = entry['ID']
                        # if we see this we can consider that message is a MMS
                        if entry_id in ['MMSIndicatorLong']:
                            if not message['type']:
                                message['type'] = 'MMS'
                        # any of theses ID can be considered as SMS message
                        elif entry_id in ['Text',
                                          'ConcatenatedTextLong',
                                          'ConcatenatedAutoTextLong',
                                          'ConcatenatedTextLong16bit',
                                          'ConcatenatedAutoTextLong16bit']:
                            if not message['type']:
                                message['type'] = 'SMS'

                    # String to encode in message.
                    if entry['Buffer']:
                        message['sms_text'] = (message['sms_text'] or '') + entry['Buffer']
                    # MMS indication to encode in message.
                    if entry['MMSIndicator']:
                        mms_infos = entry['MMSIndicator']
                        message['mms_address'] = mms_infos['Address'] or ''
                        message['mms_title'] = mms_infos['Title'] or ''
                        # extract pure number part
                        sender_parts = (mms_infos['Sender'] or '').split('/')
                        if len(sender_parts) > 1:
                            message['mms_number'] = sender_parts[0]

            # prevent another message to be parsed
            break

        return message
