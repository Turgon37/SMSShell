# -*- coding: utf8 -*-

import logging
import pytest

import SMSShell
import SMSShell.config
import SMSShell.metrics.none
import SMSShell.exceptions
import SMSShell.commands.desc


def test_init():
    """Test abstract init methods
    """
    SMSShell.commands.desc.Desc(logging.getLogger(),
                                object(),
                                dict(),
                                SMSShell.metrics.none.MetricsHelper())

def test_main():
    """Test abstract init methods
    """
    shell = SMSShell.shell.Shell(SMSShell.config.MyConfigParser(),
                                 SMSShell.metrics.none.MetricsHelper())

    with pytest.raises(SMSShell.exceptions.BadCommandCall):
        shell.exec('local', 'desc')

    assert isinstance(shell.exec('local', 'desc desc'), str)

def test_command_not_available():
    """Test abstract init methods
    """
    shell = SMSShell.shell.Shell(SMSShell.config.MyConfigParser(),
                                 SMSShell.metrics.none.MetricsHelper())
    assert isinstance(shell.exec('local', 'desc nonexitent'), str)
