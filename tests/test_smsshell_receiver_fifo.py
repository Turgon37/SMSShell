# -*- coding: utf8 -*-

import os
import pytest
import stat
import threading

import SMSShell
import SMSShell.receivers.fifo


def test_init():
    """Just start and stop the receiver
    """
    fifo = './r_fifo'
    receiver = SMSShell.receivers.fifo.Receiver(config=dict(path=fifo))
    assert receiver.start()
    assert os.path.exists(fifo)
    assert stat.S_ISFIFO(os.stat(fifo).st_mode)

    assert receiver.stop()
    assert not os.path.exists(fifo)

def test_bad_start_because_path_already_exists():
    """Ensure receiver do not start if path exists
    """
    fifo = './r_fifo'
    receiver = SMSShell.receivers.fifo.Receiver(config=dict(path=fifo))
    # create the path
    os.mkdir(fifo)
    assert os.path.exists(fifo)
    assert os.path.isdir(fifo)
    # test start for error
    assert not receiver.start()
    # clean
    os.rmdir(fifo)
    assert not os.path.exists(fifo)

def test_bad_start_because_path_not_writable():
    """Ensure receiver do not start correctly if path is not writable
    """
    fifo = '/root/r_fifo'
    receiver = SMSShell.receivers.fifo.Receiver(config=dict(path=fifo))
    assert not receiver.start()

def test_good_start_on_previous_fifo():
    """Ensure receiver start using previous fifo
    """
    fifo = './r_fifo'
    receiver = SMSShell.receivers.fifo.Receiver(config=dict(path=fifo))
    assert receiver.start()
    assert receiver.start()

def test_bad_stop_because_path_already_deleted():
    """Ensure receiver do not stop correctly if path removed
    """
    fifo = './r_fifo'
    receiver = SMSShell.receivers.fifo.Receiver(config=dict(path=fifo))
    assert receiver.start()
    # clean
    os.unlink(fifo)
    assert not receiver.stop()

def test_simple_read_from_fifo():
    """Open the fifo and test read/write

    Use a separate thread to create fifo client
    """
    fifo = './r_fifo'
    data = 'ok'

    def writeToFifo(data):
        # encode data
        with open(fifo, 'w') as path:
            path.write(data)

    # init socket
    receiver = SMSShell.receivers.fifo.Receiver(config=dict(path=fifo))
    assert receiver.start()
    assert os.path.exists(fifo)
    assert stat.S_ISFIFO(os.stat(fifo).st_mode)
    # start client
    threading.Thread(target=writeToFifo, args=(data, )).start()

    # fetch one data from one client
    client_context = next(receiver.read())
    with client_context as client_context_data:
        # ensure we had received what we sent
        assert data in client_context_data

    assert receiver.stop()
    assert not os.path.exists(fifo)
