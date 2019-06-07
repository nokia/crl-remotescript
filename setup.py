# -*- coding: utf-8 -*-

import os
import sys
import importlib
from setuptools import setup, find_packages


__copyright__ = 'Copyright (C) 2019, Nokia'

VERSIONFILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'src', 'crl', 'remotescript', '_version.py')


def get_version():
    if sys.version_info.major == 2:
        import imp
        return imp.load_source('_version', VERSIONFILE).get_version()
    spec = importlib.util.spec_from_file_location('_version', VERSIONFILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_version()


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='crl.remotescript',
    version=get_version(),
    author='Zoltán Veres',
    author_email='zoltan.veres@nokia.com',
    description='Robot test library for executing shell commands and scripts over SSH '
                'and Telnet and transferring files over SFTP, SCP and FTP protocols',
    install_requires=['robotframework', 'paramiko'],
    long_description=read('README.rst'),
    license='BSD-3-Clause',
    classifiers=['Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Software Development'],
    keywords='SSH Telnet SFTP FTP',
    url='https://github.com/nokia/crl-remotescript',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['crl'],
    entry_points={'robotdocsconf': [
        'robotdocsconf = crl.remotescript.robotdocsconf:robotdocs']}
)
