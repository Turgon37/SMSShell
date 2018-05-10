# -*- coding: utf8 -*-

import shlex
import subprocess


# command line test
def test_cmdline_help():
    """Must produce an error is no url was given"""
    result = subprocess.Popen(shlex.split('./utils/sms-shell-client --help'), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert 'usage:' in stdout.decode()

def test_cmdline_version():
    result = subprocess.Popen(shlex.split('./utils/sms-shell-client --version'), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert 'SMSShell client version' in stdout.decode()

def test_cmdline_without_config_file():
    result = subprocess.Popen(shlex.split('./utils/sms-shell-client'), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert result.returncode == 0
