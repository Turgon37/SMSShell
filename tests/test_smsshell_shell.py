# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.config
import SMSShell.shell


def test_loading():
    """Test base transmitter class exception with init
    """
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    program = SMSShell.shell.Shell(conf)
