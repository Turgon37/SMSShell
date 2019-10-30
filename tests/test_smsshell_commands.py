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

def test_abstract_bad_input_state_type():

    class Bad(SMSShell.commands.AbstractCommand):
        def inputStates(self):
            return dict()

    com = Bad(logging.getLogger(),
              object(),
              object(),
              object())
    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        com._inputStates()


def test_abstract_bad_input_state_value():

    class Bad(SMSShell.commands.AbstractCommand):
        def inputStates(self):
            return ['d']

    com = Bad(logging.getLogger(),
              object(),
              object(),
              object())
    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        com._inputStates()


def test_abstract_bad_arg_parser_type():

    class Bad(SMSShell.commands.AbstractCommand):
        def argsParser(self):
            return 'a'

    com = Bad(logging.getLogger(),
              object(),
              object(),
              object())
    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        com._argsParser()

def test_abstract_bad_arg_parser_init():

    class Bad(SMSShell.commands.AbstractCommand):
        def argsParser(self):
            raise ValueError('no')

    com = Bad(logging.getLogger(),
              object(),
              object(),
              object())
    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        com._argsParser()
