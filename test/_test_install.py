
"""Test installation."""

import os
import subprocess
import tempfile

DATA = b'<meta charset=greek>'


def _test_import():
    expected = ('greek', 'ISO-8859-7', 'ISO-8859-7')

    import html5prescan
    assert html5prescan.get(DATA) == (expected, DATA)


def _test_commandline():
    cmd = ['html5prescan']
    expected = b"('greek', 'ISO-8859-7', 'ISO-8859-7')\n"

    ret = subprocess.run(cmd, input=DATA, stdout=subprocess.PIPE)
    assert ret.stdout == expected


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
