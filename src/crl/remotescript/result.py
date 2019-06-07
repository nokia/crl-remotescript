from crl.remotescript import pathops
from crl.remotescript.compatibility import (
    unic_to_string, py23_unic)

__copyright__ = 'Copyright (C) 2019, Nokia'


class Result(object):
    """
    Result of executed remote command in
    [crl.remotescript.remotescript.RemoteScript.html|RemoteScript] library. Result
    consists of command exit status, standard output, standard error and some
    additional properties. All fields can be logged by printing
    the result object.

    *Examples:*\n
    | testcase | ${result}=      | Execute Command In Target | echo foo; echo bar>&2 |
    |          | Should Be Equal | ${result.status}          | 0                     |
    |          | Should Be Equal | ${result.stdout}          | foo                   |
    |          | Should Be Equal | ${result.stderr}          | bar                   |
    |          | Should Be Equal | ${result.connection_ok}   | True                  |

    | testcase | ${result}=      | Execute Command In Target | echo foo; echo bar>&2 |
    |          | Log             | ${result}                 |                       |

    """

    OPEN_OK = 'True'
    OPEN_FAIL = 'False'
    CLOSE_OK = OPEN_OK
    CLOSE_FAIL = OPEN_FAIL
    UNKNOWN_STATUS = 'unknown'

    def __init__(self, status, stdout, stderr, connection_ok, close_ok):
        """
        *Arguments:*\n
        _status_: Exit status of the remote command.\n
        _stdout_: Standard output of the remote command.\n
        _stderr_: Standard error of the remote command.\n
        _connection_ok_: \"True\" if connection was opened succesfully. \"False\"
                     if opening connection failed. See also 'connection failure is error' property\n
        _close_ok_:   Tells how the connection was closed: \"True\" if the command was executed
                     normally, \"False\" if executing command ended prematurely.
                     See also 'connection break is error' property\n
        """
        self.status = status
        self.stdout = unic_to_string(py23_unic(stdout))
        self.stderr = unic_to_string(py23_unic(stderr))
        self.connection_ok = connection_ok
        self._close_ok = close_ok

    def __str__(self):
        return ' '.join(['\n',
                         'connection OK: ', self.connection_ok, '\n',
                         'close OK:      ', self._close_ok, '\n',
                         'exit status:   ', str(self.status), '\n',
                         'stdout:\n', pathops.unic(self.stdout), '\n',
                         'stderr:\n', pathops.unic(self.stderr), '\n'])


Result.SUCCESS = Result('0', '', '', Result.OPEN_OK, Result.CLOSE_OK)
Result.CONNECTION_FAILURE = Result(Result.UNKNOWN_STATUS, '', '', Result.OPEN_FAIL, Result.CLOSE_FAIL)
