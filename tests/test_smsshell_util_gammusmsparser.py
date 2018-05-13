# -*- coding: utf8 -*-

import os
import pytest
import re

import SMSShell
import SMSShell.utils

@pytest.yield_fixture
def environSetup():
    """Purge environment variables from resulting tests
    """
    regex = re.compile('^(SMS|DECODED)_')
    keys_to_remove = []
    for key in os.environ:
        if regex.match(key):
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del os.environ[key]
    yield True


def test_env_sms_decoding_with_good_single_message(environSetup):
    """"""
    env = dict(
        SMS_MESSAGES="1",
        DECODED_PARTS="0",
        SMS_1_NUMBER="0124",
        SMS_1_CLASS="-1",
        SMS_1_TEXT="ghgg",
    )
    for key in env:
        os.environ[key] = env[key]
    content = SMSShell.utils.GammuSMSParser.decodeFromEnv()
    assert content['sms_text'] == 'ghgg'
    assert content['type'] == 'SMS'
    assert 'errors' in content
    assert len(content['errors']) == 0


def test_env_sms_decoding_with_good_multipart_message(environSetup):
    """"""
    env = dict(
        SMS_MESSAGES="2",
        DECODED_PARTS="1",
        DECODED_0_TEXT="ABCDEFGH",
        SMS_1_NUMBER="0124",
        SMS_1_CLASS="-1",
        SMS_1_TEXT="ABCD",
        SMS_2_NUMBER="0124",
        SMS_2_CLASS="-1",
        SMS_2_TEXT="EFGH",
    )
    for key in env:
        os.environ[key] = env[key]
    content = SMSShell.utils.GammuSMSParser.decodeFromEnv()
    assert content['sms_text'] == 'ABCDEFGH'
    assert content['type'] == 'SMS'
    assert 'errors' in content
    assert len(content['errors']) == 0


def test_env_sms_decoding_with_empty_values(environSetup):
    """"""
    env = dict(
        SMS_MESSAGES="0",
        DECODED_PARTS="0",
    )
    for key in env:
        os.environ[key] = env[key]
    content = SMSShell.utils.GammuSMSParser.decodeFromEnv()
    assert content['type'] == None
    assert 'errors' in content
    assert len(content['errors']) >= 0


def test_env_sms_decoding_with_different_common_values(environSetup):
    """"""
    env = dict(
        SMS_MESSAGES="2",
        DECODED_PARTS="1",
        DECODED_0_TEXT="ABCDEFGH",
        SMS_1_NUMBER="0124",
        SMS_1_CLASS="-1",
        SMS_1_TEXT="ABCD",
        SMS_2_NUMBER="01245",
        SMS_2_CLASS="-1",
        SMS_2_TEXT="EFGH",
    )
    for key in env:
        os.environ[key] = env[key]
    content = SMSShell.utils.GammuSMSParser.decodeFromEnv()
    assert content['sms_text'] == 'ABCDEFGH'
    assert content['type'] == 'SMS'
    assert 'errors' in content
    assert len(content['errors']) >= 0


def test_env_sms_decoding_with_different_decoded_parts(environSetup):
    """"""
    env = dict(
        SMS_MESSAGES="2",
        DECODED_PARTS="1",
        DECODED_0_TEXT="ABCDEFGH",
        SMS_1_NUMBER="0124",
        SMS_1_CLASS="-1",
        SMS_1_TEXT="ABCD",
        SMS_2_NUMBER="01245",
        SMS_2_CLASS="-1",
        SMS_2_TEXT=" EFGH",
    )
    for key in env:
        os.environ[key] = env[key]
    content = SMSShell.utils.GammuSMSParser.decodeFromEnv()
    assert content['sms_text'] == 'ABCDEFGH'
    assert content['type'] == 'SMS'
    assert 'errors' in content
    assert len(content['errors']) >= 0


def test_env_mms_decoding(environSetup):
    """
    """
    env = dict(
        DECODED_1_MMS_SENDER="01234/TYPE=PLMN",
        SMS_MESSAGES="1",
        DECODED_PARTS="1",
        DECODED_1_MMS_SIZE="0",
        DECODED_1_MMS_TITLE="",
        DECODED_1_MMS_ADDRESS="",
        SMS_1_NUMBER="01234",
        SMS_1_CLASS="-1",
    )
    for key in env:
        os.environ[key] = env[key]
    content = SMSShell.utils.GammuSMSParser.decodeFromEnv()
    assert content['type'] == 'MMS'
    assert content['sms_number'] == '01234'
    assert content['mms_number'] == '01234'
