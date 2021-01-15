---
title: nlmfedcred / Installation
---

## Pre-requisites

This software is written for CPython 3.6, and supported on Windows, Linux, and MacOS.
It should work with Anaconda and more recent distributions of Python but is not
tested on these platforms.

## Installation

This module can be installed the same way you would install any other Python package.
However, it is not distributed to the global PyPI repository, and so this
option will be presented last.

### From a tarball or cloned distribution

After expanding the tarball, change into that directory and
issue the following command:

    python setup.py install

A python sdist and binary wheel can be built as follows:

    python setup.py sdist bdist_wheel

### From a PyPI repository

If you have placed a python sdist or binary wheel into a custom PyPI respository,
and properly configured pip to use that custom repository, then you 
can install this package as follows:

    pip install nlmfedcred
