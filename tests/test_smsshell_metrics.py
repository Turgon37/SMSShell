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

    with pytest.raises(NotImplementedError):
        abs.counter('a')

    with pytest.raises(NotImplementedError):
        abs.gauge('a')

def test_abstract_name_normalizer():
    """
    """
    abs = SMSShell.metrics.AbstractMetricsHelper()
    name = abs.normalize_name('1.2.3.4.5')
    assert abs.SEPARATOR in name
    assert abs.PREFIX in name
    assert abs.normalize_name('1') == abs.normalize_name(abs.SEPARATOR.join([abs.PREFIX, '1']))

    abs_with_underscore = SMSShell.metrics.AbstractMetricsHelper()
    abs_with_underscore.SEPARATOR = '_'
    name2 = abs_with_underscore.normalize_name('1.2.3.4.5')
    assert abs_with_underscore.SEPARATOR in name2
    assert '.' not in name2
