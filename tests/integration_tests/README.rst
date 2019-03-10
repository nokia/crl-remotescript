.. Copyright (C) 2019, Nokia

To run these tests with ``crl.remotescript`` you should change ``__init__.py`` in
``libraries/RemoteScript`` like this::

    import logging

    try:
        from crl.remotescript import *
    except:
        from RemoteScript.RemoteScript import RemoteScript
        from RemoteScript.FP import FP
