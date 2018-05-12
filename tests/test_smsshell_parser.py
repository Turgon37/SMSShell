# -*- coding: utf8 -*-

import json
import pytest

try:
    import SMSShell
except ImportError:
    sys.path.insert(1, os.path.join(
        os.path.dirname(
            os.path.realpath(__file__)
        ),
        os.pardir)
    )
    import SMSShell

import SMSShell.parsers


def test_abstract_class():
    """"""
    abs = SMSShell.parsers.AbstractParser()
    with pytest.raises(NotImplementedError):
        abs.parse('')
