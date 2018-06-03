# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.smsshell


def test_loading():
    """Test base transmitter class exception with init
    """
    program = SMSShell.smsshell.SMSShell()
