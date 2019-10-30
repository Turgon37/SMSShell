# -*- coding: utf8 -*-

import datetime
import pytest
import time

import SMSShell
import SMSShell.models.session
from SMSShell.models.session import SessionStates, BadStateTransitionException

def test_session():
    """Test Session attributes
    """
    s = SMSShell.models.session.Session('sender', 20)
    assert s.subject == 'sender'
    assert s.state == SessionStates.STATE_GUEST
    assert s.ttl == 20
    assert 'sender' in str(s)
    assert 'sender' in repr(s)

    assert s.access_at <= datetime.datetime.today()

def test_session_good_state_transition():
    """Perform a good state transition
    """
    s = SMSShell.models.session.Session('sender')
    s.state = SessionStates.STATE_LOGININPROGRESS

def test_session_bad_state_transition():
    """Performe a bad state transition
    """
    s = SMSShell.models.session.Session('sender')
    s.state = SessionStates.STATE_USER
    with pytest.raises(BadStateTransitionException):
        s.state = SessionStates.STATE_LOGININPROGRESS

    with pytest.raises(BadStateTransitionException):
        s.state = 1

    with pytest.raises(BadStateTransitionException):
        s.force_state(1)

def test_session_ttl():
    """Test ttl validation
    """
    s = SMSShell.models.session.Session('sender', 1)
    assert s.is_valid()
    time.sleep(1.1)
    assert not s.is_valid()

def test_session_storage_access():
    """Test session storage get/set
    """
    s = SMSShell.models.session.Session('sender')
    s.set('key', 'sample')
    assert s.get('key') == 'sample'

def test_session_storage_isolation():
    """Test session storage for isolation
    """
    s = SMSShell.models.session.Session('sender')
    s.set_storage_prefix('user1')
    s.set('key', 'sample1')
    s.set_storage_prefix('user2')
    s.set('key', 'sample2')
    s.set_storage_prefix('')

    assert s.get('key') is None
    s.set_storage_prefix('user1')
    assert s.get('key') == 'sample1'
    s.set_storage_prefix('user2')
    assert s.get('key') == 'sample2'

def test_session_secure_wrapper():
    """Test to use secure session wrapper
    """
    s = SMSShell.models.session.Session('sender')
    sw = s.get_secure_session()

    sw.set('key', 'sample')
    assert sw.get('key') == 'sample'

def test_session_secure_wrapper_isolation():
    """Test secure session for critical attributes
    """
    s = SMSShell.models.session.Session('sender')
    sw = s.get_secure_session()

    with pytest.raises(AttributeError):
        sw.set_storage_prefix('user1')

    with pytest.raises(AttributeError):
        sw.force_state(SessionStates.STATE_LOGININPROGRESS)
