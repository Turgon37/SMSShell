# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.utils


def test_user_to_uid():
    """"""
    assert SMSShell.utils.user_to_uid('root') == 0
    assert SMSShell.utils.user_to_uid('0') == 0

    with pytest.raises(KeyError):
        SMSShell.utils.user_to_uid('roo')

def test_group_to_gid():
    """"""
    assert SMSShell.utils.group_to_gid('root') == 0
    assert SMSShell.utils.group_to_gid('0') == 0

    with pytest.raises(KeyError):
        SMSShell.utils.group_to_gid('roo')
