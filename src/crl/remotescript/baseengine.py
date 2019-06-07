# pylint: disable=unused-argument,protected-access
# pylint: disable=redefined-builtin
import os
import random
import sys
import threading
import time
import traceback
from logging import debug, error
from crl.remotescript import pathops
from crl.remotescript import connectionmediator
from crl.remotescript.result import Result
from robot.libraries.BuiltIn import BuiltIn


__copyright__ = 'Copyright (C) 2019, Nokia'


class NoExitStatusError(Exception):
    pass


class NonZeroExitStatusError(Exception):
    pass


class ExecutionError(Exception):
    pass


class TimeoutError(ExecutionError):
    pass


class SSHException(Exception):
    pass


class _ExecutionRunner(threading.Thread):
    def __init__(self, targets, command, args, lib):
        threading.Thread.__init__(self)
        if isinstance(targets, list):
            self.targets = targets
        else:
            self.targets = [targets]
        self.command = command
        self.args = args
        self.lib = lib
        self.result = None
        self.messages = None
        self.error = None
        self.trace = None
        self.connections = list()
        self.interrupted = False

    def run(self):
        try:
            self.lib._thread_local.connection = None
            self.lib._thread_local.connections = list()
            self.lib._thread_local.transaction_level = 0
            self.lib._thread_local.messages = list()
            if self.lib._start_transaction(self.targets):
                try:
                    if not self.interrupted:
                        self.result = self.command(*self.args)
                    else:
                        self.result = Result.CONNECTION_FAILURE
                finally:
                    self.lib._stop_transaction()
            else:
                self.result = Result.CONNECTION_FAILURE
            self.messages = self.lib._thread_local.messages
        except Exception:  # pylint: disable=broad-except; noqa: W0703
            self.error = sys.exc_info()[1]
            self.trace = sys.exc_info()
            self.messages = self.lib._thread_local.messages

    def interrupt(self):
        self.interrupted = True
        for con in self.connections:
            con.close_connection()
        self.connections = list()


class BaseEngine(object):
    CONNECTION_MONITOR_CMD = '( while :; do if ! kill -0 $PPID &>/dev/null; \
            then /bin/kill -s HUP -$$; break; fi; if ! kill -0 $$ &>/dev/null; \
            then break; fi; usleep 100 &>/dev/null || sleep 1; done & )'

    def __init__(self):
        self._temp_id = str(random.randint(100000000, 999999999))
        self.targets = dict()  # <name, Target>
        self._threads = dict()  # <connection alias, thread>
        self._main_thread = threading.currentThread()
        # contains SSH or Telnet connectionmediator instance and transaction_level
        self._thread_local = threading.local()
        self.default_properties = {
            'cleanup': True,
            'connection break is error': True,
            'connection failure is error': True,
            'login prompt': 'login: ',
            'login timeout': 60,
            'max connection attempts': 10,
            'nonzero status is error': False,
            'password prompt': 'Password: ',
            'port': None,
            'prompt is regexp': False,
            'prompt': '$ ',
            'tempdir': '/tmp/pdrobot-remotescript/' + self._temp_id,
            'su username': None,
            'su password': None,
            'use sudo user': False
        }

    def set_target_property(self, target_name, property_name, property_value):
        self._check_target(target_name)
        self.targets[target_name].properties[property_name] = property_value

    def get_target_properties(self, target):
        self._check_target(target)
        properties = dict()
        properties.update(self.default_properties)
        properties.update(self.targets[target].properties)
        return properties

    def _check_target(self, target):
        if target not in self.targets:
            raise ValueError('Unknown target: "' + target +
                             '" Make sure you have added the target with "Set Target" keyword')

    def _check_targets(self, targets):
        for target in targets:
            self._check_target(target)

    def _get_target_property(self, target, property_name, default_value=None):
        """
        Retrieves target property.

        *Arguments:*\n
        _target_name_ Name of the individual target, whose property to get.\n
        _property_name_ Name of the property.\n

        *Returns:*\n
        Property _property_name_ for target _target_name_. If
        the property has not been set for _target_name_ then default
        property value is returned. ValueError is thrown if no default
        value has been set.
        """
        self._check_target(target)
        value = self.targets[target].properties.get(property_name)
        if value is None:
            value = self.default_properties.get(property_name)
        if value is None:
            value = default_value
        if value is None:
            raise ValueError('Unknown property key: "' + property_name + '"')
        return value

    def _get_bool_target_property(self, target, property_name, default_value=None):
        return BuiltIn().convert_to_boolean(self._get_target_property(
            target, property_name, default_value))

    def _get_int_target_property(self, target, property_name, default_value=None):
        return BuiltIn().convert_to_number(self._get_target_property(
            target, property_name, default_value))

    def _get_str_target_property(self, target, property_name, default_value=None):
        return str(self._get_target_property(target, property_name, default_value))

    def execute(self, command, target, exec_id, timeout):
        self._start_thread(exec_id, target, self._execute_impl, [command, target, exec_id, True])
        return self._join_thread(exec_id, timeout)

    def execute_background(self, command, target, exec_id):
        self._start_thread(exec_id, target, self._execute_impl, [command, target, exec_id, True])

    def wait_background(self, exec_id, timeout):
        return self._join_thread(exec_id, timeout)

    def kill_background(self, exec_id):
        if self._threads[exec_id].is_alive():
            self._threads[exec_id].interrupt()

    def _execute_impl(self, command, target, exec_id, check_su=False):
        status = Result.UNKNOWN_STATUS
        out = ""
        err = ""
        end = Result.CLOSE_FAIL
        try:
            if check_su:
                command = self._thread_local.connection.get_su_command(command)
            self._debug('Executing command "' + command + '"')
            (status, out, err) = self._thread_local.connection.execute_command(
                BaseEngine.CONNECTION_MONITOR_CMD + '; ' + command)  # Here's the beef
            out = out.strip()
            err = err.strip()
        except SSHException:
            self._debug("Connecttion closed unexpectedly")
            if self._get_bool_target_property(target, 'connection break is error'):
                raise
        if status == Result.UNKNOWN_STATUS:
            if self._get_bool_target_property(target, 'connection break is error'):
                msg = 'Command execution failure, did not get exit status'
                msg += ', stdout="' + pathops.unic(out) + '"'
                msg += ', stderr="' + pathops.unic(err) + '"'
                raise NoExitStatusError(msg)
        else:
            end = Result.CLOSE_OK
        if self._get_bool_target_property(target, 'nonzero status is error') and status != '0':
            msg = 'status="' + status + '"'
            msg += ', stdout="' + pathops.unic(out) + '"'
            msg += ', stderr="' + pathops.unic(err) + '"'
            raise NonZeroExitStatusError(msg)
        return Result(status, out, err, Result.OPEN_OK, end)

    def execute_script(self, file, target, exec_id, timeout, arguments):
        self._start_thread(exec_id, target, self._execute_script_impl,
                           [file, target, exec_id, arguments])
        return self._join_thread(exec_id, timeout)

    def execute_script_background(self, file, target, exec_id):
        self._start_thread(exec_id, target, self._execute_script_impl,
                           [file, target, exec_id])

    def _execute_script_impl(self, script_file, target, exec_id, arguments=None):
        if arguments is None:
            arguments = []
        if not os.path.exists(script_file):
            raise IOError('File not found ' + script_file + ' (Working  directory: ' + os.getcwd() + ')')
        filename = os.path.basename(script_file)
        target_temp_dir = pathops.append(self._get_str_target_property(target, 'tempdir'), '-' + exec_id)
        target_temp_dir = pathops.directorize(target_temp_dir)
        target_temp_file = pathops.join(target_temp_dir, filename)
        self._debug('Copying ' + script_file + ' to ' + target + ':' + target_temp_dir)
        self._mkdir_impl(target_temp_dir, oct(0o777), target, exec_id)
        self._put_file_impl(script_file, target_temp_dir, oct(0o777), target, exec_id)
        command = self._thread_local.connection.get_su_command(
            target_temp_file) + " " + " ".join(arguments)
        result = self._execute_impl(
            "cd " + target_temp_dir + "; chmod +x " + target_temp_file +
            "; " + command, target, exec_id)
        if self._get_bool_target_property(target, 'cleanup'):
            try:
                self._execute_impl('rm -rf ' + target_temp_dir, target, exec_id)
            except (NoExitStatusError, NonZeroExitStatusError):
                self._debug('Target "' + str(target) + '" cleanup failed. ' + str(sys.exc_info()[1]))
        return result

    def copy_file(self, from_target, source_file, to_target, destination_dir, mode, exec_id, timeout):
        self._start_thread(exec_id, [from_target, to_target], self._copy_file_impl,
                           [from_target, source_file, to_target, destination_dir, mode, exec_id])
        return self._join_thread(exec_id, timeout)

    def _copy_file_impl(self, from_target, source_file, to_target, destination_dir, mode, exec_id):
        destination_dir = pathops.directorize(destination_dir)
        self._debug(''.join(
            ['Copying file from target "', from_target, ':', source_file,
             '" to "', to_target, ':', destination_dir, '"']))
        self._thread_local.connections[0].copy_file(self._thread_local.connections[1],
                                                    source_file, destination_dir, mode)
        return Result.SUCCESS

    def put_file(self, source_file, destination_dir, mode, target, exec_id, timeout):
        self._start_thread(exec_id, target, self._put_file_impl,
                           [source_file, destination_dir, mode, target, exec_id])
        return self._join_thread(exec_id, timeout)

    def _put_file_impl(self, source_file, destination_dir, mode, target, exec_id):
        destination_dir = pathops.directorize(destination_dir)
        self._debug(''.join(
            ['Copying file "', source_file, '" to target "', target,
             ':', destination_dir, '" (cwd: ', os.getcwd(), ')']))
        self._thread_local.connection.put_file(source_file, destination_dir, mode)
        return Result.SUCCESS

    def get_file(self, source_file, destination, target, exec_id, timeout):
        self._start_thread(exec_id, target, self._get_file_impl,
                           [source_file, destination, target, exec_id])
        return self._join_thread(exec_id, timeout)

    def _get_file_impl(self, source_file, destination, target, exec_id):
        self._debug(''.join(
            ['Copying file from target "', target, ':', source_file, '" to "',
             destination, '" (cwd: ', os.getcwd(), ')']))
        self._thread_local.connection.get_file(source_file, destination)
        return Result.SUCCESS

    def put_dir(self, source_dir, target_dir, mode, target, exec_id, timeout):
        self._start_thread(exec_id, target, self._put_dir_impl,
                           [source_dir, target_dir, mode, target, exec_id])
        return self._join_thread(exec_id, timeout)

    def _put_dir_impl(self, source_dir, target_dir, mode, target, exec_id):
        self._mkdir_impl(target_dir, mode, target, exec_id)
        for root, dirs, files in os.walk(source_dir):
            current_target_dir = os.path.join(target_dir,
                                              root[len(source_dir):].lstrip(os.sep)) + os.sep
            for f in files:
                self._put_file_impl(os.path.join(root, f),
                                    current_target_dir, mode, target, exec_id)
            for d in dirs:
                self._mkdir_impl(os.path.join(current_target_dir, d),
                                 mode, target, exec_id)
                self._debug("Created directory " + os.path.join(current_target_dir, d))
        return Result.SUCCESS

    def mkdir(self, path, mode, target, exec_id, timeout):
        self._start_thread(exec_id, target, self._mkdir_impl, [path, mode, target, exec_id])
        return self._join_thread(exec_id, timeout)

    def _mkdir_impl(self, path, mode, target, exec_id):
        self._debug('Creating directory ' + target + ':' + path)
        self._thread_local.connection.mkdir(path, mode)
        return Result.SUCCESS

    def rmdir(self, path, target, exec_id, timeout):
        self._start_thread(exec_id, target, self._rmdir_impl, [path, target, exec_id])
        return self._join_thread(exec_id, timeout)

    def _rmdir_impl(self, path, target, exec_id):
        self._debug('Removing directory ' + target + ':' + path)
        self._thread_local.connection.rmdir(path)
        return Result.SUCCESS

    def _start_thread(self, exec_id, targets, command, args):
        exec_id = str(exec_id)
        if self._threads.get(exec_id):
            raise ExecutionError('Execution with ID "' + exec_id + '" is already running')
        self._threads[exec_id] = _ExecutionRunner(targets, command, args, self)
        self._threads[exec_id].start()

    def _join_thread(self, exec_id, timeout=None):
        try:
            exec_id = str(exec_id)
            if timeout:
                timeout = float(timeout)
            if not self._threads.get(exec_id):
                raise ExecutionError('There is no execution with ID "' + exec_id + '"')
            timed_out = False
            self._threads[exec_id].join(timeout)
            if self._threads[exec_id].is_alive():
                timed_out = True
                self._threads[exec_id].interrupt()
                self._threads[exec_id].join(5)
                if self._threads[exec_id].is_alive():
                    raise TimeoutError(
                        'Execution ID "' + exec_id + '" timed out: failed to interrupt running thread')
            result = self._threads[exec_id].result
            if self._threads[exec_id].messages:
                for m in self._threads[exec_id].messages:
                    debug(m)
            if not result:
                error('\n' + ''.join(traceback.format_exception(self._threads[exec_id].trace[0],
                                                                self._threads[exec_id].trace[1],
                                                                self._threads[exec_id].trace[2])))
                if not timed_out:
                    raise self._threads[exec_id].error
            if timed_out:
                if result:
                    debug('Result:' + str(result))
                raise TimeoutError('Execution ID "' + exec_id + '" timed out')
            return result
        finally:
            self._threads[exec_id] = None

    def _start_transaction(self, targets):
        self._check_targets(targets)
        if self._thread_local.transaction_level == 0:
            for target in targets:
                try:
                    self.__connect(target)
                    self._debug('Connection opened to target "' + target + '"')
                except (ValueError, SSHException, IOError):
                    self.__disconnect()
                    if self._get_bool_target_property(target, 'connection failure is error'):
                        raise
                    return False

        self._thread_local.transaction_level += 1
        return True

    def _stop_transaction(self):
        self._thread_local.transaction_level -= 1
        if self._thread_local.transaction_level < 1:
            self.__disconnect()
            self._debug('Connection closed')

    def __connect(self, target_name):
        connection_attempts = 0
        connection = None
        while not connection:
            try:
                connection = self.__create_new_connection(target_name)
                break
            except (ValueError, SSHException, IOError):
                connection_attempts += 1
                if connection_attempts < self._get_int_target_property(target_name, 'max connection attempts'):
                    self._debug(
                        'Opening connection to "' + str(self.targets[target_name]) + '" failed.' + str(
                            sys.exc_info()[1]))
                    self._debug('Trying to reconnect in 5 seconds')
                    time.sleep(5)
                else:
                    self._debug('Failed to open connection. Maximum connection attempt count (' +
                                self._get_str_target_property(target_name, 'max connection attempts') +
                                ') exceeded')
                    raise
        # All but one keyword uses only one connection,
        # thus also easy access without list
        self._thread_local.connection = connection
        self._thread_local.connections.append(connection)
        # Purpose of this is that we can call connection.close()
        # from main thread when executing thread is blocked in
        # connection.read_command_output()
        threading.currentThread().connections.append(connection)

    def __disconnect(self):
        for con in self._thread_local.connections:
            con.close_connection()
        self._thread_local.transaction_level = 0
        self._thread_local.connections = list()
        self._thread_local.connection = None

    def __create_new_connection(self, target_name):
        target = self.targets[target_name]
        connection = None
        if target.protocol in ['ssh/sftp', 'ssh']:
            connection = connectionmediator.SSH()
            default_port = 22
        elif target.protocol == 'ssh/scp':
            connection = connectionmediator.SSH_SCP()
            default_port = 22
        elif target.protocol == 'telnet':
            connection = connectionmediator.Telnet()
            default_port = 23
        elif target.protocol == 'ftp':
            connection = connectionmediator.FTP()
            default_port = 21
        else:
            raise ValueError('Unsupported protocol ' + target.protocol)

        connection.open_connection(target.host,
                                   port=self._get_str_target_property(target_name, 'port', default_port),
                                   timeout=self._get_str_target_property(target_name, 'login timeout'),
                                   prompt=self._get_str_target_property(target_name, 'prompt'),
                                   prompt_is_regexp=self._get_bool_target_property(target_name, 'prompt is regexp'))

        if target.protocol in ['ssh/sftp', 'ssh', 'ssh/scp'] and target.sshkeyfile is not None:
            connection.login_with_key(target.username, target.sshkeyfile)
        else:
            connection.login(target.username,
                             target.password,
                             self._get_str_target_property(target_name, 'login prompt'),
                             self._get_str_target_property(target_name, 'password prompt'))
        props = self.get_target_properties(target_name)
        su_username = props.get('su username')
        su_password = props.get('su password')
        if su_username:
            if su_password:
                connection.set_su_user(str(su_username), str(su_password))
            else:
                connection.set_su_user(str(su_username))
        self._set_use_sudo_user_if_needed(props, connection)
        return connection

    @staticmethod
    def _set_use_sudo_user_if_needed(props, connection):
        if props.get('use sudo user'):
            connection.set_use_sudo_user()

    def _debug(self, message):
        msg = threading.currentThread().getName() + ' ' + message
        if threading.currentThread() == self._main_thread:
            debug(msg)
        else:
            self._thread_local.messages.append(msg)
