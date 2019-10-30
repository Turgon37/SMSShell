# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.receivers


def test_abstract_receiver_init():
    """Test abstract init methods
    """
    abs = SMSShell.receivers.AbstractReceiver()
    with pytest.raises(NotImplementedError):
        abs.start()

    with pytest.raises(NotImplementedError):
        abs.stop()

def test_abstract_receiver_read():
    """Test abstract read method
    """
    abs = SMSShell.receivers.AbstractReceiver()
    with pytest.raises(NotImplementedError):
        abs.read()

def test_abstract_context_init():
    """Test abstract read method
    """
    abs = SMSShell.receivers.AbstractClientRequest('')
    with pytest.raises(NotImplementedError):
        abs.enter()

    with pytest.raises(NotImplementedError):
        abs.exit()

def test_abstract_context_bad_usage():
    """Test abstract read method
    """
    abs = SMSShell.receivers.AbstractClientRequest('')
    with pytest.raises(RuntimeError):
        abs.get_request_data()
