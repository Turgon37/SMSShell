# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.models.message


def test_message():
    """Test Message attributes
    """
    m = SMSShell.models.message.Message('sender', 'content')
    assert m.sender == 'sender'
    assert m.content == 'content'
    assert isinstance(m.asString(), str)
    assert 'content' in str(m)
    assert 'sender' in repr(m)
