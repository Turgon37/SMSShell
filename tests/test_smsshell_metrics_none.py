# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.metrics.none


def test_start():
    """Test base metrics helper class exception with init
    """
    metrics = SMSShell.metrics.none.MetricsHelper()
    assert metrics.start()

def test_stop():
    """
    """
    metrics = SMSShell.metrics.none.MetricsHelper()
    assert metrics.start()
    assert metrics.stop()
