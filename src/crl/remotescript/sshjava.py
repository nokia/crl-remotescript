# pylint: disable=too-many-statements,too-many-branches,too-many-locals
import os
import posixpath
import re
import sys
import time
# pylint: disable=import-error
from com.trilead.ssh2 import (
    ChannelCondition,
    Connection,
    StreamGobbler,
    SFTPv3Client,
    SCPClient)
import jarray
from java.io import BufferedReader, InputStreamReader, FileOutputStream, IOException
# pylint: enable=import-error
from .remotefile import RemoteFile
from .result import Result
from .SSHClientBase import (
    SSHClientBase, SSHException)
sys.path.append(os.path.join(
    os.path.split(os.path.abspath(__file__))[0], 'trilead-ssh2-' +
    '__TRILEAD_SSH2_VERSION__' + '.jar'))

__copyright__ = 'Copyright (C) 2019, Nokia'


class SSHClient(SSHClientBase):

    def open_connection(self, host, port, timeout):
        self.client = Connection(host, int(port))
        timeout = int(timeout) * 1000
        self.client.connect(None, timeout, timeout)

    def login(self, username, password):
        if not self.client.authenticateWithPassword(username, password):
            raise SSHException('Login failed with username "%s"' % username)

    @property
    def su_command_template(self):
        return "su - {su_username} -c '{command}'"

    def close_connection(self):
        self.client.close()

    def get_scp_client(self):
        return SCPClient(self.client)

    def execute_command(self, command):
        chan = self.client.openSession()
        try:
            if self.su_username and self.su_password:
                chan.requestPTY('vt100', 80, 24, 0, 0, None)
            chan.execCommand(command)
            stdin = chan.getStdin()
            stdout = BufferedReader(InputStreamReader(StreamGobbler(chan.getStdout())))
            stderr = BufferedReader(InputStreamReader(StreamGobbler(chan.getStderr())))

            out = ""
            data = jarray.zeros(SSHClient.BUFFER_SIZE, 'c')
            password_sent = False
            endcond = ChannelCondition.CLOSED | ChannelCondition.EOF | \
                ChannelCondition.EXIT_SIGNAL | ChannelCondition.EXIT_STATUS
            if self.su_username and self.su_password:
                for _ in range(100):
                    cond = chan.waitForCondition(endcond, 10)  # arg2 timeout in ms
                    if (cond & ChannelCondition.TIMEOUT) == 0:
                        break  # not timeout, must be some of the expected conds
                    if not stdout.ready():
                        time.sleep(0.1)
                    else:
                        datalen = stdout.read(data, 0, SSHClient.BUFFER_SIZE)
                        if datalen == -1:
                            break
                        if datalen > 0:
                            out += ''.join([str(c) for c in data[0:datalen]])
                        # pylint: disable=anomalous-backslash-in-string
                        outmatch = re.match(".*[P|p]assword:\s*$", out, re.DOTALL)  # noqa: W605
                        if outmatch:
                            stdin.write('%s\n' % self.su_password)
                            stdin.flush()
                            password_sent = True
                            break

            if password_sent:
                out = ""

            counter = 0
            while True:
                cond = chan.waitForCondition(endcond, 10)  # arg2 timeout in ms
                if (cond & ChannelCondition.TIMEOUT) == 0:
                    break  # not timeout, must be some of the expected conds
                counter = (counter + 1) % 10
                if counter == 0:
                    try:
                        self.client.sendIgnorePacket()
                    except IOException:
                        break
                time.sleep(0.1)

            out += self._read_output(stdout)
            err = self._read_output(stderr)
            stat = chan.getExitStatus()
            if stat is None:
                stat = Result.UNKNOWN_STATUS
            else:
                stat = str(stat)
            return stat, out, err
        finally:
            chan.close()

    @staticmethod
    def _read_output(reader):
        lines = ''
        line = reader.readLine()
        while line is not None:
            lines += line + '\n'
            line = reader.readLine()
        return lines

    def put_file(self, src_file, dst_dir, mode):
        src_file.replace('/', os.sep)
        mode = int(mode, 8)
        sftp = SFTPv3Client(self.client)
        src_fd = None
        dst_fd = None
        try:
            dst_dir = self._resolve_dir(sftp, dst_dir)
            self._create_missing_dirs(sftp, dst_dir)
            dst_file = posixpath.join(dst_dir, os.path.basename(src_file))
            src_fd = open(src_file, 'rb')
            dst_fd = sftp.createFile(dst_file)
            stats = sftp.fstat(dst_fd)
            stats.permissions = mode
            sftp.fsetstat(dst_fd, stats)
            size = 0
            while True:
                data = src_fd.read(SSHClient.BUFFER_SIZE)
                datalen = len(data)
                if datalen == 0:
                    break
                sftp.write(dst_fd, size, data, 0, datalen)
                size += datalen
        finally:
            if dst_fd:
                sftp.closeFile(dst_fd)
            if src_fd:
                src_fd.close()
            sftp.close()

    @staticmethod
    def _create_missing_dirs(sftp, dst_dir):
        curdir = '/'
        for directory in dst_dir.split('/'):
            if directory:
                curdir = '%s/%s' % (curdir, directory)
            try:
                sftp.stat(curdir)
            except IOException:
                sftp.mkdir(curdir, 0o744)

    def get_file(self, src_file, dst_file):
        sftp = SFTPv3Client(self.client)
        dst_fd = None
        src_fd = None
        try:
            dst_file = os.path.abspath(dst_file.replace('/', os.sep))
            dst_dir = os.path.dirname(dst_file)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            dst_fd = FileOutputStream(dst_file)
            stats = sftp.stat(src_file)
            src_size = stats.size
            src_fd = sftp.openFileRO(src_file)
            size = 0
            arraysize = SSHClient.BUFFER_SIZE
            data = jarray.zeros(arraysize, 'b')
            while True:
                moredata = sftp.read(src_fd, size, data, 0, arraysize)
                datalen = len(data)
                if moredata == -1:
                    break
                if src_size - size < arraysize:
                    datalen = src_size - size
                dst_fd.write(data, 0, datalen)
                size += datalen
        finally:
            if src_fd:
                sftp.closeFile(src_fd)
            if dst_fd:
                dst_fd.flush()
                dst_fd.close()
            sftp.close()

    def copy_file(self, src_file, to_fd):
        sftp = SFTPv3Client(self.client)
        from_fd = None
        try:
            stats = sftp.stat(src_file)
            src_size = stats.size
            from_fd = sftp.openFileRO(src_file)
            file_to_size = 0
            arraysize = SSHClient.BUFFER_SIZE
            data = jarray.zeros(arraysize, 'b')
            while True:
                moredata = sftp.read(from_fd, file_to_size, data, 0, arraysize)
                datalen = len(data)
                if moredata == -1:
                    break
                if src_size - file_to_size < arraysize:
                    datalen = src_size - file_to_size
                to_fd.write(data)
                file_to_size += datalen
        finally:
            if from_fd:
                sftp.closeFile(from_fd)
            sftp.close()
        if src_size != file_to_size:
            raise IOError('Size mismatch in copying:  %d != %d' % (
                src_size, file_to_size))

    def get_remote_fd(self, directory, filename):
        sftp = SFTPv3Client(self.client)
        directory = self._resolve_dir(sftp, directory)
        self._create_missing_dirs(sftp, directory)
        file_path = posixpath.join(directory, filename)
        fd = sftp.createFile(file_path)
        return SFTPRemoteFile(sftp, fd)


class SFTPRemoteFile(RemoteFile):

    def __init__(self, sftp, fd):
        self._sftp = sftp
        self._fd = fd
        self._size = 0

    def write(self, data):
        datalen = len(data)
        self._sftp.write(self._fd, self._size, data, 0, datalen)
        self._size += datalen

    def chmod(self, mode):
        stats = self._sftp.fstat(self._fd)
        stats.permissions = mode
        self._sftp.fsetstat(self._fd, stats)

    def close(self):
        self._sftp.closeFile(self._fd)
        self._sftp.close()
