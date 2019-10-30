# -*- coding: utf8 -*-

import logging
import SMSShell
import SMSShell.config
import SMSShell.metrics.none
import SMSShell.commands.role


def test_init():
    """Test abstract init methods
    """
    SMSShell.commands.role.Role(logging.getLogger(),
                                object(),
                                dict(),
                                SMSShell.metrics.none.MetricsHelper())

def test_main():
    """Test abstract init methods
    """
    shell = SMSShell.shell.Shell(SMSShell.config.MyConfigParser(),
                                 SMSShell.metrics.none.MetricsHelper())
    assert isinstance(shell.exec('local', 'role'), str)
