# -*- coding: utf8 -*-

import configparser
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
    smsdrc = configparser.ConfigParser()
    smsdrc['gammu'] = dict(Device='/dev/null')
    smsdrc['smsd'] = dict(Service='FILES')
    with open('tests/smsdrc', 'w') as w:
        smsdrc.write(w)
    config = dict(umask='9', smsdrc_configuration=os.path.join(os.getcwd(), 'tests/smsdrc'))
    transmitter = SMSShell.transmitters.python_gammu.Transmitter(config=config)
    transmitter.start()
    message = SMSShell.models.Message('local', 'OK')
    transmitter.transmit(message)
    transmitter.stop()
    #os.unlink('tests/smsdrc')
