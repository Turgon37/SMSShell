# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.metrics.prometheus


def test_run():
    """Test base metrics helper class exception with init
    """
    metrics = SMSShell.metrics.prometheus.MetricsHelper()
    assert metrics.start()
    assert metrics.stop()

def test_init_bad_configuration():
    """Test base metrics helper class exception with init
    """
    metrics = SMSShell.metrics.prometheus.MetricsHelper(config=dict(listen_port='a'))
