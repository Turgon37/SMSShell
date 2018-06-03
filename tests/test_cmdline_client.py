# -*- coding: utf8 -*-

import os
import shlex
import subprocess


# command line test
def test_cmdline_help():
    """Must produce an error is no url was given"""
    result = subprocess.Popen(shlex.split('./bin/sms-shell-client --help'), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert 'usage:' in stdout.decode()

def test_cmdline_version():
    result = subprocess.Popen(shlex.split('./bin/sms-shell-client --version'), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert 'SMSShell client version' in stdout.decode()

def test_cmdline_without_arguments():
    result = subprocess.Popen(shlex.split('./bin/sms-shell-client'), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert result.returncode == 1

def test_cmdline_write_fifo():
    """Test to write to a fifo
    """
    fifo = './fifo'
    result = subprocess.Popen(shlex.split('./bin/sms-shell-client -i env -o fifo -oa {}'.format(fifo)), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert result.returncode == 0
    # without daemon running, this is a simple file
    assert os.path.isfile(fifo)

def test_cmdline_write_unix():
    """Test to write to an unix socket
    """
    unix = './unix'
    result = subprocess.Popen(shlex.split('./bin/sms-shell-client -i env -o unix -oa {}'.format(unix)), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert result.returncode == 1
