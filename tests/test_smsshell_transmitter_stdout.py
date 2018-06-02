# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.transmitters.stdout


def test_simple_transmit(capsys):
    """Test base parser class exception
    """
    transmitter = SMSShell.transmitters.stdout.Transmitter()
    message = transmitter.transmit('OK')
    out, err = capsys.readouterr()
    assert 'OK' in out
