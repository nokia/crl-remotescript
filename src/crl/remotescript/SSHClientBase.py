import re
import posixpath

__copyright__ = 'Copyright(C) 2019, Nokia'


class SSHClientBase(object):

    BUFFER_SIZE = 32768

    def __init__(self):
        self.client = None
        self.su_username = None
        self.su_password = None

    def set_su_user(self, username, password=None):
        self.su_username = username
        self.su_password = password

    def get_su_username(self):
        return self.su_username

    @property
    def su_command_template(self):
        raise NotImplementedError()

    def get_su_command(self, command):
        if self.su_username:
            if re.search("'", command):
                raise SSHException(
                    'Su command may not contain single quotes. Consider using double quotes: "' +
                    command + '"')
            return self.su_command_template.format(su_username=self.su_username, command=command)
        return command

    @staticmethod
    def _resolve_dir(sftp, dst_dir):
        dst_home = sftp.normalize('.')
        dst_dir = dst_dir.split(':')[-1].replace('\\', '/')
        if dst_dir == '.':
            dst_dir = dst_home + '/'
        if not posixpath.isabs(dst_dir):
            dst_dir = posixpath.join(dst_home, dst_dir)
        return dst_dir


class SSHException(Exception):
    pass
