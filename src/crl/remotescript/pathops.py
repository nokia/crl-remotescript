__copyright__ = 'Copyright (C) 2019, Nokia'


def append(path, extension):
    path = path.rstrip('/')
    extension = extension.rstrip('/')
    return path + extension


def join(path1, path2):
    path1 = path1.rstrip('/')
    path2 = path2.rstrip('/')
    return path1 + '/' + path2


def directorize(path):
    path = path.replace('//', '/')
    path = path.rstrip('/')
    return path + '/'


def unic(out):
    try:
        return unicode(out, errors='replace')
    except ValueError:
        return out
