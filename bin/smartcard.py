#!/usr/bin/env python3
import os
import sys

lib_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, lib_dir)

from nlmfedcred import smartcard

if __name__ == '__main__':
    sys.exit(smartcard.main())
