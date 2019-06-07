# pylint: disable=redefined-builtin
from crl.remotescript.RemoteScript import RemoteScript
from crl.remotescript.fpengine import FPEngine


__copyright__ = 'Copyright (C) 2019, Nokia'

__version__ = '__VERSION__'


class FP(RemoteScript):
    """
    Multi-node specific extensions to [crl.remotescript.RemoteScript.html|RemoteScript]
    library.

    Keywords defined in this library are: `Execute Command In Node`,
    `Execute Background Command In Node`, `Execute Script In Node`,
    `Execute Background Script In Node`, `Copy File To Node`, `Copy File From Node`
    """
    @staticmethod
    def _engine_factory():
        return FPEngine()

    def node(self, node, command, target='default', exec_id='foreground', timeout=None):
        """*DEPRECATED* Keyword has been renamed to `Execute Command In Node`."""
        return self._engine.node_execute(node, command, target, exec_id, timeout)

    def execute_command_in_node(self, node, command, target='default',
                                exec_id='foreground', timeout=None):
        """
        Execute command in the node accessed through a primary target.

        Like keyword `Execute Command In Target`, but instead of
        executing the command in the primary target executes
        the command in named node. This keyword first opens connection
        to the primary target using connection protocol specified with
        `Set Target` keyword. SSH connection is opened from primary
        target to the node to execute the command.

        *Arguments:*\n
        _node_: Target node in which to execute the command.\n
        _command_: Bash shell command to execute in target node.\n
        _target_: Primary target through which the target node is accessed.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout for command in seconds.

        *Returns:*\n
        [crl.remotescript.result.Result.html|Result] object.
        """
        return self._engine.node_execute(node, command, target, exec_id, timeout)

    def node_background(self, node, command, target='default', exec_id='background'):
        """*DEPRECATED* Keyword has been renamed to `Execute Background Command In Node`."""
        self._engine.node_execute_background(node, command, target, exec_id)

    def execute_background_command_in_node(self, node, command, target='default',
                                           exec_id='background'):
        """
        Start executing command in the node accessed through a primary target.

        Like keyword `Execute Background Command In Target`, but
        instead of executing the command in the primary target
        executes the command in named node. This keyword first opens
        connection to the primary target using connection protocol
        specified with `Set Target` keyword. SSH connection is opened
        from primary target to the node to execute the command.

        This keyword returns immediately and the command is left
        running in the background. See `Wait Background Execution` on
        how to read command output and `Kill Background Execution` on
        how to interrupt the execution.

        *Arguments:*\n
        _node_: Target node in which to execute the command.\n
        _command_: Bash shell command to execute in target node.\n
        _target_: Primary target through which the target node is accessed.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout for command in seconds.\n

        *Returns:*\n
        Nothing.\n
        """
        self._engine.node_execute_background(node, command, target, exec_id)

    def node_script(self, node, file, target='default', exec_id='foreground', timeout=None):
        """*DEPRECATED* Keyword has been renamed to `Execute Script In Node`."""
        return self._engine.node_execute_script(node, file, target, exec_id, timeout)

    def execute_script_in_node(self, node, file, target='default', exec_id='foreground', timeout=None):
        """
        Execute script file in the node accessed through a primary target.

        Like keyword `Execute Script In Target`, but instead of
        executing the script file in the primary target executes it in
        named node. This keyword first copies the script file to the
        primary target using the procol specified with `Set
        Target` keyword and from the primary target the script file is
        copied to the target node using scp command. The script file
        is then executed in the node. This call will block until the command
        has been executed.

        *Arguments:*\n
        _node_: Target node in which to execute the script file.\n
        _file_: Path to file to execute in the local host (example: my_script.sh).\n
        _target_: Name of the target through which to open the connection to the node.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout for command in seconds.\n

        *Returns:*\n
        [crl.remotescript.result.Result.html|Result] object.\n
        """
        return self._engine.node_execute_script(node, file, target, exec_id, timeout)

    def node_script_background(self, node, file, target='default', exec_id='background'):
        """*DEPRECATED* Keyword has been renamed to `Execute Background Script In Node`."""
        self._engine.node_execute_script_background(node, file, target, exec_id)

    def execute_background_script_in_node(self, node, file, target='default', exec_id='background'):
        """
        Start executing script file in the node accessed through a primary target.

        Like keyword `Execute Background Script In Target`, but instead of
        executing the script file in the primary target executes it in
        named node. This keyword first copies the script file to the
        primary target node using the procol specified with `Set
        Target` keyword and from the primary node the script file is
        copied to the target node using scp command. The script file
        is then executed in the node.

        This keyword returns immediately and the script is left
        running in the background. See `Wait Background Execution` on
        how to read command output and `Kill Background Execution` on
        how to how to interrupt the execution.

        *Arguments:*\n
        _node_: Target node in which to execute the script file.\n
        _file_: Path to file to execute in the local host (example: my_script.sh).\n
        _target_: Name of the target through which to open the connection to the node.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout for command in seconds.\n

        *Returns:*\n
        Nothing.\n
        """
        self._engine.node_execute_script_background(node, file, target, exec_id)

    def node_put_file(self, node, source_file, destination_dir='.', mode=oct(0o755),
                      target='default', exec_id='foreground', timeout=None):
        """*DEPRECATED* Keyword has been renamed to `Copy File To Node`."""
        return self._engine.node_put_file(
            node, source_file, destination_dir, mode, target, exec_id, timeout)

    def copy_file_to_node(self, node, source_file, destination_dir='.', mode=oct(0o755),
                          target='default', exec_id='foreground', timeout=None):
        """
        Copy file from local host through primary target to the target node.

        *Arguments:*\n
        _node_: Target node where to copy the file to.\n
        _source_file_: Local source file.\n
        _destination_dir_: Remote destination directory in the node. The directory is \
                created if missing.\n
        _mode_: Access mode to set to the file in the target.\n
        _target_: Name of the target through which to copy the file to the node.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout in seconds.\n

        *Returns:*\n
        [crl.remotescript.result.Result.html|Result] object.\n
        """
        return self._engine.node_put_file(
            node, source_file, destination_dir, mode, target, exec_id, timeout)

    def node_get_file(self, node, source_file, destination='.',
                      target='default', exec_id='foreground', timeout=None):
        """*DEPRECATED* Keyword has been renamed to `Copy File From Node`."""
        return self._engine.node_get_file(node, source_file, destination, target, exec_id, timeout)

    def copy_file_from_node(self, node, source_file, destination='.',
                            target='default', exec_id='foreground', timeout=None):
        """
        Copy file from the node through primary target to local host.

        *Arguments:*\n
        _node_: Target node where to copy the file from.\n
        _source_file_: Source file in the node.\n
        _destination_: Destination directory or file in local host.\n
        _target_: Name of the target through which to copy the file from the node.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout in seconds.\n

        *Returns:*\n
        [crl.remotescript.result.Result.html|Result] object.\n
        """
        return self._engine.node_get_file(node, source_file, destination, target, exec_id, timeout)
