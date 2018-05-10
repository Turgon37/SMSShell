#!/usr/bin/env python3

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

"""SMSShell Gammu SMS Parser

This file is able to parse an sms received by gammu-smsd tool and to format it into JSON.
"""

__author__ = 'Pierre GINDRAUD'
__license__ = 'GPL-3.0'
__version__ = '1.0.0'
__maintainer__ = 'Pierre GINDRAUD'
__email__ = 'pgindraud@gmail.com'

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

# System imports
import argparse
import json
import os
import sys

# Check python version
assert sys.version_info >= (3,4)

# template of output string
sms = dict(
  smstext='',
  smsclass=None,
  smsnumber=None,
  mmstext='',
  error=None,
  errors=[],
)

def setUniqueValue(key, value):
  """Set a value with unique constraint into SMS object
  """
  if (sms[key] is None):
    sms[key] = value
  else:
    # if the class if already set, compare it with the previous value
    if (sms[key] != value):
      errors.append('Two or more differents values for {0}'.format(key))

def decodeEnv():
  # Decode SMS messages
  smsparts = int(os.getenv('SMS_MESSAGES', 0))
  if smsparts > 0:
    for i in range(1, smsparts + 1):
      sms['smstext'] += os.getenv("SMS_{0}_TEXT".format(i), "")
      # fill sms class
      smsclass = os.getenv("SMS_{0}_CLASS".format(i), None)
      setUniqueValue('smsclass', smsclass)

      # fill SMS NUMBER
      smsnumber = os.getenv("SMS_{0}_NUMBER".format(i), None)
      setUniqueValue('smsnumber', smsnumber)

  # Decode SMS parts
  decodedparts = int(os.getenv('DECODED_PARTS', 0))
  if decodedparts > 0:
    for i in range(1, decodedparts + 1):
      sms['mmstext'] += os.getenv("DECODED_{0}_TEXT".format(i-1), "")

  if smsparts == 0 and decodedparts == 0:
    sms['error'] = 'no message content'
  return sms


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SMSShell client version v" + __version__,
                                        argument_default=argparse.SUPPRESS,
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-o', '--output', action='store', dest='output', default=None,
                            help='Path to the file ')
    parser.add_argument('-v', '--version', action='store_true', dest='show_version',
                            help='Print the version and exit')
    args = parser.parse_args()

    if hasattr(args, 'show_version') and args.show_version:
        print('SMSShell parser version v{}'.format(__version__))
        sys.exit(0)

    if args.output:
        with open(args.output, 'w') as output:
            json.dump(decodeEnv(), output)
    else:
        json.dump(decodeEnv(), sys.stdout)

    sys.exit(0)
