# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.filters
import SMSShell.exceptions


def test_abstract_init():
    """Test abstract init methods
    """
    abs = SMSShell.filters.AbstractFilter()
    with pytest.raises(NotImplementedError):
        abs('')

def test_lowercase_load():
    """Simple test with configuration sample loading
    """
    val = SMSShell.filters.LowerCase(1)
    assert isinstance(val, SMSShell.filters.AbstractFilter)

    SMSShell.filters.LowerCase('1')

    with pytest.raises(SMSShell.exceptions.ShellInitException):
        SMSShell.filters.LowerCase('a')

def test_lowercase_filtering():
    """Simple test with configuration sample loading
    """
    val = SMSShell.filters.LowerCase(1)
    assert val('Abcdef') == 'abcdef'
