# pylint: disable=redefined-builtin
import os
import re
import sys
from crl.remotescript.baseengine import (
    BaseEngine, ExecutionError, SSHException,
    NonZeroExitStatusError, NoExitStatusError)
from crl.remotescript import pathops
from crl.remotescript.result import Result


__copyright__ = 'Copyright (C) 2019, Nokia'


class FPEngine(BaseEngine):

    SSH_CMD = 'ssh -2 -q -x -e none -oStrictHostKeyChecking=no \
        -oServerAliveInterval=10 -oServerAliveCountMax=3 -oUserKnownHostsFile=/dev/null'
    SCP_CMD = 'scp -2 -q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null'

    def __init__(self):
        BaseEngine.__init__(self)
        self.default_properties['node_tempdir'] = '/tmp/pdrobot-remotescript/node/' + self._temp_id + '/'

    def node_execute(self, node, command, target, exec_id, timeout):
        self._start_thread(exec_id, target, self._node_execute_impl,
                           [node, command, target, exec_id])
        return self._join_thread(exec_id, timeout)

    def node_execute_background(self, node, command, target, exec_id):
        self._start_thread(exec_id, target, self._node_execute_impl,
                           [node, command, target, exec_id])

    def _node_execute_impl(self, node, command, target, exec_id):
        command = self._wrap_node_command(command, node)
        return self._execute_impl(command, target, exec_id)

    def _wrap_node_command(self, command, node):
        if re.search("'", command):
            raise ExecutionError(
                'Command in Node keyword may not contain single quotes. \
                        Consider using double quotes or Node Script keyword: "' + command + '"')
        sunode = self._add_su_user(node)
        return FPEngine.SSH_CMD + " " + sunode + " '" + BaseEngine.CONNECTION_MONITOR_CMD + '; ' + command + "'"

    def _add_su_user(self, node):
        su_username = self._thread_local.connection.get_su_username()
        if su_username:
            return '%s@%s' % (su_username, node)
        return node

    def node_execute_script(self, node, file, target, exec_id, timeout):
        self._start_thread(exec_id, target, self._node_script_impl,
                           [node, file, target, exec_id])
        return self._join_thread(exec_id, timeout)

    def node_execute_script_background(self, node, file, target, exec_id):
        self._start_thread(exec_id, target, self._node_script_impl,
                           [node, file, target, exec_id])

    def _node_script_impl(self, node, file, target, exec_id):
        if not os.path.exists(file):
            raise IOError('File not found ' + file + ' (Working  directory: ' + os.getcwd() + ')')
        filename = os.path.basename(file)
        target_temp_dir = pathops.append(
            self._get_str_target_property(target, 'tempdir'), '-' + exec_id)
        target_temp_file = pathops.join(target_temp_dir, filename)
        node_temp_dir = pathops.append(
            self._get_str_target_property(target, 'node_tempdir'), '-' + exec_id)
        node_temp_file = pathops.join(node_temp_dir, filename)
        self._mkdir_impl(target_temp_dir, oct(0o777), target, exec_id)
        self._put_file_impl(file, target_temp_dir, oct(0o777), target, exec_id)
        sunode = self._add_su_user(node)
        command = FPEngine.SSH_CMD + ' ' + sunode + ' \'cd ' + node_temp_dir + '; chmod +x ' + node_temp_file + '; '
        command += BaseEngine.CONNECTION_MONITOR_CMD + '; ' + node_temp_file + "'"
        result = self._execute_impl(
            FPEngine.SSH_CMD + ' ' + sunode + ' "umask 0000; mkdir -p ' + node_temp_dir + '"', target, exec_id)
        if result.status != str(0):
            raise ExecutionError(
                'Creating temp dir "%s:%s" failed: %s' % (sunode, node_temp_dir, result))
        result = self._execute_impl(
            FPEngine.SCP_CMD + ' ' + target_temp_file + ' ' +
            sunode + ':' + node_temp_file, target, exec_id)
        if result.status != str(0):
            raise ExecutionError('Copying script to "%s:%s" failed: %s' % (sunode, node_temp_file, result))
        result = self._execute_impl(command, target, exec_id)
        if self._get_bool_target_property(target, 'cleanup'):
            try:
                self._execute_impl('rm -rf ' + target_temp_dir + '; ' +
                                   FPEngine.SSH_CMD + ' ' + sunode + ' rm -rf ' + node_temp_dir,
                                   target, exec_id)
            except (SSHException, NoExitStatusError, NonZeroExitStatusError):
                self._debug('Target "' + str(target) + ":" + node +
                            '" cleanup failed. ' + str(sys.exc_info()[1]))
        return result

    def node_put_file(self, node, source_file, destination_dir, mode, target, exec_id, timeout):
        self._start_thread(exec_id, target, self._node_put_file_impl,
                           [node, source_file, destination_dir, mode, target, exec_id])
        return self._join_thread(exec_id, timeout)

    def _node_put_file_impl(self, node, source_file, destination_dir, mode, target, exec_id):
        if not os.path.exists(source_file):
            raise IOError(''.join(['File not found: "', source_file, '" (cwd: ', os.getcwd(), ')']))
        filename = os.path.basename(source_file)
        target_temp_dir = pathops.append(self._get_str_target_property(target, 'tempdir'), '-' + exec_id)
        target_temp_file = pathops.join(target_temp_dir, filename)
        destination_file = pathops.join(destination_dir, filename)
        self._debug(''.join(['Copying localhost:', source_file, ' -> ', target, ':', target_temp_file,
                             ' -> ', target, ':', node, ':', destination_file]))
        self._mkdir_impl(target_temp_dir, oct(0o777), target, exec_id)
        self._put_file_impl(source_file, target_temp_dir, oct(0o777), target, exec_id)
        sunode = self._add_su_user(node)
        result = self._execute_impl(
            FPEngine.SSH_CMD + ' ' + sunode + ' "umask 0000; mkdir -p ' + destination_dir + '"', target, exec_id)
        if result.status != str(0):
            raise ExecutionError('Creating destination dir "%s:%s" failed: %s' % (sunode, destination_dir, result))
        result = self._execute_impl(
            FPEngine.SCP_CMD + ' ' + target_temp_file + ' ' + sunode + ':' + destination_file, target, exec_id)
        if result.status != str(0):
            raise ExecutionError('Copying file to "%s:%s" failed: %s' % (sunode, destination_file, result))
        result = self._execute_impl(
            FPEngine.SSH_CMD + ' ' + sunode + ' chmod ' + mode + ' ' + destination_file, target, exec_id)
        if result.status != str(0):
            raise ExecutionError('Setting mode %s on file "%s:%s" failed: %s' %
                                 (mode, sunode, destination_file, result))
        if self._get_bool_target_property(target, 'cleanup'):
            self._execute_impl('rm -rf ' + target_temp_dir, target, exec_id)
        return Result.SUCCESS

    def node_get_file(self, node, source_file, destination, target, exec_id, timeout):
        self._start_thread(exec_id, target, self._node_get_file_impl, [node, source_file, destination, target, exec_id])
        return self._join_thread(exec_id, timeout)

    def _node_get_file_impl(self, node, source_file, destination, target, exec_id):
        filename = os.path.basename(source_file)
        target_temp_dir = pathops.append(self._get_str_target_property(target, 'tempdir'), '-' + exec_id)
        target_temp_file = pathops.join(target_temp_dir, filename)
        self._debug(''.join(['Copying ', target, ':', node, ':', source_file,
                             ' -> ', target, ':', target_temp_file, ' -> localhost:', destination]))
        sunode = self._add_su_user(node)
        result = self._execute_impl(''.join(['umask 0000; mkdir -p ', target_temp_dir, '; ', FPEngine.SCP_CMD, ' ',
                                             sunode, ':', source_file, ' ', target_temp_file]), target, exec_id)
        if result.status != str(0):
            raise ExecutionError('Copying file from "%s:%s" node failed: %s' % (sunode, source_file, result))
        self._get_file_impl(target_temp_file, destination, target, exec_id)
        if self._get_bool_target_property(target, 'cleanup'):
            self._execute_impl('rm -rf ' + target_temp_dir, target, exec_id)
        return Result.SUCCESS
