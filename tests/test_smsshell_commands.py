# -*- coding: utf8 -*-

import argparse
import logging
import pytest

import SMSShell
import SMSShell.commands


def test_abstract_init():
    """Test abstract init methods
    """
    abs = SMSShell.commands.AbstractCommand(logging.getLogger(),
                                            object(),
                                            object(),
                                            object())

    assert abs.name == 'abstractcommand'

def test_abstract_not_implemented():
    abs = SMSShell.commands.AbstractCommand(logging.getLogger(),
                                            object(),
                                            object(),
                                            object())

    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        abs.description([])
    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        abs.usage([])
    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        abs.main([])
