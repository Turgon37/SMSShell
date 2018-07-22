# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.metrics


def test_abstract_init():
    """Test base metrics helper class exception with init
    """
    abs = SMSShell.metrics.AbstractMetricsHelper()
    with pytest.raises(NotImplementedError):
        abs.start()

    with pytest.raises(NotImplementedError):
        abs.stop()

def test_abstract_name_normalizer():
    """
    """
    abs = SMSShell.metrics.AbstractMetricsHelper()
    name = abs.normalizeName('1.2.3.4.5')
    assert abs.SEPARATOR in name

    abs_with_underscore = SMSShell.metrics.AbstractMetricsHelper()
    abs_with_underscore.SEPARATOR = '_'
    name2 = abs_with_underscore.normalizeName('1.2.3.4.5')
    assert abs_with_underscore.SEPARATOR in name2
    assert '.' not in name2

def test_abstract_counter():
    """
    """
    abs = SMSShell.metrics.AbstractMetricsHelper()
