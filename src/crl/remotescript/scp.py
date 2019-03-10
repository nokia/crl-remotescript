"""
Not Implented. File sending via SSH using the scp1 protocol.
"""

__copyright__ = 'Copyright (C) 2019, Nokia'


class SCPClient(object):

    def __init__(self, transport):
        pass

    def put(self, files, remote_path='.', mode=None,
            recursive=False, preserve_times=False):
        raise NotImplementedError()

    def get(self, remote_path, local_path='',
            recursive=False, preserve_times=False):
        raise NotImplementedError()
