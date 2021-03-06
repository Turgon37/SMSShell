# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.transmitters
import SMSShell.models


def test_abstract_init():
    """Test base transmitter class exception with init
    """
    abs = SMSShell.transmitters.AbstractTransmitter()
    with pytest.raises(NotImplementedError):
        abs.start()

    with pytest.raises(NotImplementedError):
        abs.stop()

def test_abstract_transmit():
    """Test base transmitter class exception
    """
    abs = SMSShell.transmitters.AbstractTransmitter()
    message = SMSShell.models.Message('local', '')
    with pytest.raises(NotImplementedError):
        abs.transmit(message)
