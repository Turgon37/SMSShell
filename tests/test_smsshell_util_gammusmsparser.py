# -*- coding: utf8 -*-

import os

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

import SMSShell.utils


def test_env_sms_decoding_with_good_single_message():
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
    assert 'sms_text' in content
    assert content['sms_text'] == 'ghgg'
    assert 'errors' in content
    assert len(content['errors']) == 0

def test_env_sms_decoding_with_good_multipart_message():
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
    assert 'sms_text' in content
    assert content['sms_text'] == 'ABCDEFGH'
    assert 'errors' in content
    assert len(content['errors']) == 0

def test_env_sms_decoding_with_different_common_values():
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
    assert 'sms_text' in content
    assert content['sms_text'] == 'ABCDEFGH'
    assert 'errors' in content
    assert len(content['errors']) >= 0

def test_env_sms_decoding_with_different_decoded_parts():
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
    assert 'sms_text' in content
    assert content['sms_text'] == 'ABCDEFGH'
    assert 'errors' in content
    assert len(content['errors']) >= 0
