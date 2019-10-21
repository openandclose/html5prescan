
"""
Test against data files.

Date files are derived from ``html5lib-tests/encoding``.
The format is the same.
"""

import sys

import support


def test(on_error='error'):
    for (i, encoding, data, fname) in support.read_datafiles():

        ret = support.scan.get(data)
        ret = ret[0][1]
        if ret is None:
            ret = 'None'

        encoding = encoding.decode('ascii')

        if ret != encoding:
            print(fname, '%3d' % i, ret, encoding, data)
            if on_error == 'error':
                raise ValueError("'test_data.py' failed.")


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] in ('i', '-i', '--ignore'):
        test(on_error='ignore')
    else:
        test()
