# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.validators
import SMSShell.models.message


def test_abstract_init():
    """Test abstract init methods
    """
    abs = SMSShell.validators.AbstractValidator()
    with pytest.raises(NotImplementedError):
        abs('')

def test_message_load_validator():
    class V():
        def __call__(self, data):
            assert data == 'a'

    chain = SMSShell.validators.ValidatorChain()
    with pytest.raises(SMSShell.exceptions.ShellInitException):
        chain.addLinksFromDict({'number': [V()]})

def test_message_load_validator():
    m = SMSShell.models.message.Message('a', 'b')

    class V(SMSShell.validators.AbstractValidator):
        def __call__(self, data):
            assert data == 'a'

    chain = SMSShell.validators.ValidatorChain()
    chain.addLinksFromDict({'number': [V()]})
    chain.callChainOnObject(m)

def test_message_load_validator_on_missing_field():
    m = SMSShell.models.message.Message('a', 'b')

    class V(SMSShell.validators.AbstractValidator):
        def __call__(self, data):
            pass

    chain = SMSShell.validators.ValidatorChain()
    chain.addLinksFromDict({'nonexistent': [V()]})
    with pytest.raises(SMSShell.validators.ValidationException):
        chain.callChainOnObject(m)

# Regexp validator

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
