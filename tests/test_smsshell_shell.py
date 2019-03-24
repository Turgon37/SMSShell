# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.config
import SMSShell.shell
import SMSShell.models.session
import SMSShell.metrics.none
import SMSShell.commands
import SMSShell.exceptions


def test_loading():
    """Test base transmitter class exception with init
    """
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    metrics = SMSShell.metrics.none.MetricsHelper()

    shell = SMSShell.shell.Shell(conf, metrics)
    session = SMSShell.models.session.Session('sender')

def test_loading_all_commands():
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    metrics = SMSShell.metrics.none.MetricsHelper()

    shell = SMSShell.shell.Shell(conf, metrics)
    session = SMSShell.models.session.Session('sender')

    assert shell.getAvailableCommands(session)
    shell.flushCommandCache()

def test_exec_command_help():
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    metrics = SMSShell.metrics.none.MetricsHelper()

    shell = SMSShell.shell.Shell(conf, metrics)

    assert shell.exec('sender', 'help')
    assert shell.exec('sender', 'help')

def test_exec_usage_on_all_commands():
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    metrics = SMSShell.metrics.none.MetricsHelper()

    shell = SMSShell.shell.Shell(conf, metrics)

    commands = shell.exec('sender', 'help')
    for c in commands.split():
        assert shell.exec('sender', 'help ' + c)
        assert shell.exec('sender', 'desc ' + c)

def test_exec_command_not_found():
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    metrics = SMSShell.metrics.none.MetricsHelper()

    shell = SMSShell.shell.Shell(conf, metrics)

    with pytest.raises(SMSShell.commands.CommandNotFoundException):
        shell.exec('sender', 'nonexistent')

def test_exec_with_bad_syntax():
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    metrics = SMSShell.metrics.none.MetricsHelper()

    shell = SMSShell.shell.Shell(conf, metrics)

    with pytest.raises(SMSShell.exceptions.ShellException):
        shell.exec('sender', '"')

    with pytest.raises(SMSShell.exceptions.ShellException):
        shell.exec('sender', '\\')

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

    metrics = SMSShell.metrics.none.MetricsHelper()

    shell = SMSShell.shell.Shell(conf, metrics)
    sw = shell.getSecureShell()
    sw.flushCommandCache()

def test_secure_wrapper_isolation():
    """Test secure shell for critical attributes
    """
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    metrics = SMSShell.metrics.none.MetricsHelper()

    shell = SMSShell.shell.Shell(conf, metrics)
    sw = shell.getSecureShell()

    with pytest.raises(AttributeError):
        sw.exec('user1', 'help')
