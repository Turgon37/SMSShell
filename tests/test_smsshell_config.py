# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.config


def test_loading():
    """Simple test with configuration sample loading
    """
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

def test_with_bad_file_path():
    """Test to give a bad file path
    """
    conf = SMSShell.config.MyConfigParser()
    assert not conf.load('/nonexistent')[0]
    assert not conf.isLoaded()

def test_getter():
    """Test getter
    """
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.isLoaded()

    assert isinstance(conf.getPidPath(), str)
    assert conf.getLogLevel('null') != 'null'

    uid = conf.getUid()
    assert isinstance(uid, int) or uid is None

    gid = conf.getGid()
    assert isinstance(gid, int) or gid is None

    assert isinstance(conf.getMode(), str)

    c_mode = conf.getModeConfig(conf.getMode())
    assert isinstance(c_mode, dict) or c_mode is None

    assert not conf.getSectionOrEmpty('no_section')

    assert conf.getSectionOrEmpty('main')
