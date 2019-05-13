# -*- coding: utf8 -*-

import pytest
import os

import SMSShell
import SMSShell.transmitters.python_gammu


def test_init():
    transmitter = SMSShell.transmitters.python_gammu.Transmitter()

def test_without_gammurc():
    transmitter = SMSShell.transmitters.python_gammu.Transmitter()
    assert not transmitter.start()

def test_without_bad_configuration():
    config = dict(umask='9')
    transmitter = SMSShell.transmitters.python_gammu.Transmitter(config=config)
    assert not transmitter.start()

def test_without_read_right():
    config = dict(umask='9', smsdrc_configuration='/root')
    transmitter = SMSShell.transmitters.python_gammu.Transmitter(config=config)
    assert not transmitter.start()

def test_simple_transmit():
    """Test base parser class exception
    """
    with open('tests/smsdrc', 'w') as w:
        pass
    config = dict(umask='9', smsdrc_configuration='tests/smsdrc')
    transmitter = SMSShell.transmitters.python_gammu.Transmitter(config=config)
    message = SMSShell.models.Message('local', 'OK')
    transmitter.transmit(message)
    os.unlink('tests/smsdrc')
