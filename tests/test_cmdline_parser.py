# -*- coding: utf8 -*-

import json
import os
import shlex
import subprocess


# command line test
def test_cmdline_help():
    """Must produce an error is no url was given"""
    result = subprocess.Popen(shlex.split('./bin/sms-shell-parser --help'), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert 'usage:' in stdout.decode()

def test_cmdline_version():
    result = subprocess.Popen(shlex.split('./bin/sms-shell-parser --version'), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert 'SMSShell parser version' in stdout.decode()

def test_cmdline_with_env_input():
    env = dict(
        SMS_MESSAGES="1",
        DECODED_PARTS="0",
        SMS_1_NUMBER="0124",
        SMS_1_CLASS="-1",
        SMS_1_TEXT="ghgg",
    )
    # Load env
    for key in env:
        os.environ[key] = env[key]

    result = subprocess.Popen(shlex.split('./bin/sms-shell-parser --input env'), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    if isinstance(stdout, bytes):
        stdout = stdout.decode()
    obj = json.loads(stdout)
    assert result.returncode == 0
    assert 'sms_number' in obj and obj['sms_number'] == '0124'
