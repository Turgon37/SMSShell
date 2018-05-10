# -*- coding: utf8 -*-

# This file is a part of SMSShell
#
# Copyright (c) 2016-2018 Pierre GINDRAUD
#
# SMSShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SMSShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SMSShell. If not, see <http://www.gnu.org/licenses/>.

"""
"""

__author__ = 'Pierre GINDRAUD'
__license__ = 'GPL-3.0'
__version__ = '1.0.0'
__maintainer__ = 'Pierre GINDRAUD'
__email__ = 'pgindraud@gmail.com'

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

    def __init__(self, daemon=False, log_level=None):
        """Constructor : Build the program lead object

        @param bool daemon if the server must be daemonized (False)
        @param str log_level the system minimum logging level for put log
        message
        """
        # config parser
        self.cp = MyConfigParser()
        self.__daemon = daemon

        # log parameters
        self.__log_level = log_level

        # List of callable to call on smsshell stop
        self.__stop_callbacks = []

    def load(self, config):
        """Load configuration function

        Use this function to load settings from given configuration file
        @param str config The path fo the configuration file
        @return boolean True if success, False otherwise
        """
        if config is not None:
            if self.cp.load(config):
                self.setLogLevel(self.__log_level if self.__log_level is not None else self.cp.getLogLevel())
                self.setLogTarget(self.cp.getLogTarget())
                return True
        return False

    def start(self, pid_path=None):
        """Run the service features

        Daemonize only if daemon is True in constructor
        @param str pid_path : pid file's path
        @return boolean True is start success, False otherwise
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
        self.__pid_path = pid_path
        # Create the pid file
        try:
            g_logger.debug("Creating PID file '%s'", self.__pid_path)
            pid_file = open(self.__pid_path, 'w')
            pid_file.write(str(os.getpid()) + '\n')
            pid_file.close()
        except IOError as e:
            g_logger.error("Unable to create PID file: %s", self.__pid_path)

        self.__downgrade()
        self.run()

        # Stop properly
        self.stop()

        return True


    def importAndCheckAbstract(self, module_path, class_name, abstract, config_section=None):
        """Import a sub module, instanciate a class and check object's instance

        @param str module_path the path to the module in the file system
        @param str class_name the name of the class to instanciate
        @param cls abstract the abstract class to check the instance for inheritance
        @param str config_section the name of the configuration section to load into
                    the instance
        """
        try:
            mod = importlib.import_module(module_path, package='SMSShell')
        except ImportError as e:
            raise ShellInitException("Unable to import the module {0}. Reason : {1}".format(module_path, str(e)))
        try: # instanciate
            cl = getattr(mod, class_name)
            if config_section and config_section in self.cp:
                inst = cl(self.cp[config_section])
            else:
                inst = cl()
        except AttributeError as e:
            raise ShellInitException("Error in module '{0}' : {1}.".format(module_path, str(e)))

        # handler class checking
        if not isinstance(inst, abstract):
            raise ShellInitException("Class '{0}' must extend AbstractCommand class".format(module_path))
        return inst

    def run(self):
        """This function do main applicatives stuffs
        """
        shell = Shell(self.cp)
        if self.cp.getMode() == 'STANDALONE':
            raise NotImplementedError('STANDALONE mode not yet implemented')
        else:
            # Init daemon mode
            try:
                parser = self.importAndCheckAbstract(
                    '.parsers.' + self.cp.get('daemon', 'message_parser', fallback="json"),
                    'Parser', AbstractParser, 'parser'
                )
                recv = self.importAndCheckAbstract(
                    '.receivers.' + self.cp.get('daemon', 'receiver_type', fallback="fifo"),
                    'Receiver', AbstractReceiver, 'receiver'
                )
                transv = self.importAndCheckAbstract(
                    '.transmitters.' + self.cp.get('daemon', 'transmitter_type', fallback="file"),
                    'Transmitter', AbstractTransmitter, 'transmitter'
                )
            except ShellInitException as e:
                g_logger.fatal("Unable to load an internal module : %s", str(e))
                return False
        if not recv.start():
            g_logger.fatal('Unable to open receiver')
            return False
        self.__stop_callbacks.append(recv.stop)
        if not transv.start():
            g_logger.fatal('Unable to open transmitter')
            return False
        for raw in recv.read():
            # parse received content
            try:
                msg = parser.parse(raw)
                transv.transmit(shell.exec(msg.sender, msg.getStr()))
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
        # Properly close some objects
        for c in self.__stop_callbacks:
            try:
                c()
            except NotImplementedError as e:
                g_logger.warning("Unable to close object of %s because of : %s", c.__self__.__class__, str(e))
        # Remove the pid file
        try:
            g_logger.debug("Remove PID file %s", self.__pid_path)
            os.remove(self.__pid_path)
        except OSError as e:
            g_logger.error("Unable to remove PID file: %s", str(e))

        g_logger.info("Exiting SMSShell")

        # Close log
        logging.shutdown()

    #
    # System running functions
    #

    def __sigTERM_handler(self, signum, frame):
        """Make the program terminate after receving system signal
        """
        g_logger.debug("Caught system signal %d", signum)
        self.stop()
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
        """
        # if g_logger.getEffectiveLevel() == value:
        #     return True

        try:
            g_logger.setLevel(value)
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
                g_logger.error("Unable to remove handler %s", str(type(handler)))

        hdlr.setFormatter(formatter)
        g_logger.addHandler(hdlr)
        # Sets the logging target.
        g_logger.info("Changed logging target to %s", target)
        return True
