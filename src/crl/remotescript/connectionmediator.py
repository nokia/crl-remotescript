# pylint: disable=unused-argument,abstract-method
import os
import re
import shutil
import sys
import tempfile
import ftplib
from ftplib import FTP as PythonFTP
from robot.libraries import Telnet as RobotTelnet
from crl.remotescript.result import Result

if sys.platform.startswith('java'):
    from crl.remotescript.sshjava import SSHClient
else:
    from crl.remotescript.ssh import SSHClient


__copyright__ = 'Copyright (C) 2019, Nokia'


class ConnectionMediator(object):
    """
    Mediator class that provides unified API for different connection protocol
    libraries. New Library instance is created for each connection
    because multi connection handling facilities in the libraries are
    not thread safe (at least for some libs).
    """

    @property
    def lib(self):
        raise NotImplementedError()

    def open_connection(self, host, port, timeout, prompt, prompt_is_regexp):
        self.lib.open_connection(host, port, timeout)

    def login(self, username, password, login_prompt, password_prompt):
        self.lib.login(username, password)

    def set_su_user(self, username, password=None):
        raise NotImplementedError()

    @staticmethod
    def get_su_username():
        return None

    @staticmethod
    def get_su_command(command):
        return command

    def close_connection(self):
        self.lib.close_connection()

    def execute_command(self, command):
        raise NotImplementedError()

    def mkdir(self, path, mode):
        # TBD: This should verify exit status (and execute_command should provide it)
        self.execute_command("umask 0000; sudo mkdir -m %s -p %s" % (mode, path))

    def rmdir(self, path):
        # TBD: This should verify exit status (and execute_command should provide it)
        self.execute_command("rm -rf " + path)

    def put_file(self, src, dst, mode):
        raise NotImplementedError()

    def get_file(self, src, dst):
        raise NotImplementedError()

    def copy_file(self, to_connection, src, dst_dir, mode):
        src_filename = src
        src_filename.replace('/', os.sep)
        src_filename = os.path.basename(src_filename)
        mode = int(mode, 8)
        to_fd = to_connection.get_remote_fd(dst_dir, src_filename)
        try:
            self.remote_copy(src, to_fd)
            to_fd.chmod(mode)
        finally:
            to_fd.close()

    # Must return RemoteFile
    def get_remote_fd(self, directory, filename):
        raise NotImplementedError()

    def remote_copy(self, src, to_fd):
        raise NotImplementedError()


class Telnet(ConnectionMediator):

    EXIT_STATUS_CMD = 'echo -e "\n$?"'

    def __init__(self):
        self._lib = RobotTelnet()  # pylint: disable=not-callable

    @property
    def lib(self):
        return self._lib

    def open_connection(self, host, port, timeout, prompt, prompt_is_regexp):
        self.lib.open_connection(host, timeout=timeout, port=port)
        self.lib.set_prompt(prompt, prompt_is_regexp)

    def login(self, username, password, login_prompt, password_prompt):
        self.lib.login(username, password, login_prompt, password_prompt)

    def execute_command(self, command):
        status = Result.UNKNOWN_STATUS
        out = self.lib.execute_command(command + '; ' + Telnet.EXIT_STATUS_CMD)
        out = out.rstrip()
        # pylint: disable=anomalous-backslash-in-string
        output = re.match("^(.*)\n(\d+)$", out, re.DOTALL)  # noqa: W605
        if output:
            out = output.group(1).strip()
            status = output.group(2)
        return status, out, ''


class SSH(ConnectionMediator):
    def __init__(self):
        self._lib = SSHClient()

    @property
    def lib(self):
        return self._lib

    def login_with_key(self, username, sshkeyfile):
        self.lib.login(username, key_filename=sshkeyfile)

    def set_su_user(self, username, password=None):
        self.lib.set_su_user(username, password)

    def set_use_sudo_user(self):
        self.lib.set_use_sudo_user()

    def get_su_username(self):
        return self.lib.get_su_username()

    def get_su_command(self, command):
        return self.lib.get_su_command(command)

    def execute_command(self, command):
        return self.lib.execute_command(command)

    def put_file(self, src, dst, mode):
        self.lib.put_file(src, dst, mode)

    def get_file(self, src, dst):
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src))
        self.lib.get_file(src, dst)

    def get_remote_fd(self, directory, filename):
        return self.lib.get_remote_fd(directory, filename)

    def remote_copy(self, src, to_fd):
        self.lib.copy_file(src, to_fd)


class SSH_SCP(SSH):
    def put_file(self, src, dst, mode):
        self.lib.get_scp_client().put(src, dst, mode)

    def get_file(self, src, dst):
        if os.path.isdir(dst):
            (mydst, myfile) = (dst, '')
        else:
            (myrealdst, myfile) = os.path.split(dst)
            mydst = tempfile.mkdtemp(dir=myrealdst)
        self.lib.get_scp_client().get(src, mydst)
        if myfile != '':
            shutil.move(os.path.join(mydst, os.path.basename(src)), dst)
            os.rmdir(mydst)

    def copy_file(self, to_connection, src, dst_dir, mode):
        raise NotImplementedError()


class FTP(ConnectionMediator):
    def __init__(self):
        self._lib = PythonFTP()

    @property
    def lib(self):
        return self._lib

    def open_connection(self, host, port, timeout, prompt, prompt_is_regexp):
        if timeout:
            self.lib.connect(host, port=port, timeout=float(timeout))
        else:
            self.lib.connect(host, port=port)

    def close_connection(self):
        self.lib.close()

    def mkdir(self, path, mode=oct(0o755)):
        # mode argument is not used ==> ignored
        # method for creating non existing directories on the remote server
        # no "chmod" command implemented
        pwdir = self.lib.pwd()
        pathlst = path.split('/')
        if pathlst[0] == '':
            pathlst[0] = '/'
        for pathelm in pathlst:
            try:
                # If we can enter the directory, it already exists and we do nothing.
                self.lib.cwd(pathelm)
            except ftplib.all_errors:
                try:
                    # If we could not enter it, we try to create it.
                    self.lib.mkd(pathelm)
                    # If we still cannot enter it, we were not allowed to cretate it.
                    self.lib.cwd(pathelm)
                except ftplib.error_perm:
                    raise AssertionError("Cannot create directory or transfer file '%s'" % pathelm)
        # Before returning, we change back to where we were.
        self.lib.cwd(pwdir)

    def rmdir(self, path):
        self.lib.rmd(path)

    def put_file(self, src, dst, mode):
        self.lib.cwd(dst)
        fh = open(src, 'rb')
        self.lib.storbinary('STOR ' + os.path.basename(src), fh)
        fh.close()

    def get_file(self, src, dst):
        # If the destination is a directory, we can just copy the file into it.
        if os.path.isdir(dst):
            (mydst, myfile) = (dst, '')
        # Ftpdir cannot rename on the fly, so if the destination is a
        # file, we must copy into a temporary directory and move it into
        # the right place with the right name.
        else:
            (myrealdst, myfile) = os.path.split(dst)
            mydst = tempfile.mkdtemp(dir=myrealdst)
        remote_dir = os.path.dirname(src)
        file_basename = os.path.basename(src)
        local_path = os.path.join(mydst, file_basename)
        # Open the local file for writing
        fh = open(local_path, 'wb')
        # cd into the remote directory
        self.lib.cwd(remote_dir)
        # and retrieve the file.
        self.lib.retrbinary('RETR ' + file_basename, fh.write)
        fh.close()
        # If we copied into a temporary directory, move to the right
        # place and delete the temportary directory.
        if myfile != '':
            shutil.move(local_path, dst)
            os.rmdir(mydst)
