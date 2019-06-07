# pylint: disable=redefined-outer-name
import pytest
import mock
from fixtureresources.fixtures import create_patch

from crl.remotescript import RemoteScript


__copyright__ = 'Copyright (C) 2019, Nokia'


@pytest.fixture(scope='function')
def mock_paramiko_channel(request):
    c = create_patch(mock.patch(
        'crl.remotescript.ssh.paramiko.SSHClient',
        spec_set=True), request)

    chan = c.return_value.get_transport.return_value.open_session.return_value
    chan.recv_ready.return_value = False
    chan.recv_stderr_ready.return_value = False
    return chan


@pytest.mark.parametrize('use_sudo_user, expected_exec_call_end', [
    (False, "su - suuser -c 'command'"),
    (True, "sudo -u suuser command"),
    (None, "su - suuser -c 'command'")])
def test_su_command(mock_paramiko_channel,
                    use_sudo_user,
                    expected_exec_call_end):
    r = RemoteScript()
    r.set_target('host', 'user', 'password')
    r.set_target_property('default', 'su username', 'suuser')
    r.set_target_property('default', 'su password', 'supassword')
    if use_sudo_user is not None:
        r.set_target_property('default', 'use sudo user', use_sudo_user)

    r.execute_command_in_target('command')

    assert mock_paramiko_channel.exec_command.call_args[0][0].endswith(
        expected_exec_call_end)
