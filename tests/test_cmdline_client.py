# -*- coding: utf8 -*-

import queue
import os
import shlex
import stat
import subprocess
import threading

import SMSShell.receivers.fifo
import SMSShell.receivers.unix


# command line test
def test_cmdline_help():
    """Must produce an error is no url was given"""
    result = subprocess.Popen(shlex.split('./bin/sms-shell-client --help'), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert 'usage:' in stdout.decode()

def test_cmdline_version():
    result = subprocess.Popen(shlex.split('./bin/sms-shell-client --version'), stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert 'SMSShell client version' in stdout.decode()

def test_cmdline_without_arguments():
    result = subprocess.Popen(shlex.split('./bin/sms-shell-client'),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert result.returncode == 2

def test_cmdline_without_input_argument_arguments():
    """Test to write to a fifo
    """
    result = subprocess.Popen(shlex.split('./bin/sms-shell-client -i file'),
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    stdout, stderr = result.communicate()
    assert result.returncode == 2

def test_cmdline_write_fifo():
    """Test to write to a fifo
    """
    m_fifo = './fifo'
    m_data = 'ok'
    m_channel = queue.Queue()

    def writeToFifo(channel, fifo, data):
        p = subprocess.Popen(shlex.split('./bin/sms-shell-client -i stdin -o fifo -oa {}'.format(fifo)),
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate(input=data.encode())
        channel.put((stdout, stderr, p.returncode))

    # init socket
    receiver = SMSShell.receivers.fifo.Receiver(config=dict(path=m_fifo))
    assert receiver.start()
    assert os.path.exists(m_fifo)
    assert stat.S_ISFIFO(os.stat(m_fifo).st_mode)

    # start client
    threading.Thread(target=writeToFifo, args=(m_channel, m_fifo, m_data)).start()

    client_context = next(receiver.read())
    with client_context as client_context_data:
        # ensure we had received what we sent
        assert m_data in client_context_data

    # assert client
    stdout, stderr, returncode = m_channel.get()
    assert returncode == 0
    # clean
    assert receiver.stop()
    assert not os.path.exists(m_fifo)

def test_cmdline_write_fifo_with_os_error():
    """Test to write to a fifo
    """
    m_fifo = '/nonexistentfolder/fifo'
    m_data = 'ok'
    result = subprocess.Popen(shlex.split('./bin/sms-shell-client -i stdin -o fifo -oa {}'.format(m_fifo)),
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE)
    stdout, stderr = result.communicate(input=m_data.encode())
    assert result.returncode == 1

def test_cmdline_write_unix():
    """Test to write to an unix socket
    """
    m_unix = './unix'
    m_data = 'ok'
    m_channel = queue.Queue()

    def writeToUnix(queue, unix, data):
        p = subprocess.Popen(shlex.split('./bin/sms-shell-client -i stdin -o unix -oa {}'.format(unix)),
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)

        (stdout, stderr) = p.communicate(input=data.encode())
        queue.put((stdout, stderr, p.returncode))

    # init socket
    receiver = SMSShell.receivers.unix.Receiver(config=dict(path=m_unix))
    assert receiver.start()
    assert os.path.exists(m_unix)
    assert stat.S_ISSOCK(os.stat(m_unix).st_mode)

    # start client
    threading.Thread(target=writeToUnix, args=(m_channel, m_unix, m_data)).start()

    # fetch one data from one client
    client_context = next(receiver.read())
    with client_context as client_context_data:
        # ensure we had received what we sent
        assert m_data in client_context_data

    # assert client
    stdout, stderr, returncode = m_channel.get()
    assert returncode == 0
    # clean
    assert receiver.stop()
    assert not os.path.exists(m_unix)
