# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.transmitters


def test_abstract_class():
    """Test base transmitter class exception
    """
    abs = SMSShell.transmitters.AbstractTransmitter()
    with pytest.raises(NotImplementedError):
        abs.transmit('')
