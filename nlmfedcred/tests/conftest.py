import os

import pytest

# Safe from KeyError
os.environ.pop('AWS_PROFILE', None)
os.environ.pop('AWS_DEFAULT_PROFILE', None)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture(scope='module')
def samldata():
    samlout_path = os.path.join(DATA_DIR, 'samlout.b64')
    with open(samlout_path, 'rb') as f:
        return f.read()


@pytest.fixture(scope='module')
def samldata_wg():
    samlout_path = os.path.join(DATA_DIR, 'samlout-wg.b64')
    with open(samlout_path, 'rb') as f:
        return f.read()


@pytest.fixture(scope='module')
def samldata_sysop():
    samlout_path = os.path.join(DATA_DIR, 'samlout-sysop.b64')
    with open(samlout_path, 'rb') as f:
        return f.read()
