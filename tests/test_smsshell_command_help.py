# -*- coding: utf8 -*-

import logging
import SMSShell
import SMSShell.config
import SMSShell.metrics.none
import SMSShell.commands.help


def test_init():
    """Test abstract init methods
    """
    SMSShell.commands.help.Help(logging.getLogger(),
                                object(),
                                dict(),
                                SMSShell.metrics.none.MetricsHelper())

def test_main():
    """Test abstract init methods
    """
    shell = SMSShell.shell.Shell(SMSShell.config.MyConfigParser(),
                                 SMSShell.metrics.none.MetricsHelper())
    assert isinstance(shell.exec('local', 'help'), str)
    assert isinstance(shell.exec('local', 'help help'), str)

def test_command_not_available():
    """Test abstract init methods
    """
    shell = SMSShell.shell.Shell(SMSShell.config.MyConfigParser(),
                                 SMSShell.metrics.none.MetricsHelper())
    assert isinstance(shell.exec('local', 'help nonexitent'), str)
