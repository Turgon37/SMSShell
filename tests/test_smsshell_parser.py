# -*- coding: utf8 -*-

import json
import pytest

import SMSShell
import SMSShell.parsers


def test_abstract_class():
    """"""
    abs = SMSShell.parsers.AbstractParser()
    with pytest.raises(NotImplementedError):
        abs.parse('')
