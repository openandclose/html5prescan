
"""Test installation."""

import os
import subprocess
import tempfile

DATA = b'<meta charset=greek>'


def _test_import():
    expected = (
        'greek', 'ISO-8859-7', 'ISO-8859-7', 0, 20, '<meta charset=greek>')

    import html5prescan
    scan, data = html5prescan.get(DATA)
    assert scan[:] == expected
    assert data == DATA


def _test_commandline():
    cmd = ['html5prescan']
    expected = ("Scan(label='greek', name='ISO-8859-7', pyname='ISO-8859-7'"
        ", start=0, end=20, match='<meta charset=greek>')\n")
    ret = subprocess.run(cmd, input=DATA, stdout=subprocess.PIPE)
    assert ret.stdout.decode() == expected


def _test_register():
    import html5prescan.replacement as replacement
    replacement.register()
    assert DATA.decode('replacement') == '\ufffd'


def _run(func):
    with tempfile.TemporaryDirectory(prefix='html5prescan-') as tmpdir:
        os.chdir(tmpdir)
        func()


def run():
    _run(_test_import)
    _run(_test_commandline)
    _run(_test_register)

if __name__ == '__main__':
    run()
