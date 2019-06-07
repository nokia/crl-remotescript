# pylint: disable=redefined-builtin
from crl.remotescript import RemoteScript
from crl.remotescript import FP


__copyright__ = 'Copyright (C) 2019, Nokia'


def test_import_base_library():
    lib = RemoteScript()
    assert hasattr(lib, 'set_target')
    del lib


def test_import_fp_library():
    lib = FP()
    assert hasattr(lib, 'execute_command_in_node')
    del lib


def test_import_noexitstatuserror():
    from crl.remotescript import NoExitStatusError
    e = NoExitStatusError
    assert issubclass(e, Exception)
    del e


def test_import_nonzeroexitstatuserror():
    from crl.remotescript import NonZeroExitStatusError
    e = NonZeroExitStatusError
    assert issubclass(e, Exception)
    del e


def test_import_executionerror():
    from crl.remotescript import ExecutionError
    e = ExecutionError
    assert issubclass(e, Exception)
    del e


def test_import_timeouterror():
    from crl.remotescript import TimeoutError
    e = TimeoutError
    assert issubclass(e, Exception)
    del e
