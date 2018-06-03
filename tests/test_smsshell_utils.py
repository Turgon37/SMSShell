# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.utils


def test_user_to_uid():
    """"""
    assert SMSShell.utils.userToUid('root') == 0
    assert SMSShell.utils.userToUid('0') == 0

    with pytest.raises(KeyError):
        SMSShell.utils.userToUid('roo')

def test_group_to_gid():
    """"""
    assert SMSShell.utils.groupToGid('root') == 0
    assert SMSShell.utils.groupToGid('0') == 0

    with pytest.raises(KeyError):
        SMSShell.utils.groupToGid('roo')
