# -*- coding: utf8 -*-

import configparser
import pytest
import os

import SMSShell
import SMSShell.config


def test_loading():
    """Simple test with configuration sample loading
    """
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.is_loaded()

def test_with_bad_file_path():
    """Test to give a bad file path
    """
    conf = SMSShell.config.MyConfigParser()
    assert not conf.load('/nonexistent')[0]
    assert not conf.is_loaded()

def test_with_bad_file_content():
    """Test to give a bad file content
    """
    conf = SMSShell.config.MyConfigParser()
    with open('error.ini', 'w') as configfile:
        configfile.write("test")
    assert not conf.load('error.ini')[0]
    assert not conf.is_loaded()
    os.unlink('error.ini')

def test_with_bad_log_level():
    """Test to give a bad log level
    """
    conf = SMSShell.config.MyConfigParser()

    writer = configparser.ConfigParser()
    writer[conf.MAIN_SECTION] = dict()
    writer[conf.MAIN_SECTION]['log_level'] = 'nonexistent'

    with open('error.ini', 'w') as configfile:
        writer.write(configfile)
    assert conf.load('error.ini')[0]
    assert conf.is_loaded()
    os.unlink('error.ini')

    assert conf.get_log_level(default='_default_') == '_default_'

def test_with_bad_uid_mapping():
    """Test to give a bad uid value
    """
    conf = SMSShell.config.MyConfigParser()

    writer = configparser.ConfigParser()
    writer[conf.MAIN_SECTION] = dict()
    writer[conf.MAIN_SECTION]['user'] = 'nonexistent'

    with open('error.ini', 'w') as configfile:
        writer.write(configfile)
    assert conf.load('error.ini')[0]
    assert conf.is_loaded()
    os.unlink('error.ini')

    assert conf.get_uid() is None

def test_with_bad_gid_mapping():
    """Test to give a bad gid value
    """
    conf = SMSShell.config.MyConfigParser()

    writer = configparser.ConfigParser()
    writer[conf.MAIN_SECTION] = dict()
    writer[conf.MAIN_SECTION]['group'] = 'nonexistent'

    with open('error.ini', 'w') as configfile:
        writer.write(configfile)
    assert conf.load('error.ini')[0]
    assert conf.is_loaded()
    os.unlink('error.ini')

    assert conf.get_gid() is None

def test_getter():
    """Test getter
    """
    conf = SMSShell.config.MyConfigParser()
    assert conf.load('./config.conf')[1]
    assert conf.is_loaded()

    assert conf.get_log_level('null') != 'null'

    uid = conf.get_uid()
    assert isinstance(uid, int) or uid is None

    gid = conf.get_gid()
    assert isinstance(gid, int) or gid is None

    assert isinstance(conf.get_mode(), str)

    c_mode = conf.get_mode_config(conf.get_mode())
    assert isinstance(c_mode, dict) or c_mode is None

    assert not conf.get_section_or_empty('no_section')

    assert conf.get_section_or_empty('main')

def test_with_classes_chain_loading():
    """Test correct parsing of classes chain
    """
    conf = SMSShell.config.MyConfigParser()

    writer = configparser.ConfigParser()
    writer['test'] = dict()
    writer['test']['chain'] = 'a=f1:|f2:tes|f3:a,b'

    with open('chain.ini', 'w') as configfile:
        writer.write(configfile)
    assert conf.load('chain.ini')[0]
    assert conf.is_loaded()
    os.unlink('chain.ini')

    class module:

        class F1:
            pass

        class F2:
            def __init__(self, value):
                self.value = value

        class F3:
            def __init__(self, value1, value2):
                self.values = (value1, value2)

    spec = conf.get_classes_chain_from_config('test', 'chain', module)
    assert 'a' in spec
    assert isinstance(spec['a'][0], module.F1)
    assert isinstance(spec['a'][1], module.F2)
    assert spec['a'][1].value == 'tes'
    assert isinstance(spec['a'][2], module.F3)
    assert spec['a'][2].values == ('a', 'b')

def test_with_classes_chain_missing_filter_class():
    """Test correct parsing of classes chain
    """
    conf = SMSShell.config.MyConfigParser()

    writer = configparser.ConfigParser()
    writer['test'] = dict()
    writer['test']['chain'] = 'a=f1:|f4:tes'

    with open('chain.ini', 'w') as configfile:
        writer.write(configfile)
    assert conf.load('chain.ini')[0]
    assert conf.is_loaded()
    os.unlink('chain.ini')

    class module:

        class F1:
            pass

    spec = conf.get_classes_chain_from_config('test', 'chain', module)
    assert 'a' in spec
    assert len(spec['a']) == 1
    assert isinstance(spec['a'][0], module.F1)

def test_with_classes_chain_bad_filter_config():
    """Test correct parsing of classes chain
    """
    conf = SMSShell.config.MyConfigParser()

    writer = configparser.ConfigParser()
    writer['test'] = dict()
    writer['test']['chain'] = 'a=f1:tes'

    with open('chain.ini', 'w') as configfile:
        writer.write(configfile)
    assert conf.load('chain.ini')[0]
    assert conf.is_loaded()
    os.unlink('chain.ini')

    class module:

        class F1:
            pass

    with pytest.raises(SMSShell.exceptions.ShellInitException):
        spec = conf.get_classes_chain_from_config('test', 'chain', module)
