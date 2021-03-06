#!/usr/bin/env python
import os
import shutil
from distutils.command import clean

from setuptools import find_packages, setup


def get_version():
    if os.path.isfile('VERSION.txt'):
        with open('VERSION.txt', 'r') as f:
            version = f.read().strip()
    else:
        version = '0.0.1'
    return version


def get_readme():
    with open('README.md') as f:
        return f.read()


class PurgeCommand(clean.clean):
    description = "Purge 'build', 'dist', and '*.egg-info' directiories"

    def run(self):
        super().run()
        if not self.dry_run:
            for path in ['build', 'dist', 'nlmfedcred.egg-info']:
                os.path.isdir(path) and shutil.rmtree(path)


setup(
    name='nlmfedcred',
    version=get_version(),
    description='Utility for Federating Credentials with AWS',
    long_description=get_readme(),
    long_description_content_type='text/markdown; charset=UTF-8; variant=CommonMark',
    author='Dan Davis',
    author_email='daniel.davis@nih.gov',
    url='https://github.com/NLM-OCCS/nlmfedcred',
    packages=find_packages(),
    include_package_data=True,
    scripts=['bin/getawscreds.py', 'bin/awscreds.cmd', 'bin/awscreds-func.sh'],
    install_requires=[
        'boto3',
        'bs4',
        'requests',
        'beautifulsoup4',
        'lxml',
        'cryptography',
        "pywin32; sys_platform=='win32'",
    ],
    extras_require={
        'smartcard': ['PyKCS11'],
    },
    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-pythonpath',
        'pytest-mock',
    ],
    cmdclass={
        'purge': PurgeCommand,
    },
    entry_points={'console_scripts': [
        'getawscreds = nlmfedcred.cli:main',
        'smartcard = nlmfedcred.smartcard:main',
    ]},
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: Public Domain',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: System Administration',
        'Topic :: Utilities',
    ],
    python_requires=">=3.5",
)
