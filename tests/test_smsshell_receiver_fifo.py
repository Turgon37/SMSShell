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

def test_bad_init_because_path_already_exists():
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
    recv_data = next(receiver.read())
    # ensure we had received what we sent
    assert recv_data == data

    assert receiver.stop()
    assert not os.path.exists(fifo)
