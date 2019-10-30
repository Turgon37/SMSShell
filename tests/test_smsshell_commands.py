# -*- coding: utf8 -*-

import logging
import pytest

import SMSShell
import SMSShell.commands


def test_abstract_init():
    """Test abstract init methods
    """
    com = SMSShell.commands.AbstractCommand(logging.getLogger(),
                                            object(),
                                            object(),
                                            object())

    assert com.name == 'abstractcommand'

def test_abstract_not_implemented():
    com = SMSShell.commands.AbstractCommand(logging.getLogger(),
                                            object(),
                                            object(),
                                            object())

    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        com.description([])
    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        com.usage([])
    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        com.main([])

def test_abstract_bad_input_state_type():

    class Bad(SMSShell.commands.AbstractCommand):
        def input_states(self):
            return dict()

    com = Bad(logging.getLogger(),
              object(),
              object(),
              object())
    session = SMSShell.models.session.Session('sender')

    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        SMSShell.shell.Shell.has_session_access_to_command(session, com)


def test_abstract_bad_input_state_value():

    class Bad(SMSShell.commands.AbstractCommand):
        def input_states(self):
            return ['d']

    com = Bad(logging.getLogger(),
              object(),
              object(),
              object())
    session = SMSShell.models.session.Session('sender')

    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        SMSShell.shell.Shell.has_session_access_to_command(session, com)


def test_abstract_bad_arg_parser_type():

    class Bad(SMSShell.commands.AbstractCommand):
        def args_parser(self):
            return 'a'

    com = Bad(logging.getLogger(),
              object(),
              object(),
              object())
    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        com._args_parser()

def test_abstract_bad_arg_parser_init():

    class Bad(SMSShell.commands.AbstractCommand):
        def args_parser(self):
            raise ValueError('no')

    com = Bad(logging.getLogger(),
              object(),
              object(),
              object())
    with pytest.raises(SMSShell.commands.CommandBadImplemented):
        com._args_parser()
