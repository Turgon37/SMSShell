# -*- coding: utf8 -*-

import pytest

import SMSShell
import SMSShell.transmitters.python_gammu


def test_init(capsys):
    transmitter = SMSShell.transmitters.python_gammu.Transmitter()

def test_without_gammurc(capsys):
    transmitter = SMSShell.transmitters.python_gammu.Transmitter()
    assert not transmitter.start()
