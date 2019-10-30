# -*- coding: utf8 -*-

import configparser
import pytest
import os

import SMSShell


def test_loading():
    """Test base transmitter class exception with init
    """
    program = SMSShell.SMSShell()
    status, msg = program.load('./tests/config.conf')
    assert status

def test_loading_without_config():
    """Test base transmitter class exception with init
    """
    program = SMSShell.SMSShell()
    status, msg = program.load(None)

    assert not status

def test_start_standalone_mode():
    """
    """
    writer = configparser.ConfigParser()
    writer['main'] = dict()
    writer['main']['mode'] = 'STANDALONE'

    with open('start.ini', 'w') as configfile:
        writer.write(configfile)

    program = SMSShell.SMSShell()
    status, msg = program.load('start.ini')
    assert status
    os.unlink('start.ini')

    with pytest.raises(NotImplementedError):
        program.start('./pid.pid')
