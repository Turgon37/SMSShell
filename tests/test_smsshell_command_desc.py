# -*- coding: utf8 -*-

import configparser
import logging
import pytest

import SMSShell
import SMSShell.config
import SMSShell.commands.desc


def test_init():
    """Test abstract init methods
    """
    com = SMSShell.commands.desc.Desc(logging.getLogger(),
                                      object(),
                                      dict(),
                                      object())

def test_main():
    """Test abstract init methods
    """
    shell = SMSShell.shell.Shell(SMSShell.config.MyConfigParser(), object())
    assert isinstance(shell.exec('local', 'desc'), str)
