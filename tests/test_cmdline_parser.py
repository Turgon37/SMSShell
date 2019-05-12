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

    result = subprocess.Popen(shlex.split('./bin/sms-shell-parser --input env --output tests/test_out'), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert os.path.exists('tests/test_out')
    os.unlink('tests/test_out')

def test_cmdline_with_bad_file_input():
    result = subprocess.Popen(shlex.split('./bin/sms-shell-parser --input file'),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert result.returncode != 0

def test_cmdline_with_file_input():
    result = subprocess.Popen(shlex.split('./bin/sms-shell-parser --input file -ia tests/samples/IN20190512_222525_00.txt'), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    if isinstance(stdout, bytes):
        stdout = stdout.decode()
    obj = json.loads(stdout)
    assert result.returncode == 0
    assert 'sms_number' in obj and obj['sms_number'] == '+3365'
