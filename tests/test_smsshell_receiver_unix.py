# -*- coding: utf8 -*-

import json
import os
import pytest
import queue
import shlex
import socket
import stat
import subprocess
import threading

import SMSShell
import SMSShell.receivers.unix

def test_start():
    """Just start and stop the receiver
    """
    unix = './r_unix'
    receiver = SMSShell.receivers.unix.Receiver(config=dict(
                                                    path=unix,
                                                    umask='80'))
    assert receiver.start()
    assert os.path.exists(unix)
    assert stat.S_ISSOCK(os.stat(unix).st_mode)

    assert receiver.stop()
    assert not os.path.exists(unix)

def test_start_with_existing_socket():
    """Just start and stop the receiver
    """
    unix = './r_unix'
    receiver = SMSShell.receivers.unix.Receiver(config=dict(
                                                    path=unix,
                                                    umask='80'))

    # create a unix socket then close it
    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_socket.bind(unix)
    server_socket.close()
    assert os.path.exists(unix)
    assert stat.S_ISSOCK(os.stat(unix).st_mode)

    assert receiver.start()
    assert os.path.exists(unix)
    assert stat.S_ISSOCK(os.stat(unix).st_mode)

    assert receiver.stop()
    assert not os.path.exists(unix)

def test_init_with_bad_config():
    """Just start and stop the receiver
    """
    unix = './r_unix'
    receiver = SMSShell.receivers.unix.Receiver(config=dict(
                                                    path=unix,
                                                    umask='80',
                                                    listen_queue='a'))
    assert isinstance(receiver, SMSShell.receivers.unix.Receiver)

def test_bad_start_because_path_already_exists():
    """Ensure receiver do not start if path exists
    """
    unix = './r_unix'
    receiver = SMSShell.receivers.unix.Receiver(config=dict(path=unix))
    # create the path
    os.mkdir(unix)
    assert os.path.exists(unix)
    assert os.path.isdir(unix)
    # test start for error
    assert not receiver.start()
    # clean
    os.rmdir(unix)
    assert not os.path.exists(unix)

def test_bad_start_because_path_not_writable():
    """Ensure receiver do not start correctly if path is not writable
    """
    unix = '/root/r_unix'
    receiver = SMSShell.receivers.unix.Receiver(config=dict(path=unix))
    assert not receiver.start()

def test_bad_stop_because_path_already_deleted():
    """Ensure receiver do not stop correctly if path removed
    """
    unix = './r_unix'
    receiver = SMSShell.receivers.unix.Receiver(config=dict(path=unix))
    assert receiver.start()
    # clean
    os.unlink(unix)
    assert not receiver.stop()

def test_simple_read_from_socket():
    """Open the socket and test read/write

    Use a separate thread to create socket client
    Use a queue to communicate between main thread and client thread
    """
    m_unix = './r_unix'
    m_data = 'ok'
    m_channel = queue.Queue()

    def writeToSocket(channel, unix, data):
        p = subprocess.Popen(shlex.split('./bin/sms-shell-client -i stdin -o unix -oa {}'.format(unix)),
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate(input=data.encode())
        channel.put((stdout, stderr, p.returncode))

    # init socket
    receiver = SMSShell.receivers.unix.Receiver(config=dict(path=m_unix))
    assert receiver.start()
    assert os.path.exists(m_unix)
    assert stat.S_ISSOCK(os.stat(m_unix).st_mode)
    # start client
    threading.Thread(target=writeToSocket, args=(m_channel, m_unix, m_data)).start()

    # fetch one data from one client
    client_context = next(receiver.read())
    with client_context as client_context_data:
        # ensure we had received what we sent
        assert m_data in client_context_data

    # ensure ack is valid
    stdout, stderr, returncode = m_channel.get()
    assert returncode == 0

    assert receiver.stop()
    assert not os.path.exists(m_unix)
