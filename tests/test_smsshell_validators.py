# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.validators


def test_abstract_init():
    """Test abstract init methods
    """
    abs = SMSShell.validators.AbstractValidator()
    with pytest.raises(NotImplementedError):
        abs('')

def test_regexp_load():
    """Simple test with configuration sample loading
    """
    val = SMSShell.validators.Regexp('[a-z]')
    assert isinstance(val, SMSShell.validators.AbstractValidator)

def test_regexp_data_valid():
    """Simple test with configuration sample loading
    """
    val = SMSShell.validators.Regexp('^a$')
    assert val('a')

def test_regexp_data_invalid():
    """Simple test with configuration sample loading
    """
    val = SMSShell.validators.Regexp('^a$')
    with pytest.raises(SMSShell.validators.ValidationException):
        val('b')
