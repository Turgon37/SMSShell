# -*- coding: utf8 -*-

import os
import pytest
import re
import sys

import SMSShell
import SMSShell.utils

def getBackupSample(file):
    return os.path.join('tests/sms_backup_samples', file)

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
    content = SMSShell.utils.GammuSMSParser.decode_from_env()
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
    content = SMSShell.utils.GammuSMSParser.decode_from_env()
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
    content = SMSShell.utils.GammuSMSParser.decode_from_env()
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
    content = SMSShell.utils.GammuSMSParser.decode_from_env()
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
    content = SMSShell.utils.GammuSMSParser.decode_from_env()
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
    content = SMSShell.utils.GammuSMSParser.decode_from_env()
    assert content['type'] == 'MMS'
    assert content['sms_number'] == '01234'
    assert content['mms_number'] == '01234'

def test_backupfile_simple_sms_decoding():
    """Test to decode a simple text sms
    """
    content = SMSShell.utils.GammuSMSParser.decode_from_backup_file_path(getBackupSample('simple_sms.txt'))
    assert isinstance(content, dict)
    assert len(content['errors']) == 0
    assert content['type'] == 'SMS'
    assert content['sms_number'] == '+3301234'
    assert content['sms_type'] == 'message'

def test_backupfile_unicode_sms_decoding():
    """test to decode a SMS with unicode caracters
    """
    content = SMSShell.utils.GammuSMSParser.decode_from_backup_file_path(getBackupSample('unicode_sms.txt'))
    assert isinstance(content, dict)
    assert len(content['errors']) == 0
    assert content['type'] == 'SMS'
    assert content['sms_number'] == '+3301234'
    assert content['sms_type'] == 'message'
    assert content['sms_text'] == '\u00c9'

def test_backupfile_smiley_sms_decoding():
    """Test to decode SMS with smileys
    """
    content = SMSShell.utils.GammuSMSParser.decode_from_backup_file_path(getBackupSample('smileys_sms.txt'))
    assert isinstance(content, dict)
    assert len(content['errors']) == 0
    assert content['type'] == 'SMS'
    assert content['sms_number'] == '+3301234'
    assert content['sms_type'] == 'message'
    assert len(content['sms_text']) == 8

def test_backupfile_mms_decoding():
    """Test to decode MMS indication in SMS
    """
    content = SMSShell.utils.GammuSMSParser.decode_from_backup_file_path(getBackupSample('mms.bin'))
    assert isinstance(content, dict)
    assert len(content['errors']) == 0
    assert content['type'] == 'MMS'
    assert content['sms_number'] == '+33012340000'
    assert content['sms_type'] == 'message'
    assert content['mms_address'] == 'http://213.227.3.60/mms.php?xP'
    assert content['mms_number'] == content['sms_number']

def test_backupfile_status_report_sms_decoding():
    """Test to decode a SMS status report
    """
    content = SMSShell.utils.GammuSMSParser.decode_from_backup_file_path(getBackupSample('status_report.txt'))
    assert isinstance(content, dict)
    assert len(content['errors']) == 0
    assert content['type'] == 'SMS'
    assert content['sms_number'] == '+3301234'
    assert content['sms_type'] == 'status_report'

def test_backupfile_missing_file():
    """Test to give an unexistent file
    """
    content = SMSShell.utils.GammuSMSParser.decode_from_backup_file_path(getBackupSample('unexistent_file'))
    assert isinstance(content, dict)
    assert content['errors']

def test_backupfile_unreadable_file():
    """Test to give an unreadable file
    """
    content = SMSShell.utils.GammuSMSParser.decode_from_backup_file_path(getBackupSample('/etc/shadow'))
    assert isinstance(content, dict)
    assert content['errors']
