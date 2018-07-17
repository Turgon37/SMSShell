# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.config
import SMSShell.shell
import SMSShell.models.session
import SMSShell.commands


def test_loading():
    """Test base transmitter class exception with init
    """
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    shell = SMSShell.shell.Shell(conf)
    session = SMSShell.models.session.Session('sender')

def test_loading_all_commands():
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    shell = SMSShell.shell.Shell(conf)
    session = SMSShell.models.session.Session('sender')

    assert shell.getAvailableCommands(session)
    shell.flushCommandCache()

def test_exec_command_help():
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    shell = SMSShell.shell.Shell(conf)

    assert shell.exec('sender', 'help')
    assert shell.exec('sender', 'help')

def test_exec_command_not_found():
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    shell = SMSShell.shell.Shell(conf)

    with pytest.raises(SMSShell.commands.CommandNotFoundException):
        shell.exec('sender', 'nonexistent')

# def test_exec_command_forbidden():
#     conf = SMSShell.config.MyConfigParser()
#     assert conf.load('./config.conf')[1]
#     assert conf.isLoaded()
#
#     shell = SMSShell.shell.Shell(conf)
#
#     with pytest.raises(SMSShell.commands.CommandForbidden):
#         shell.exec('sender', 'logout')

def test_secure_wrapper():
    """Test to use secure shell wrapper
    """
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    shell = SMSShell.shell.Shell(conf)
    sw = shell.getSecureShell()
    sw.flushCommandCache()

def test_secure_wrapper_isolation():
    """Test secure shell for critical attributes
    """
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    shell = SMSShell.shell.Shell(conf)
    sw = shell.getSecureShell()

    with pytest.raises(AttributeError):
        sw.exec('user1', 'help')