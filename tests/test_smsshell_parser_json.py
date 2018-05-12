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

import SMSShell.parsers.json
import SMSShell.models.message


# command line test
def test_parse_good_json_and_good_message():
    """"""
    parser = SMSShell.parsers.json.Parser()
    message = parser.parse('{"sms_number": "01234", "sms_text": "hello"}')
    assert isinstance(message, SMSShell.models.message.Message)

def test_parse_good_json_and_bad_message():
    """"""
    parser = SMSShell.parsers.json.Parser()
    with pytest.raises(SMSShell.parsers.BadMessageException) as exc:
        parser.parse('{"sms_number": null, "sms_text": "hello"}')
    assert exc.type == SMSShell.parsers.BadMessageException

    with pytest.raises(SMSShell.parsers.BadMessageException) as exc:
        parser.parse('{"sms_number": "", "sms_text": "hello"}')
    assert exc.type == SMSShell.parsers.BadMessageException

    with pytest.raises(SMSShell.parsers.BadMessageException) as exc:
        parser.parse('{"sms_number": "01234", "sms_text": null}')
    assert exc.type == SMSShell.parsers.BadMessageException

    with pytest.raises(SMSShell.parsers.BadMessageException) as exc:
        parser.parse('{"sms_number": "01234", "sms_text": ""}')
    assert exc.type == SMSShell.parsers.BadMessageException

def test_parse_good_json_and_partial_message():
    """"""
    parser = SMSShell.parsers.json.Parser()
    with pytest.raises(SMSShell.parsers.BadMessageException) as exc:
        parser.parse('{"sms_number": null}')
    assert exc.type == SMSShell.parsers.BadMessageException

    with pytest.raises(SMSShell.parsers.BadMessageException) as exc:
        parser.parse('{"sms_text": ""}')
    assert exc.type == SMSShell.parsers.BadMessageException

def test_parse_bad_json():
    """"""
    parser = SMSShell.parsers.json.Parser()
    with pytest.raises(SMSShell.parsers.ParsingException) as exc:
        parser.parse('{')
    assert exc.type == SMSShell.parsers.ParsingException
