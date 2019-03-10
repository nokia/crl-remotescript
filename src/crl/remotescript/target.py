__copyright__ = 'Copyright (C) 2019, Nokia'


class Target(object):
    """
    Remote target in [crl.remotescript.RemoteScript.html|RemoteScript] library.
    Targets are added to RemoteScipt library with
    [crl.remotescript.RemoteScript.html#Set Target|Set Target] keyword.
    """

    def __init__(self, host, username, protocol='ssh/sftp'):
        """
        Target for remote script executions.

        *Arguments:*\n
        _host_: Host name or ip address of the target host.\n
        _username_: User name for login to _host_.\n
        _protocol_: Protocol for connecting the target (\"telnet\",
        \"ssh/sftp\", \"ssh/scp\" or \"ftp\").\nValue \"ssh\" is mapped
        to default \"ssh/sftp\". Value is case insensitive.\n

        After Instatiating, the target must be initialized with:\n
        `set_password` *or*
        `set_ssh_key_file`
        """
        self.host = host
        self.username = username
        self.protocol = protocol.lower()  # Makes life easier.
        self.properties = dict()
        self.password = None
        self.sshkeyfile = None

    def set_password(self, password):
        """
        _password_: Password for the _username_.
        """
        self.password = password

    def set_ssh_key_file(self, file_):
        """
        _sshkeyfile_: optional ssh private key file for the _username_.
        """
        self.sshkeyfile = file_

    @property
    def port(self):
        return self.properties.get('port')

    def __str__(self):
        str_components = []
        for attr in ['host', 'username', 'protocol', 'password', 'sshkeyfile']:
            value = getattr(self, attr)
            if value is not None:
                str_components.append((attr, value))
        if self.port is not None:
            str_components.append(('port', self.port))
        return ' '.join(['{}={}'.format(name, val) for name, val in str_components])
