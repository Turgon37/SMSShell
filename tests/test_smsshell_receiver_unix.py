# -*- coding: utf8 -*-

import json
import os
import pytest
import queue
import socket
import stat
import threading

import SMSShell
import SMSShell.receivers.unix

def test_init():
    """Just start and stop the receiver
    """
    unix = './r_unix'
    receiver = SMSShell.receivers.unix.Receiver(config=dict(path=unix))
    assert receiver.start()
    assert os.path.exists(unix)
    assert stat.S_ISSOCK(os.stat(unix).st_mode)

    assert receiver.stop()
    assert not os.path.exists(unix)

def test_bad_init_because_path_already_exists():
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

def test_simple_read_from_socket():
    """Open the socket and test read/write

    Use a separate thread to create socket client
    Use a queue to communicate between main thread and client thread
    """
    unix = './r_unix'
    data = 'ok'
    chan = queue.Queue()

    def writeToSocket(chan, data):
        # encode data
        if not isinstance(data, bytes):
            data = data.encode()
        # open socket to server
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_socket.connect(unix)
        # send data
        client_socket.sendall(data)
        # wait for ack
        recv = client_socket.recv(100)
        client_socket.close()
        # decode ack
        if not isinstance(recv, str):
            recv = recv.decode()
        # post ack to queue
        chan.put(recv)

    # init socket
    receiver = SMSShell.receivers.unix.Receiver(config=dict(path=unix))
    assert receiver.start()
    assert os.path.exists(unix)
    assert stat.S_ISSOCK(os.stat(unix).st_mode)
    # start client
    threading.Thread(target=writeToSocket, args=(chan, data)).start()

    # fetch one data from one client
    recv_data = next(receiver.read())
    # ensure we had received what we sent
    assert recv_data == data

    # ensure ack is valid
    ack = chan.get()
    jack = json.loads(ack)
    assert 'length' in jack
    assert jack['length'] == len(data)

    assert receiver.stop()
    assert not os.path.exists(unix)
