import os
import pytest

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture(scope='module')
def samldata():
    samlout_path = os.path.join(DATA_DIR, 'samlout.b64')
    with open(samlout_path, 'rb') as f:
        return f.read()


@pytest.fixture(scope='module')
def samldatawg():
    samlout_path = os.path.join(DATA_DIR, 'samlout-wg.b64')
    with open(samlout_path, 'rb') as f:
        return f.read()
