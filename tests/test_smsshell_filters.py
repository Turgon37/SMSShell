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

def test_bad_filter_class():
    class V():
        def __call__(self, data):
            assert data == 'a'

    chain = SMSShell.filters.FilterChain()
    with pytest.raises(SMSShell.exceptions.ShellInitException):
        chain.addLinksFromDict({'number': [V()]})

def test_message_filter():
    m = SMSShell.models.message.Message('a', 'b')

    class V(SMSShell.filters.AbstractFilter):
        def __call__(self, data):
            assert data == 'a'

    chain = SMSShell.filters.FilterChain()
    chain.addLinksFromDict({'number': [V()]})
    assert chain.callChainOnObject(m)

def test_message_filter_on_missing_field():
    m = SMSShell.models.message.Message('a', 'b')

    class V(SMSShell.filters.AbstractFilter):
        def __call__(self, data):
            pass

    chain = SMSShell.filters.FilterChain()
    chain.addLinksFromDict({'nonexistent': [V()]})
    with pytest.raises(SMSShell.filters.FilterException):
        chain.callChainOnObject(m)

# LowerCase filter

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
