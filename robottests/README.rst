.. Copyright (C) 2019, Nokia


Running and developing Robot framework tests
============================================

To run tests, supplement targethosts.py file, which has
two HOSTS.
HOSTS are dict objects which need to have the following attributes:
- host (e.g. localhost)
- user (e.g. examplename)
In addition, HOST1 needs to have a regular password (e.g. 'password': 'password')
while HOST2's needs to have keyfile for ssh authentication.
e.g. 'key': '/root/.ssh/rsa_keys'
The keys need to be Ed25519 keys.

To run tests in docker simply type::

   tox -e docker-robottests

and robottests for python 2 and 3 are run inside docker.

To manually run robottests, e.g. for python 2, run the following command::

   tox -e {environment} {posargs}

In practise this means for example::

   tox -e robottests2 -- -V robottests/targethosts.py --exclude skip -b debug.log
