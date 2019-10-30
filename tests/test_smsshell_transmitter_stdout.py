# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.transmitters.stdout


def test_init():
    transmitter = SMSShell.transmitters.stdout.Transmitter()
    assert transmitter.start()
    assert transmitter.stop()

def test_simple_transmit(capsys):
    """Test base parser class exception
    """
    transmitter = SMSShell.transmitters.stdout.Transmitter()
    transmitter.start()
    message = SMSShell.models.Message('local', 'OK')
    transmitter.transmit(message)
    transmitter.stop()
    out, err = capsys.readouterr()
    assert 'OK' in out
