#!/usr/bin/env python
import os
import subprocess

from setuptools import setup, find_packages


def get_version():
    if os.path.isfile('VERSION.txt'):
        with open('VERSION.txt', 'r') as f:
            version = f.read().strip()
    else:
        version = '0.0.1'
    return version


setup(
    name='nlmfedcred',
    version=get_version(),
    description='Utility for Federating Credentials with AWS',
    author='Dan Davis',
    author_email='daniel.davis@nih.gov',
    packages=find_packages(),
    include_package_data=True,
    scripts=['bin/getawscreds.py'],
    install_requires=['awscli', 'boto3', 'bs4', 'requests', 'beautifulsoup4', 'lxml'],
    tests_require=['pytest', 'tox'],
    entry_points= {'console_scripts': [
        'getawscreds = nlmfedcred.cli:execute_from_command_line',
    ]},
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: Public Domain',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Mocrosoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: System Administration',
        'Topic :: Utilities',
    ],
)

