# -*- coding: utf8 -*-

# This file is a part of SMSShell
#
# Copyright (c) 2016-2017 Pierre GINDRAUD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
"""

# System imports
import configparser
import datetime
import importlib
import logging
import logging.handlers
import os
import signal
import socket
import sys
import time

# Projet Imports
try:
    from .config import MyConfigParser
    from .receivers import AbstractReceiver
    from .parsers import AbstractParser
    from .transmitters import AbstractTransmitter
    from .shell import Shell
    from .exceptions import SMSException,ShellException,ShellInitException
except Exception as e:
    import traceback
    traceback.print_exc(file=sys.stdout)
    print(str(e), file=sys.stderr)
    print("A project's module failed to be import", file=sys.stderr)
    sys.exit(1)

# Global project declarations
g_logger = logging.getLogger('smsshell')


class SMSShell(object):
    """SMSShell main class
    """

    def __init__(self, daemon=False, log_level='INFO'):
        """Constructor : Build the program lead object

        @param daemon [bool] : if the server must be daemonized (False)
        @param log_level [str] : the system minimum logging level for put log
        message
        """
        # config parser
        self.cp = MyConfigParser()
        self.__daemon = daemon

        # log parameters
        self.__log_level = None
        self.__log_target = None

    def load(self, config):
        """Load configuration function

        Use this function to load settings from given configuration file
        @param[string] config : The path fo the configuration file
        @return[boolean] : True if success
        False otherwise
        """
        if config is not None:
            if self.cp.load(config):
                self.setLogLevel(self.cp.getLogLevel())
                self.setLogTarget(self.cp.getLogTarget())
                return True
        return False

    def start(self, pid_path=None):
        """Run the service features

        Daemonize if daemon is True in constructor
        @param[string] pid_path : pid file's path
        @return[boolean] : True is start success
        False otherwise
        """
        # Restreint access to only owner
        os.umask(0o0077)

        # Installing signal catching function
        signal.signal(signal.SIGTERM, self.__sigTERM_handler)
        signal.signal(signal.SIGINT, self.__sigTERM_handler)

        # Load configuration
        if not self.cp.isLoaded():
            return False

        # Turn in daemon mode
        if self.__daemon:
            g_logger.debug('Starting in daemon mode')
            if self.__daemonize():
                g_logger.info('Daemon started')
            else:
                g_logger.fatal('Could not create daemon')
                raise Exception('Could not create daemon')

        # Check pidfile
        if pid_path is None:
            pid_path = self.cp.getPidPath()
        # Create the pid file
        try:
            g_logger.debug("Creating PID file '%s'", pid_path)
            pid_file = open(pid_path, 'w')
            pid_file.write(str(os.getpid()) + '\n')
            pid_file.close()
        except IOError as e:
            g_logger.error("Unable to create PID file: %s", pid_path)

        self.__downgrade()
        self.run()

        # Stop properly
        self.stop()

        # Remove the pid file
        try:
            g_logger.debug("Remove PID file %s", pid_path)
            os.remove(pid_path)
        except OSError as e:
            g_logger.error("Unable to remove PID file: %s", e)

        g_logger.info("Exiting SMSShell")
        return True


    def importAndCheck(self, module_path, class_name, abstract):
        """Import a sub module, instanciate a class and check object's instance

        @param
        """
        try:
            mod = importlib.import_module(module_path, package='SMSShell')
        except ImportError as e:
            raise ShellInitException("Unable to import the module {0}. Reason : {1}".format(module_path, str(e)))
        try: # instanciate
            cl = getattr(mod, class_name)
            inst = cl(self.cp)
        except AttributeError as e:
            raise ShellInitException("Error in module '{0}' : {1}.".format(module_path, str(e)))

        # handler class checking
        if not isinstance(inst, abstract):
            raise ShellInitException("Class '{0}' must extend AbstractCommand class".format(module_path))
        return inst

    def run(self):
        """This function is responsible of applicative works
        """
        shell = Shell(self.cp)

        if self.cp.getMode() == 'ONESHOT':
            raise NotImplementedError('oneshot mode not yet implemented')
        else:
            # Init standalone mode
            try:
                parser = self.importAndCheck(
                    '.parsers.' + self.cp.get('standalone', 'msg_parser', fallback="json"),
                    'Parser', AbstractParser
                )
                recv = self.importAndCheck(
                    '.receivers.' + self.cp.get('standalone', 'input_type', fallback="fifo"),
                    'Receiver', AbstractReceiver
                )
                tran = self.importAndCheck(
                    '.transmitters.' + self.cp.get('standalone', 'output_type', fallback="file"),
                    'Transmitter', AbstractTransmitter
                )
            except ShellInitException as e:
                g_logger.fatal("Unable to load an internal module : %s", str(e))
                return False
        if not recv.start():
            g_logger.fatal('Unable to open receiver')
            return False
        if not tran.start():
            g_logger.fatal('Unable to open transmitter')
            return False
        for raw in recv.read():
            # parse received content
            try:
                msg = parser.parse(raw)
                tran.transmit(shell.run(msg.sender, msg.getArgv()))
            except SMSException as em:
                g_logger.error("received a bad message, skipping")
                continue
            except ShellException as es:
                g_logger.error("error during command execution : " + str(es))
                print(es.short_message)
                continue

    def stop(self):
        """Stop properly the server after signal received

        It is call by start() and signal handling functions
        It says to all thread to exit themself properly and run
        some system routine to terminate the entire program
        """
        # Close log
        logging.shutdown()

    #
    # System running functions
    #

    def __sigTERM_handler(self, signum, frame):
        """Make the program terminate after receving system signal
        """
        g_logger.debug("Caught system signal %d", signum)
        sys.exit(1)

    def __downgrade(self):
        """Downgrade daemon privilege to another uid/gid
        """
        uid = self.cp.getUid()
        gid = self.cp.getGid()

        try:
            if gid is not None:
                g_logger.debug("Setting processus group to gid %d", gid)
                os.setgid(gid)
            if uid is not None:
                g_logger.debug("Setting processus user to uid %d", uid)
                os.setuid(uid)
        except PermissionError:
            g_logger.error('Insufficient privileges to set process id')

    def __daemonize(self):
        """Turn the service as a deamon

        Detach a process from the controlling terminal
        and run it in the background as a daemon.
        See : http://code.activestate.com/recipes/278731/
        """
        try:
            # Fork a child process so the parent can exit.  This returns control to
            # the command-line or shell.  It also guarantees that the child will not
            # be a process group leader, since the child receives a new process ID
            # and inherits the parent's process group ID.  This step is required
            # to insure that the next call to os.setsid is successful.
            pid = os.fork()
        except OSError as e:
            return ((e.errno, e.strerror))

        if (pid == 0):  # The first child.
            # To become the session leader of this new session and the process group
            # leader of the new process group, we call os.setsid().  The process is
            # also guaranteed not to have a controlling terminal.
            os.setsid()

            # Is ignoring SIGHUP necessary?
            #
            # It's often suggested that the SIGHUP signal should be ignored before
            # the second fork to avoid premature termination of the process.  The
            # reason is that when the first child terminates, all processes, e.g.
            # the second child, in the orphaned group will be sent a SIGHUP.
            #
            # "However, as part of the session management system, there are exactly
            # two cases where SIGHUP is sent on the death of a process:
            #
            #   1) When the process that dies is the session leader of a session that
            #      is attached to a terminal device, SIGHUP is sent to all processes
            #      in the foreground process group of that terminal device.
            #   2) When the death of a process causes a process group to become
            #      orphaned, and one or more processes in the orphaned group are
            #      stopped, then SIGHUP and SIGCONT are sent to all members of the
            #      orphaned group." [2]
            #
            # The first case can be ignored since the child is guaranteed not to have
            # a controlling terminal.  The second case isn't so easy to dismiss.
            # The process group is orphaned when the first child terminates and
            # POSIX.1 requires that every STOPPED process in an orphaned process
            # group be sent a SIGHUP signal followed by a SIGCONT signal.  Since the
            # second child is not STOPPED though, we can safely forego ignoring the
            # SIGHUP signal.  In any case, there are no ill-effects if it is ignored.
            #
            # import signal           # Set handlers for asynchronous events.
            # signal.signal(signal.SIGHUP, signal.SIG_IGN)

            try:
                # Fork a second child and exit immediately to prevent zombies.  This
                # causes the second child process to be orphaned, making the init
                # process responsible for its cleanup.  And, since the first child is
                # a session leader without a controlling terminal, it's possible for
                # it to acquire one by opening a terminal in the future (System V-
                # based systems).  This second fork guarantees that the child is no
                # longer a session leader, preventing the daemon from ever acquiring
                # a controlling terminal.
                pid = os.fork()  # Fork a second child.
            except OSError as e:
                return ((e.errno, e.strerror))

            if (pid == 0):  # The second child.
                # Since the current working directory may be a mounted filesystem, we
                # avoid the issue of not being able to unmount the filesystem at
                # shutdown time by changing it to the root directory.
                os.chdir("/")
            else:
                # exit() or _exit()?  See below.
                os._exit(0)  # Exit parent (the first child) of the second child.
        else:
            # exit() or _exit()?
            # _exit is like exit(), but it doesn't call any functions registered
            # with atexit (and on_exit) or any registered signal handlers.  It also
            # closes any open file descriptors.  Using exit() may cause all stdio
            # streams to be flushed twice and any temporary files may be unexpectedly
            # removed.  It's therefore recommended that child branches of a fork()
            # and the parent branch(es) of a daemon use _exit().
            os._exit(0)  # Exit parent of the first child.
        return True

    #
    # Logging functions
    #
    def setLogLevel(self, value):
        """Set the logging level.

        @param value CONSTANT : the log level according to syslog
            CRITICAL
            ERROR
            WARNING
            NOTICE
            INFO
            DEBUG
        @return [bool] : True if set success
        False otherwise
        """
        if self.__log_level == value:
            return True

        try:
            g_logger.setLevel(value)
            self.__log_level = value
            g_logger.info("Changed logging level to %s", value)
            return True
        except AttributeError:
            raise ValueError("Invalid log level")

    def setLogTarget(self, target):
        """Sets the logging target

        target can be a file, SYSLOG, STDOUT or STDERR.
        @param target [str] : the logging target
            STDOUT
            SYSLOG
            STDERR
            a file path
        @return [bool] : True if set success
        False otherwise Set the log target of the logging system
        """
        if self.__log_target == target:
            return True

        # set a format which is simpler for console use
        formatter = logging.Formatter(
            "%(asctime)s %(name)-30s[%(process)d]: %(levelname)-7s %(message)s")
        if target == "SYSLOG":
            # Syslog daemons already add date to the message.
            formatter = logging.Formatter(
                "%(name)s[%(process)d]: %(levelname)s %(message)s")
            facility = logging.handlers.SysLogHandler.LOG_DAEMON
            hdlr = logging.handlers.SysLogHandler("/dev/log", facility=facility)
        elif target == "STDOUT":
            hdlr = logging.StreamHandler(sys.stdout)
        elif target == "STDERR":
            hdlr = logging.StreamHandler(sys.stderr)
        else:
            # Target should be a file
            try:
                open(target, "a").close()
                hdlr = logging.handlers.RotatingFileHandler(target)
            except IOError:
                g_logger.error("Unable to log to " + target)
                return False

        # Remove all handler
        for handler in g_logger.handlers:
            try:
                g_logger.removeHandler(handler)
            except (ValueError, KeyError):
                g_logger.warn("Unable to remove handler %s", str(type(handler)))

        hdlr.setFormatter(formatter)
        g_logger.addHandler(hdlr)
        # Sets the logging target.
        self.__log_target = target
        g_logger.info("Changed logging target to %s", target)
        return True
