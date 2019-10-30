# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.models.message


def test_message():
    """Test Message attributes
    """
    m = SMSShell.models.message.Message('sender', 'content')
    assert m.number == 'sender'
    assert m.content == 'content'
    assert isinstance(m.as_string(), str)
    assert 'content' in str(m)
    assert 'sender' in repr(m)

def test_message_attribute():
    m = SMSShell.models.message.Message('a', 'b', attributes={'a': 2})
    assert m.attribute('a') == 2

    assert 'a' in m.attributes

def test_message_missing_attribute():
    m = SMSShell.models.message.Message('a', 'b', attributes={'a': 2})

    with pytest.raises(AttributeError):
        m.attribute('b')

    assert m.attribute('b', 'fallback') == 'fallback'
