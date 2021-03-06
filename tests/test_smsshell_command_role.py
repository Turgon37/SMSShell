# -*- coding: utf8 -*-

import configparser
import logging
import pytest

import SMSShell
import SMSShell.config
import SMSShell.commands.role


def test_init():
    """Test abstract init methods
    """
    com = SMSShell.commands.role.Role(logging.getLogger(),
                                      object(),
                                      dict(),
                                      object())

def test_main():
    """Test abstract init methods
    """
    shell = SMSShell.shell.Shell(SMSShell.config.MyConfigParser(), object())
    assert isinstance(shell.exec('local', 'role'), str)
