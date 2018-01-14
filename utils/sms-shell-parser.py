#!/usr/bin/python3

# This file is a part of SMSShell
#
# Copyright (c) 2016-2018 Pierre GINDRAUD
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

"""SMSShell Gammu SMS Parser

This file is able to parse an sms received by gammu-smsd tool and format it into JSON.
"""


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
import getopt
import json
import os
import sys

version = "1.0.0"

# template of output string
sms = dict(
  smstext="",
  smsclass=None,
  smsnumber=None,
  mmstext="",
  error=None,
  errors=[],
  )

def showVersion():
  """Print the program version
  """
  print("SMS Parser version v" + version)


def showUsage():
  """Prints command line options
  """
  print('Usage: ' + sys.argv[0] + ' [OPTIONS...]')
  showVersion()
  print("""
This tool is part os SMSShell project

Options :
  -o, --output PATH   specify the path of the output destination (default stdout)
  -h, --help          display this help message
  -V, --version       print the version

Return code :
  0 Success
  1 Error with output stream
  2 Option not recognized
""")

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
  try:
    given_options_list, args = getopt.getopt(sys.argv[1:], 'hVp:', ['help', 'version', 'output='])
  except getopt.GetoptError as e:
    sys.stderr.write(str(e))
    showUsage()
    sys.exit(2)
  # prepare default settings
  out = sys.stdout
  for opt in given_options_list:
    if opt[0] in ['-h', '--help']:
      showUsage()
      sys.exit(0)
    if opt[0] in ['-V', '--version']:
      showVersion()
      sys.exit(0)
    if opt[0] in ['-o', '--output']:
      try:
        out = open(opt[1], "w")
      except OSError as e:
        sys.stderr.write(str(e))
        sys.exit(1)

  json.dump(decodeEnv(), out)
