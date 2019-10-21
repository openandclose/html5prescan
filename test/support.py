
"""Support functions for testing."""

import os
import sys

TESTDIR = os.path.abspath(os.path.dirname(__file__))
SRCDIR = os.path.join(os.path.dirname(TESTDIR), 'src')
sys.path.insert(0, SRCDIR)
import html5prescan.scan as scan  # noqa E402 import not at the top, F401 'scan' not used
del sys.path[0]

DATAFILES = (
    os.path.join(TESTDIR, 'prescan1.dat'),
    os.path.join(TESTDIR, 'prescan2.dat'),
    os.path.join(TESTDIR, 'prescan3.dat'),
)


def read_datafiles():
    yield from _read_datafiles(DATAFILES)


def _read_datafiles(datafiles):
    for datafile in datafiles:
        fname = os.path.basename(datafile)
        for linenum, data, encoding in _read_data(datafile):
            yield (linenum, encoding, data, fname)


def _read_data(datafile):
    with open(datafile, 'rb') as f:
        data = b''
        encoding = None
        state = None
        i = 0
        linenum = 0
        for line in f:
            i += 1
            if not line.strip():
                continue
            if line.rstrip() == b'#data':
                if data and encoding:
                    yield linenum, data.rstrip(b'\n'), encoding
                    data = b''
                linenum = i
                state = 'data'
            elif line.rstrip() == b'#encoding':
                state = 'encoding'
            else:
                if state == 'data':
                    data = data + line
                elif state == 'encoding':
                    encoding = line.strip()

        if data and encoding:
            yield linenum, data.rstrip(b'\n'), encoding
