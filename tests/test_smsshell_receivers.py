# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.receivers


def test_abstract_init():
    """Test abstract init methods
    """
    abs = SMSShell.receivers.AbstractReceiver()
    with pytest.raises(NotImplementedError):
        abs.start()

    with pytest.raises(NotImplementedError):
        abs.stop()

def test_abstract_read():
    """Test abstract read method
    """
    abs = SMSShell.receivers.AbstractReceiver()
    with pytest.raises(NotImplementedError):
        abs.read()
