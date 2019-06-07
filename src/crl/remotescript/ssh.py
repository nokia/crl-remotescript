# pylint: disable=too-many-branches,too-many-statements
import os
import posixpath
import re
import sys
import time
from logging import debug
import paramiko
from .scp import SCPClient
from .remotefile import RemoteFile
from .result import Result


__copyright__ = 'Copyright (C) 2019, Nokia'


class SSHClient(object):

    BUFFER_SIZE = 32768

    def __init__(self):
        self.client = None
        self.host = None
        self.port = None
        self.timeout = None
        self.su_username = None
        self.su_password = None
        self.use_sudo_user = False

    def open_connection(self, host, port, timeout):
        self.host, self.port, self.timeout = host, int(port), float(timeout)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def login(self, username, password=None, key_filename=None):
        self.client.connect(self.host, self.port, username, password=password, key_filename=key_filename,
                            timeout=self.timeout, allow_agent=False)

    def set_su_user(self, username, password=None):
        self.su_username = username
        self.su_password = password

    def set_use_sudo_user(self):
        self.use_sudo_user = True

    def get_su_username(self):
        return self.su_username

    def get_su_command(self, command):
        if self.su_username:
            if re.search("'", command):
                raise SSHException(
                    'Su command may not contain single quotes. Consider using double quotes: "' +
                    command + '"')
            return self._su_command_template.format(su_username=self.su_username,
                                                    command=command)
        return command

    @property
    def _su_command_template(self):
        return ("sudo -u {su_username} {command}"
                if self.use_sudo_user else
                "su - {su_username} -c '{command}'")

    def close_connection(self):
        self.client.close()

    def get_scp_client(self):
        return SCPClient(self.client.get_transport())

    def execute_command(self, command):
        chan = self.client.get_transport().open_session()
        chan.settimeout(1.0)
        try:
            # if the command executed with 'sudo' prefix the terminal needed as well
            if (self.su_username and self.su_password) or (re.search("\ssudo\s.*", command, re.IGNORECASE) is not None):
                chan.get_pty()
            chan.exec_command(command)
            while not self.client.get_transport().is_active():
                time.sleep(0.1)
                try:
                    self.client.get_transport().send_ignore(1)
                except:
                    raise SSHException("Connection closed unexpectedly: " + str(sys.exc_info()[1]))

            out = ""
            err = ""
            password_sent = False
            if self.su_username and self.su_password:
                for _ in range(100):
                    if chan.exit_status_ready() or chan.closed:
                        break
                    if not chan.recv_ready():
                        time.sleep(0.1)
                    else:
                        out += chan.recv(SSHClient.BUFFER_SIZE)
                        outmatch = re.match(".*[P|p]assword:\s*$", out, re.DOTALL)
                        if outmatch:
                            stdin = chan.makefile('wb', -1)
                            stdin.write('%s\n' % self.su_password)
                            stdin.flush()
                            password_sent = True
                            break

            if password_sent:
                out = ""

            counter = 0
            while self.client.get_transport().is_active():
                if chan.exit_status_ready() or chan.closed:
                    break
                if chan.recv_ready():
                    out += chan.recv(SSHClient.BUFFER_SIZE)
                if chan.recv_stderr_ready():
                    err += chan.recv_stderr(SSHClient.BUFFER_SIZE)
                counter = (counter + 1) % 10
                if counter == 0:
                    try:
                        self.client.get_transport().send_ignore(1)
                    except SSHException:
                        break
                time.sleep(0.1)

            while chan.recv_ready():
                out += chan.recv(SSHClient.BUFFER_SIZE)
                time.sleep(0.1)
            while chan.recv_stderr_ready():
                err += chan.recv_stderr(SSHClient.BUFFER_SIZE)
                time.sleep(0.1)
            stat = Result.UNKNOWN_STATUS
            if chan.exit_status_ready():
                stat = str(chan.recv_exit_status())  # TBD: Use this as real exit status
                if stat == '-1':
                    stat = Result.UNKNOWN_STATUS
            return stat, out, err
        finally:
            chan.close()

    def put_file(self, src_file, dst_dir, mode):
        src_file.replace('/', os.sep)
        mode = int(mode, 8)
        sftp = self.client.open_sftp()
        try:
            dst_dir = self._resolve_dir(sftp, dst_dir)
            self._create_missing_dirs(sftp, dst_dir)
            dst_file = posixpath.join(dst_dir, os.path.basename(src_file))
            try:
                sftp.put(src_file, dst_file)
            except Exception as e:
                raise Exception("Putting file failed (%s/%s): %s" % (dst_dir, src_file, e))
            sftp.chmod(dst_file, mode)
        finally:
            sftp.close()

    @staticmethod
    def _resolve_dir(sftp, dst_dir):
        dst_home = sftp.normalize('.')
        dst_dir = dst_dir.split(':')[-1].replace('\\', '/')
        if dst_dir == '.':
            dst_dir = dst_home + '/'
        if not posixpath.isabs(dst_dir):
            dst_dir = posixpath.join(dst_home, dst_dir)
        return dst_dir

    @staticmethod
    def _create_missing_dirs(sftp, dst_dir):
        if dst_dir[0] == '/':
            sftp.chdir('/')
        for dir in dst_dir.split('/'):
            sftp_working_directory = sftp.getcwd()
            if (dir and dir != '.' and dir != '..' and
                    dir not in sftp.listdir(sftp_working_directory)):
                debug("Creating remote directory (%s/%s)" % (sftp_working_directory, dir))
                try:
                    sftp.mkdir(dir)
                except Exception as e:
                    raise Exception(
                        'Cannot create directory "%s" under "%s" in the remote host: %s'
                        % (dir, sftp_working_directory, e))
            try:
                sftp.chdir(dir)
            except Exception as e:
                raise Exception(
                    'Cannot cd to newly created directory "%s" under "%s" in the remote host: %s'
                    % (dir, sftp_working_directory, e))

    def get_file(self, src_file, dst_file):
        sftp = self.client.open_sftp()
        try:
            dst_file = os.path.abspath(dst_file.replace('/', os.sep))
            dst_dir = os.path.dirname(dst_file)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            sftp.get(src_file, dst_file)
        finally:
            sftp.close()

    def copy_file(self, src_file, to_fd):
        sftp = self.client.open_sftp()
        from_fd = None
        try:
            from_fd = sftp.open(src_file, 'rb')
            file_to_size = 0
            file_from_stat = from_fd.stat()
            while True:
                data = from_fd.read(SSHClient.BUFFER_SIZE)
                if not data:
                    break
                to_fd.write(data)
                file_to_size += len(data)
        finally:
            if from_fd:
                from_fd.close()
            sftp.close()
        if file_from_stat.st_size != file_to_size:
            raise IOError('Size mismatch in copying:  %d != %d' % (
                file_from_stat.st_size, file_to_size))

    def get_remote_fd(self, dir, filename):
        sftp = self.client.open_sftp()
        dir = self._resolve_dir(sftp, dir)
        self._create_missing_dirs(sftp, dir)
        file_path = posixpath.join(dir, filename)
        fd = sftp.open(file_path, 'wb')
        return SFTPRemoteFile(sftp, fd)


class SFTPRemoteFile(RemoteFile):

    def __init__(self, sftp, fd):
        self._sftp = sftp
        self._fd = fd

    def write(self, data):
        self._fd.write(data)

    def chmod(self, mode):
        self._fd.chmod(mode)

    def close(self):
        self._fd.close()
        self._sftp.close()


class SSHException(Exception):
    pass
