#!/usr/bin/python3

import os
import subprocess
import sys

iteration = 1
if '-c' not in sys.argv:
    if len(sys.argv) > 1:
        text = ' '.join(sys.argv[1:])
    else:
        text = input()
else:
    iteration = 9999

while iteration > 0:
    if '-c' in sys.argv:
        text = input()

    env = dict(
        SMS_MESSAGES="1",
        DECODED_PARTS="0",
        SMS_1_NUMBER="0124",
        SMS_1_CLASS="-1",
        SMS_1_TEXT=text,
    )

    print('Send "' + text + '"')
    for key in env:
        os.environ[key] = env[key]

    subprocess.check_output(['../utils/sms-shell-parser.py', '--output=../fifo'])
    iteration -= 1
