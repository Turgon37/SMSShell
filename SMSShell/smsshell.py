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

"""This module contains the parent class of SMSShell programm
"""

__author__ = 'Pierre GINDRAUD'
__license__ = 'GPL-3.0'
__version__ = '1.0.0'
__maintainer__ = 'Pierre GINDRAUD'
__email__ = 'pgindraud@gmail.com'

# System imports
import importlib
import logging
import logging.handlers
import os
import signal
import sys

# Projet Imports
from .config import MyConfigParser
from .models import Message, SessionStates
from .receivers import AbstractReceiver
from .parsers import AbstractParser
from .transmitters import AbstractTransmitter
from .metrics import AbstractMetricsHelper
from .shell import Shell
from .exceptions import SMSShellException, SMSException, ShellException, ShellInitException

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

        self.__pid_path = None

        # log parameters
        self.__log_level = log_level

        # List of callable to call on smsshell stop
        self.__stop_callbacks = []

        # Internal reference to metrics handler
        self.__metrics = None

    def load(self, config_file):
        """Load configuration function

        Use this function to load settings from given configuration file
        @param str config The path fo the configuration file
        @return tuple (boolean, str) True if success, False otherwise
                                                and the status message
        """
        if config_file is None:
            return False, 'no file given'
        if not os.path.isfile(config_file):
            return False, 'the configuration file {} do not exists'.format(config_file)
        if not os.access(config_file, os.R_OK):
            return False, ('the configuration file {} is '
                           'not readable by the service').format(config_file)

        status, msg = self.cp.load(config_file)
        if status:
            self.setLogLevel(self.__log_level or self.cp.getLogLevel())
            self.setLogTarget(self.cp.get(self.cp.MAIN_SECTION, 'log_target', fallback='STDOUT'))
        return status, msg

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
            pid_path = self.cp.get(self.cp.MAIN_SECTION, 'pid', fallback='/var/run/smsshell.pid')
        self.__pid_path = pid_path

        # prevent program to run if the pidfile already exists
        if os.path.isfile(self.__pid_path):
            with open(self.__pid_path, 'r') as pid_file:
                current_pid = pid_file.read()
            if os.path.isdir('/proc/{}'.format(current_pid)):
                with open('/proc/{}/cmdline'.format(current_pid)) as cmdline:
                    current_cmdline_parts = cmdline.read().split('\0')

                if current_cmdline_parts:
                    current_cmdline = current_cmdline_parts[0]
                raise ShellInitException('pidfile exists and associated ' +
                                         'with running program {}'.format(current_cmdline))

        # Create the pid file
        try:
            g_logger.debug("Creating PID file '%s'", self.__pid_path)
            with open(self.__pid_path, 'w') as pid_file:
                pid_file.write(str(os.getpid()))
        except IOError:
            g_logger.error("Unable to create PID file: %s", self.__pid_path)

        # loose users privileges if needed
        self.__downgrade()

        # Init metrics handler
        try:
            metrics = self.importAndLoadModule(
                '.metrics.' + self.cp.get('daemon', 'metrics_handler', fallback='prometheus'),
                'MetricsHelper', AbstractMetricsHelper, 'metrics'
            )
        except ShellInitException as ex:
            g_logger.fatal("Unable to load metrics handler module : %s", str(ex))
            self.stop()
            return False

        if not metrics.start():
            g_logger.fatal('Unable to open metrics handler')
            self.stop()
            return False
        self.__metrics = metrics
        self.__stop_callbacks.append(metrics.stop)

        # run the fonctionnal endpoint
        if self.cp.getMode() == 'STANDALONE':
            # Init standalone mode
            raise NotImplementedError('STANDALONE mode not yet implemented')
        else:
            self.runDaemonMode()

        # Stop properly
        self.stop()

        return True


    def importAndLoadModule(self, module_path, class_name, abstract_class=None, config_section=None):
        """Import a sub module, instanciate a class and check object's instance

        @param str module_path the path to the module in the file system
        @param str class_name the name of the class to instanciate
        @param cls abstract the abstract class to check the instance for inheritance
        @param str config_section the name of the configuration section to load into
                    the instance
        """
        try:
            mod = importlib.import_module(module_path, package='SMSShell')
        except ImportError as ex:
            raise ShellInitException(("Unable to import the module '{0}',"
                                      " reason : {1}").format(module_path, str(ex)))
        try: # instanciate
            _class = getattr(mod, class_name)
            _class_args = dict(metrics=self.__metrics)
            # append config dict if exist in config file
            if config_section and config_section in self.cp:
                _class_args['config']=self.cp[config_section]
            inst = _class(**_class_args)
        except AttributeError as ex:
            raise ShellInitException("Error in module '{0}' : {1}.".format(module_path, str(ex)))

        # handler class checking
        if abstract_class and not isinstance(inst, abstract_class):
            raise ShellInitException(("Class '{0}' must extend "
                                      "AbstractCommand class").format(module_path))
        return inst

    def getTokensStoreFromConfig(self):
        """Build the authentication tokens store from config

        Returns:

        """
        tokens_store = dict()
        raw_tokens = self.cp.getModeConfig('tokens')
        if not raw_tokens:
            return tokens_store
        for raw_token in raw_tokens.split(','):
            # parse token string
            try:
                state, token = raw_token.split(':')
            except ValueError as ex:
                g_logger.error('Invalid token format, ' +
                               'it must be in the form ROLE:SECRET, it is ignored')
                continue

            # check if state exists
            try:
                real_state = SessionStates[state]
            except KeyError:
                g_logger.error('Invalid state value %s, ' +
                               'it must be one of the SessionStates available ones, ' +
                               'it is ignored',
                               str(state))
                continue
            g_logger.debug('loaded token length %d for state %s',
                           len(token),
                           str(real_state))
            if token not in tokens_store:
                tokens_store[token] = []
            if real_state in tokens_store[token]:
                g_logger.warning('duplicate authentication token for state %s',
                                 str(real_state))
            else:
                tokens_store[token].append(real_state)
        return tokens_store

    @staticmethod
    def extractRoleFromMessageAndStore(tokens_store, message):
        """

        Args:
            tokens_store : the dict of tokens and associated reachable
                            states
            message : the full message
        Returns:
            the SessionStates : if the given token is valid
            None : if no state was enforced or token was invalid
        """
        try:
            auth_attr = message.attribute('auth')
        except KeyError:
            return None

        assert isinstance(auth_attr, dict)
        if 'token' not in auth_attr or 'role' not in auth_attr:
            g_logger.warning("'auth' attribute in message require a token and a role")
            return None

        if auth_attr['token'] not in tokens_store:
            g_logger.error('The given token (length %d) is not registered in token store',
                           len(auth_attr['token']))
            return None

        reachable_states = tokens_store[auth_attr['token']]
        try:
            needed_state = SessionStates[auth_attr['role']]
        except KeyError:
            g_logger.error('Invalid state value %s, ' +
                           'it must be one of the SessionStates available ones, ' +
                           'it is ignored',
                           str(auth_attr['role']))
            return None
        if needed_state in reachable_states:
            return needed_state
        return None

    def runDaemonMode(self):
        """Entrypoint of daemon mode
        """
        shell = Shell(self.cp, self.__metrics)

        # Init daemon mode objects
        try:
            parser = self.importAndLoadModule(
                '.parsers.' + self.cp.get('daemon', 'message_parser', fallback="json"),
                'Parser', AbstractParser, 'parser'
            )
            recv = self.importAndLoadModule(
                '.receivers.' + self.cp.get('daemon', 'receiver_type', fallback="fifo"),
                'Receiver', AbstractReceiver, 'receiver'
            )
            transm = self.importAndLoadModule(
                '.transmitters.' + self.cp.get('daemon', 'transmitter_type', fallback="file"),
                'Transmitter', AbstractTransmitter, 'transmitter'
            )
        except ShellInitException as ex:
            g_logger.fatal("Unable to load an internal module : %s", str(ex))
            return False

        if not recv.start():
            g_logger.fatal('Unable to open receiver')
            return False
        # register the receiver close callback to properly close opened file descriptors
        self.__stop_callbacks.append(recv.stop)

        if not transm.start():
            g_logger.fatal('Unable to open transmitter')
            return False
        self.__stop_callbacks.append(transm.stop)

        g_logger.debug('initialize authentication tokens store')
        tokens_store = self.getTokensStoreFromConfig()
        g_logger.info('loaded %d authentication tokens in store', len(tokens_store))

        # init counters
        g_logger.debug('initialize metrics counters')
        self.__metrics.counter('messages.receive.total', value=0, description='Number of received messages')
        self.__metrics.counter('messages.receive.errors.total', value=0, description='Number of erroneous received messages')
        self.__metrics.counter('messages.transmit.total', value=0, description='Number of transmitted messages')
        self.__metrics.counter('messages.transmit.errors.total', value=0, description='Number of erroneous transmitted messages')

        # read and parse each message from receiver
        for client_context in recv.read():
            self.__metrics.counter('messages.receive.total')

            with client_context as client_context_data:
                # parse received content
                try:
                    msg = parser.parse(client_context_data)
                    client_context.appendTreatmentChain('parsed')
                except SMSException as ex:
                    self.__metrics.counter('messages.receive.errors.total')
                    g_logger.error('received a bad message, skipping because of %s', str(ex))
                    continue

                as_role = SMSShell.extractRoleFromMessageAndStore(tokens_store, msg)

                # run in shell
                try:
                    response_content = shell.exec(msg.sender, msg.asString(), as_role=as_role)
                    client_context.appendTreatmentChain('executed')
                except ShellException as ex:
                    g_logger.error('error during command execution : %s', ex.args[0])
                    if len(ex.args) > 1 and ex.args[1]:
                        ex_message = ex.args[1]
                    else:
                        ex_message = str(ex)
                    response_content = '#Err: {}'.format(ex_message)

                # forge the answer
                self.__metrics.counter('messages.transmit.total')
                try:
                    answer = Message(msg.sender, response_content)
                    transm.transmit(answer)
                    client_context.appendTreatmentChain('transmitted')
                except SMSException as ex:
                    self.__metrics.counter('messages.transmit.errors.total')
                    g_logger.error('error on emitting a message: %s', str(ex))
                    continue


    def stop(self):
        """Stop properly the server after signal received

        It is call by start() and signal handling functions
        It says to all thread to exit themself properly and run
        some system routine to terminate the entire program
        """
        # Properly close some objects
        for cb_stop in self.__stop_callbacks:
            try:
                cb_stop()
            except NotImplementedError as ex:
                g_logger.warning("Unable to close object of %s because of : %s",
                                 cb_stop.__self__.__class__,
                                 str(ex))
        # Remove the pid file
        try:
            g_logger.debug("Remove PID file %s", self.__pid_path)
            os.remove(self.__pid_path)
        except OSError as ex:
            g_logger.error("Unable to remove PID file: %s", str(ex))

        g_logger.info("Exiting SMSShell")

        # Close log
        logging.shutdown()

        return 0

    #
    # System running functions
    #

    def __sigTERM_handler(self, signum, frame):
        """Make the program terminate after receving system signal

        TODO : improve signal handling
        """
        g_logger.debug("Caught system signal %d", signum)
        sys.exit(self.stop())

    def __downgrade(self):
        """Downgrade daemon privilege to another uid/gid
        """
        gid = self.cp.getGid()
        if gid is not None:
            if os.getgid() == gid:
                g_logger.debug(("ignore setgid option because current "
                                "group is already to expected one %d"), gid)
            else:
                g_logger.debug("setting processus group to gid %d", gid)
                try:
                    os.setgid(gid)
                except PermissionError:
                    g_logger.fatal('Insufficient permissions to set process GID to %d', gid)
                    raise SMSShellException('Insufficient permissions to ' +
                                            'downgrade processus privileges')

        uid = self.cp.getUid()
        if uid is not None:
            if os.getuid() == uid:
                g_logger.debug(("ignore setuid option because current user "
                                "is already to expected one %d"), uid)
            else:
                g_logger.debug("setting processus user to uid %d", uid)
                try:
                    os.setuid(uid)
                except PermissionError:
                    g_logger.fatal('Insufficient permissions to set process UID to %d')
                    raise SMSShellException('Insufficient permissions to ' +
                                            'downgrade processus privileges')

    @staticmethod
    def __daemonize():
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
        except OSError as ex:
            return (ex.errno, ex.strerror)

        if pid == 0:  # The first child.
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
            except OSError as ex:
                return (ex.errno, ex.strerror)

            if pid == 0:  # The second child.
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
    @staticmethod
    def setLogLevel(value):
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
        # Syslog daemons already add date to the message.
        if target == 'SYSLOG':
            default_format = '%(name)s[%(process)d]: %(levelname)s %(message)s'
        # set a format which is simpler for console use
        else:
            default_format = '%(asctime)s %(name)-30s[%(process)d]: %(levelname)-7s %(message)s'
        formatter = logging.Formatter(self.cp.get(self.cp.MAIN_SECTION,
                                                  'log_format',
                                                  fallback=default_format))

        if target == 'SYSLOG':
            facility = logging.handlers.SysLogHandler.LOG_DAEMON
            hdlr = logging.handlers.SysLogHandler('/dev/log', facility=facility)
        elif target == 'STDOUT':
            hdlr = logging.StreamHandler(sys.stdout)
        elif target == 'STDERR':
            hdlr = logging.StreamHandler(sys.stderr)
        else:
            # Target should be a file
            try:
                with open(target, 'a'):
                    pass
                hdlr = logging.handlers.RotatingFileHandler(target)
            except IOError:
                g_logger.error("Unable to log to %s", target)
                return False

        # Remove all previous handlers
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
