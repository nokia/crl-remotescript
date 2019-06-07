# pylint: disable=redefined-builtin
from crl.remotescript.baseengine import BaseEngine
from crl.remotescript.target import Target


__copyright__ = 'Copyright (C) 2019, Nokia'

__version__ = '__VERSION__'


class RemoteScript(object):
    """
    Library for executing remote commands over SSH or Telnet and
    transferring files over SFTP and FTP protocols.

    See also [crl.remotescript.result.Result.html|Result] and
    [crl.remotescript.target.Target.html|Target].

    Multi-node specific extensions are implemented in subclass
    [crl.remotescript.FP.html|RemoteScript.FP].

    With this library the test targets are first defined with `Set
    Target` keyword and they are given optionally a name. More
    detailed target setup is possible with `Set Target Property`
    keyword. After the targets are defined the commands can be
    executed with `Execute Command In Target` keyword.

    Robot library scope is 'TEST CASE' meaning that the targets have
    to be set individually before each test case. This is done
    conveniently by using Test Setup setting.\n

    *Example test case:*\n
    | *Setting*  | *Value*       |
    | Library    | RemoteScript  |
    | Test Setup | Init Target   |

    | *Keyword* | *Action* | *Argument* | *Argument*  | *Argument* | *Argument* | *Argument* |
    | Init Targets | Set Target | 10.20.0.1  | root | root |
    |  | Set Target  | 10.20.0.2  | root  | root           |  target_2  |
    |  | Set Target Property | target_2   | port           | 2323       |
    |  | Set Target  | 10.20.0.2  | root  | root           |  target_3  | telnet |
    |  | Set Target Property | target_3   | login prompt   | LOGIN>     |


    | *Test Case*  | *Action*  | *Argument*  | *Argument*  | *Argument* |
    | TC 1  | ${result}=       | Execute Command In Target | echo \"Hello World\" |
    |       | Should Be Equal  | ${result.status}  | 0     |
    |       |                  |                           |
    | TC 2  | Execute Background Command In Target | echo \"Hello World\" | target_2 | bg_id |
    |       | ${fg_result}=    | Execute Command In Target | echo \"Hello World\" |
    |       | ${bg_result}=    | Wait Background Execution | bg_id                |
    |       | Should Be Equal  | ${fg_result.stdout}       | Hello World          |
    |       | Should Be Equal  | ${bg_result.stdout}       | Hello World          |
    """
    ROBOT_LIBRARY_SCOPE = 'TEST CASE'

    def __init__(self):
        self._engine = self._engine_factory()

    @staticmethod
    def _engine_factory():
        return BaseEngine()

    def __str__(self):
        ret = 'RemoteScript instance\ntargets:'
        for name, target in self._engine.targets.items():
            ret += name + ' ' + str(target) + '\n'
        return ret

    def set_target(self, host, username, password, name='default', protocol='ssh/sftp'):
        """
        Adds a target to RemoteScript Library.

        *Arguments:*\n
        _host_: Host name or ip address of the target host\n
        _username_: User name for login to _host_\n
        _password_: Password for the _username_\n
        _name_: String identifier used to distinguish multiple targets.\n
        _protocol_: Protocol for connecting the target (\"telnet\", \"ssh/sftp\" \
                or \"ftp\").\nValue \"ssh\" is mapped to default \"ssh/sftp\". \
                Value is case insensitive.

        *Returns:*\n
        Nothing.\n
        """
        target = Target(host, username, protocol)
        target.set_password(password)
        self._engine.targets[name] = target

    def set_target_with_sshkeyfile(self, host, username, sshkeyfile, name='default', protocol='ssh/sftp'):
        """
        Exactly as `Set Target` but instead of a password, a ssh private key file is expected as input\n
        Due to paramiko the used key pair must be Ed25519 type

        *Arguments:*\n
        _sshkeyfile_: Ssh key file for the _username_\n
        """
        target = Target(host, username, protocol)
        target.set_ssh_key_file(sshkeyfile)
        self._engine.targets[name] = target

    def set_target_property(self, target_name, property_name, property_value):
        """
        Sets property _property_name_ for target _target_name_.

        *Arguments:*\n
        _target_name_: Name of the individual target, whose property to set.\n
        _property_name_: Name of the property.\n
        _property_value_: Value of the property.\n

        *Returns:*\n
        Nothing.\n

        *Supported properties:*\n
        | *Name*    | *Description* | *Default Value*   |
        | _cleanup_ | Delete temporary directories and files when the keyword  is exiting. | True |
        | _connection break is error_ | Raise exception if connection is lost before command is \
                finished. If set to False, exception is not raised if connection is closed  \
                unexpectely. [crl.remotescript.result.Result.html|Result].close_ok  will be \
                set to \"False\", exit status is  \"unknown\", stdout  and stderr will be \
                empty strings | True |
        | _connection failure is error_ | Raise exception if connection cannot be opened. If \
                set to false, exception is not raised if opening connection fails.  \
                [crl.remotescript.result.Result.html|Result].connection_ok will be set to \
                \"False\", exit status to \"unknown\", stdout and stderr will be empty \
                strings | True |
        | _login prompt_  | Telnet login prompt regular expression   | \"login: \" |
        | _login timeout_ | Timeout to wait login prompt in seconds. | 60 |
        | _max connection attempts_ | Maxmum nuber of reconnection attempts if connection \
                is  refused | 10 |
        | _nonzero status is error_ | Raise NonZeroExitStatusError if exit status of the \
                command is not  zero. If set to 'True' and command fails  stdout and stderr \
                are not returned, but they are included in the exception message | False |
        | _password prompt_ | Telnet password prompt regular expression  | \"Password: \"  |
        | _port_            | Target port.       | 22 for ssh and 23 for telnet |
        | _prompt_          | Target prompt      | \"$ \" |
        | _su password_     | Target su password | None |
        | _su username_     | Target su username. If defined, command and script  execution \
                related keywords will do the execution under  this account. *NOTE:* \
                Multi-node specific keywords in [crl.remotescript.FP.html|RemoteScript.FP] \
                use this _su username_  (if defined) in all SSH/SCP operations  between CLA \
                and nodes (not doing su). *LIMITATIONS:* Commands may not contain single \
                quotes (double quotes are ok). Stdout and stderr are combined to \
                [crl.remotescript.result.Result.html|Result] object stdout field. Telnet \
                protocol is not supported. | None  |
        | _use sudo user_  | Use 'sudo -u' instead of 'su -'. | False |
        """
        self._engine.set_target_property(target_name, property_name, property_value)

    def set_default_target_property(self, property_name, property_value):
        """
        Sets default property for all targets.

        Target specific properties override the default values. See
        `Set Target Property` for supported properties.

        *Arguments:*\n
        _property_name_: Name of the property.\n
        _property_value_: Value of the property.\n

        *Returns:*\n
        Nothing.\n
        """
        self._engine.default_properties[property_name] = property_value

    def get_target_properties(self, target):
        """
        Returns python dict object containing effective properties for _target_.
        """
        return self._engine.get_target_properties(target)

    def execute(self, command, target='default', exec_id='foreground', timeout=None):
        """*DEPRECATED* Keyword has been renamed to `Execute Command In Target`."""
        return self._engine.execute(command, target, exec_id, timeout)

    def execute_command_in_target(self, command, target='default', exec_id='foreground', timeout=None):
        """
        Executes remote command in the target.

        This call will block until the command has been executed.

        *Arguments:*\n
        _commmand_: Bash shell command to execute in the target (example: \"uname -a;ls;sleep 5;date\")\n
        _target_: Name of the target where to execute the command.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout for command in seconds.\n

        *Returns:*\n
        [crl.remotescript.result.Result.html|Result] object.

        *Example:*\n
        | testcase | ${result}=      | Execute Command In Target | echo foo; echo bar>&2 |
        |          | Should Be Equal | ${result.status}          | 0                     |
        |          | Should Be Equal | ${result.stdout}          | foo                   |
        |          | Should Be Equal | ${result.stderr}          | bar                   |
        |          | Should Be Equal | ${result.connection_ok}   | True                  |
        |          | Should Be Equal | ${result.close_ok}        | True                  |
        """
        return self._engine.execute(command, target, exec_id, timeout)

    def execute_background(self, command, target='default', exec_id='background'):
        """*DEPRECATED* Keyword has been renamed to `Execute Background Command In Target`."""
        self._engine.execute_background(command, target, exec_id)

    def execute_background_command_in_target(self, command, target='default', exec_id='background'):
        """
        Starts to execute remote command in the target.

        This keyword returns immediately and the command is left
        running in the background. See `Wait Background Execution` on
        how to read command output and `Kill Background Execution` on
        how to interrupt the execution.

        *Arguments:*\n
        _commmand_: Bash shell command to execute (example: \"uname -a;ls;sleep 5;date\")\n
        _target_: Name of the target where to execute the command\n
        _exec_id_: Connection ID to use.\n

        *Returns:*\n
        Nothing.\n

        *Example:*\n
        | testcase | Execute Background Command In Target | echo Hello | default | bg1 |
        |          | Execute Background Command In Target | echo Hello | default | bg2 |
        |          | Execute Background Command In Target | echo Hello | default | bg3 |
        |          | ${result_1}=                         | Wait Background Execution | bg1 |
        |          | ${result_2}=                         | Wait Background Execution | bg2 |
        |          | ${result_3}=                         | Wait Background Execution | bg3 |
        """
        self._engine.execute_background(command, target, exec_id)

    def execute_script(self, file, target='default', exec_id='foreground', timeout=None):
        """*DEPRECATED* Keyword has been renamed to `Execute Script In Target`."""
        return self._engine.execute_script(file, target, exec_id, timeout, arguments=None)

    def execute_script_in_target(self, file, target='default', exec_id='foreground', timeout=None, arguments=None):
        """
        Execute script file in remote target.

        Copies the file to the target and executes it. This call will
        block until the command has been executed.

        *Arguments:*\n
        _file_: Path to file to execute (example: my_script.sh).\n
        _target_: Name of the target where to execute the file.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout for command in seconds.\n
        _arguments_: Optional arguments for the executed script

        *Returns:*\n
        [crl.remotescript.result.Result.html|Result] object.\n

        *Example:*\n
        | testcase | ${result}=      | Execute Script In Target | my_script.sh |
        |          | Log             | ${result}                |              |
        |          | Should Be Equal | ${result.status}         | 0            |

        """
        return self._engine.execute_script(file, target, exec_id, timeout, arguments)

    def execute_script_background(self, file, target='default', exec_id='background'):
        """*DEPRECATED* Keyword has been renamed to `Execute Background Script In Target`."""
        self._engine.execute_script_background(file, target, exec_id)

    def execute_background_script_in_target(self, file, target='default', exec_id='background'):
        """
        Starts to execute script file in the remote target.

        Returns immediately and the command is left running in the
        background. See `Wait Background Execution` on how to read
        command output and `Kill Background Execution` on how to
        terminate the connection without retrieving the results.

        *Arguments:*\n
        _file_: Path to file to execute (example: my_script.sh).\n
        _target_: Name of the target where to execute the file.\n
        _exec_id_: Connection ID to use.\n

        *Returns:*\n
        Nothing.\n

        *Example:*\n
        | testcase | Execute Background Script In Target | my_script.sh  | default   | bg1 |
        |          | ${result_bg1}                       | Wait Background Execution | bg1 |
        |          | Log                                 | ${result_bg1}             |     |
        |          | Should Be Equal                     | ${result_bg1.status}      | 0   |
        """
        self._engine.execute_script_background(file, target, exec_id)

    def wait_background(self, exec_id='background', timeout=None):
        """*DEPRECATED* Keyword has been renamed to `Wait Background Execution`."""
        return self._engine.wait_background(exec_id, timeout)

    def wait_background_execution(self, exec_id='background', timeout=None):
        """
        Waits for background command execution to finish.

        This keyword blocks until the background command with id
        _exec_id_ finishes or the timeout expires.

        *Arguments:*\n
        _exec_id_: Connection ID to wait for.\n
        _timeout_: Time to wait in seconds.\n

        *Returns:*\n
        [crl.remotescript.result.Result.html|Result] object containing the result of the execution
        that was waited for.\n

        *Example:* See `Execute Background Command In Target`
        """
        return self._engine.wait_background(exec_id, timeout)

    def kill_background(self, exec_id='background'):
        """*DEPRECATED* Keyword has been renamed to `Kill Background Execution`."""
        self._engine.kill_background(exec_id)

    def kill_background_execution(self, exec_id='background'):
        """
        Closes background connection.

        The command being executed is killed. Result object can be
        retreived by with 'Wait Background Execution` keyword.

        *Arguments:*\n
        _exec_id_: Connection ID to kill.

        *Returns:*\n
        Nothing

        *Example:* See `Execute Background Command In Target`
        """
        self._engine.kill_background(exec_id)

    def put_file(self, source_file, destination_dir='.', mode=oct(0o755),
                 target='default', exec_id='foreground', timeout=None):
        """*DEPRECATED* Keyword has been renamed to `Copy File To Target`."""
        return self._engine.put_file(source_file, destination_dir, mode, target, exec_id, timeout)

    def copy_file_to_target(self, source_file, destination_dir='.',
                            mode=oct(0o755), target='default', exec_id='foreground', timeout=None):
        """
        Copy file from local host to the target.

        *Arguments:*\n
        _source_file_: Local source file.\n
        _destination_dir_: Remote destination directory. It is protocol specific
            if the destination directory must exist. SFTP protocol creates
            the destination directory and missing intermediate directories if
            they do not exist. SCP and FTP protocols raise exception if the
            destination directory is missing.\n
        _mode_: Access mode to set to the file in the target. Ignored for FTP.\n
        _target_: Target where to copy the file.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout in seconds.\n

        *Returns:*\n
        [crl.remotescript.result.Result.html|Result] object.

        *Example:*\n
        | testcase | Create Directory In Target | /tmp/my-robot-tc |                   |
        |          | Copy File To Target        | foo.sh           | /tmp/my-robot-tc/ |
        """
        return self._engine.put_file(source_file, destination_dir, mode, target, exec_id, timeout)

    def copy_file_between_targets(self, from_target, source_file, to_target,
                                  destination_dir=".", mode=oct(0o755), exec_id='foreground', timeout=None):
        """
        Copy file from one remote target to another. Supports only SFTP.

        *Arguments:*\n
        _from_target_: Source target.\n
        _source_file_: Source file.\n
        _to_target_: Destination target.\n
        _destination_dir_: Destination directory.\n
        _mode_: Access mode to set to the file in the destination target.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout in seconds.\n

        *Returns:*\n
        [crl.remotescript.result.Result.html|Result] object.

        *Example:*\n
        | testcase | Copy File Between Targets | default | /tmp/foo.tgz | target2 | /tmp/backups/ |
        """
        return self._engine.copy_file(from_target, source_file, to_target,
                                      destination_dir, mode, exec_id, timeout)

    def get_file(self, source_file, destination='.', target='default', exec_id='foreground', timeout=None):
        """*DEPRECATED* Keyword has been renamed to `Copy File From Target`."""
        return self._engine.get_file(source_file, destination, target, exec_id, timeout)

    def copy_file_from_target(self, source_file, destination='.',
                              target='default', exec_id='foreground', timeout=None):
        """
        Copy file from the target to local host.\n

        *Arguments:*\n
        _source_file_: Target source file.\n
        _destination_: Local destination directory or file.\n
        _target_: Target where to copy the file from.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout in seconds.\n

        *Returns:*\n
        [crl.remotescript.result.Result.html|Result] object.

        *Example:*\n
        | testcase | Create Directory In Target | /tmp/my-robot-tc  |                         |
        |          | Execute Command In Target  | touch             | /tmp/my-robot-tc/foo.sh |
        |          | Copy File From Target      | /tmp/my-robot-tc/bar.sh |
        """
        return self._engine.get_file(source_file, destination, target, exec_id, timeout)

    def put_dir(self, source_dir, target_dir='.', mode=oct(0o755),
                target='default', exec_id='foreground', timeout=None):
        """*DEPRECATED* Keyword has been renamed to `Copy Directory To Target`."""
        return self._engine.put_dir(source_dir, target_dir, mode, target, exec_id, timeout)

    def copy_directory_to_target(self, source_dir, target_dir='.', mode=oct(0o755),
                                 target='default', exec_id='foreground', timeout=None):
        """
        Copies contents of local source directory to remote destination directory.

        *Arguments:*\n
        _source_dir_: Local source directory whose contents are copied to the target.\n
        _target_dir_: Remote destination directory that will be created if missing.\n
        _mode_: Access mode to set to the files and directories copied to the target.\n
        _target_: Target where to copy the file.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout in seconds.\n

        *Returns:*\n
        [crl.remotescript.result.Result.html|Result] object.\n

        *Example:*\n
        | testcase | Copy Directory To Target | scripts | /tmp/my-robot-tc/scripts/ |
        """
        return self._engine.put_dir(source_dir, target_dir, mode, target, exec_id, timeout)

    def mkdir(self, path, mode=oct(0o755), target='default', exec_id='foreground', timeout=None):
        """*DEPRECATED* Keyword has been renamed to `Create Directory In Target`."""
        return self._engine.mkdir(path, mode, target, exec_id, timeout)

    def create_directory_in_target(self, path, mode=oct(0o755), target='default', exec_id='foreground', timeout=None):
        """
        Create a directory including missing parent directories in the target.

        For FTP, missing intermediate directories are not created and mode is ignored.

        *Arguments:*\n
        _path_: Remote directory to create.\n
        _mode_: Access mode to set to the directory in the target.\n
        _target_: Target where to create the file.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout in seconds.\n

        *Returns:*\n
        [crl.remotescript.result.Result.html|Result] object.\n
        """
        return self._engine.mkdir(path, mode, target, exec_id, timeout)

    def rmdir(self, path, target='default', exec_id='foreground', timeout=None):
        """*DEPRECATED* Keyword has been renamed to `Remove Directory In Target`."""
        return self._engine.rmdir(path, target, exec_id, timeout)

    def remove_directory_in_target(self, path, target='default', exec_id='foreground', timeout=None):
        """
        Delete a directory including all contained files and directories.

        This keyword does not work for pure file transfer protocols like FTP.

        *Arguments:*\n
        _path_: Remote directory to delete.\n
        _target_: Target where to create the file.\n
        _exec_id_: Connection ID to use.\n
        _timeout_: Timeout in seconds.\n

        *Returns:*\n
        [crl.remotescript.result.Result.html|Result] object.\n
        """
        return self._engine.rmdir(path, target, exec_id, timeout)
