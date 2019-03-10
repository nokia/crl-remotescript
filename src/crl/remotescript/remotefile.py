__copyright__ = 'Copyright (C) 2019, Nokia'


class RemoteFile(object):

    @staticmethod
    def write(data):
        raise NotImplementedError()

    @staticmethod
    def chmod(mode):
        raise NotImplementedError()

    @staticmethod
    def close():
        raise NotImplementedError()
