#!/usr/bin/env python

"""
Prescan a byte string and return WHATWG and Python encoding names.

As a commandline script, it reads standard input,
and return 'Encoding Label', 'Encoding Name', 'Python codec name',
and the match details.

    $ html5prescan
    <meta charset=greek>
    (CTRL+D)
    Scan(label='greek', name='ISO-8859-7', pyname='ISO-8859-7',
        start=0, end=20, match='<meta charset=greek>')
"""

from collections import namedtuple
import json
import os

SPACES = (b'\t', b'\n', b'\f', b'\r', b' ')

NULL = object()

TABLE = {}

PYTHON_NAMES = {
    'ISO-8859-8-I': 'iso8859_8',
    'windows-874': 'cp874',
    'x-mac-cyrillic': 'mac_cyrillic',
    'replacement': None,
    'x-user-defined': 'windows-1252',
}

Scan = namedtuple(
    'Scan', ['label', 'name', 'pyname', 'start', 'end', 'match'])


class Buffer(object):
    """A wrapper object for bytes manupilation.

    :param buf: a bytes object

    Note ``get()`` doesn't advance the position.
    Note ``next()`` is callable multiple times at the last position.
    """

    def __init__(self, buf):
        self.buf = buf
        self.pos = 0
        self.end = len(self.buf) - 1

    def get(self, num=1):
        pos = self.pos
        return self.buf[pos:pos + num]  # EOF is b''.

    def next(self, num=1):
        # self.pos = min(self.pos + num, self.end + 1)
        self.pos = self.pos + num

    def is_eof(self):
        if self.pos > self.end:
            return True
        return False

    def skip(self, *chars):
        # Skip argument characters e.g. whitespaces, and advance the position.
        while self.pos <= self.end:
            c = self.get()
            if c not in chars:
                return c
            self.next()


def _detect_bom(buf):
    if buf.startswith(b'\xEF\xBB\xBF'):
        return 'UTF-8', 2, 'EFBBBF', buf[3:]
    if buf.startswith(b'\xFE\xFF'):
        return 'UTF-16BE', 1, 'FEFF', buf[2:]
    if buf.startswith(b'\xFF\xFE'):
        return 'UTF-16LE', 1, 'FFFE', buf[2:]
    return None, None, None, buf


def _prescan(buf, length=1024, jsonfile=None):  # noqa: C901 too complex (32)
    """Return a tuple: (Encoding Label, Encoding Name, startpos, endpos).

    The last two indicate the position of matched b'<meta...>' substring.
    """
    buf = Buffer(buf[:length + 1])
    get = buf.get
    next = buf.next
    EOF = buf.is_eof
    _m_start = 0  # startpos, not in the spec.

    while not EOF():
        # shortcut, not in the spec.
        index = buf.buf.find(b'<', buf.pos)
        if index == -1:
            break
        else:
            next(index - buf.pos)

        if get(4) == b'<!--':
            next(4)
            if get() == b'>':
                pass
            elif get(2) == b'->':
                next()
            else:
                while not EOF():
                    if get(3) == b'-->':
                        next(2)
                        break
                    next()
        elif get(5).lower() == b'<meta':
            _m_start = buf.pos
            next(5)
            if get() in (*SPACES, b'/'):
                next()
                attribute_list = []
                got_pragma = False
                need_pragma = NULL
                charset = NULL
                label = None  # this is an addition, not in the spec.
                while not EOF():
                    attribute = _get_an_attribute(buf)
                    name, value = attribute
                    if name == b'' and value == b'':
                        break
                    if name not in attribute_list:
                        attribute_list.append(name)
                        if name == b'http-equiv':
                            if value == b'content-type':
                                got_pragma = True
                        elif name == b'content':
                            ret = _parse_content(value, jsonfile)
                            label_, charset_ = ret
                            if charset_:
                                if charset is NULL:
                                    label, charset = label_, charset_
                                    need_pragma = True
                        elif name == b'charset':
                            ret = _get_an_encoding(value, jsonfile)
                            label, charset = ret
                            need_pragma = False

                if need_pragma is NULL:
                    pass
                elif need_pragma is True and not got_pragma:
                    pass
                elif charset in (NULL, None):
                    pass
                else:
                    if charset in ('UTF-16LE', 'UTF-16BE'):
                        charset = 'UTF-8'
                    if charset == 'x-user-defined':
                        charset = 'windows-1252'
                    return label, charset, _m_start, buf.pos
                continue
        elif (get() == b'<'
                and (get(2)[1:2].isalpha()
                        or (get(2) == b'/' and get(3)[2:3].isalpha()))):
            if get(2)[1:2].isalpha():
                next(2)
            else:
                next(3)
            while not EOF():
                if get() in (*SPACES, b'>'):
                    break
                next()
            while not EOF():
                attribute = _get_an_attribute(buf)
                name, value = attribute
                if name == b'' and value == b'':
                    break
            continue
        elif get(2) in (b'<!', b'</', b'<?'):
            next(2)
            while not EOF():
                if get() == b'>':
                    break
                next()
        next()  # next byte

    return None, None, 0, 0  # reached EOF


def _get_an_attribute(buf):
    get = buf.get
    next = buf.next
    EOF = buf.is_eof

    buf.skip(*SPACES, b'/')
    if get() == b'>':
        next()
        return (b'', b'')

    name = b''
    value = b''

    # getting name
    while not EOF():
        c = get()
        if c == b'=' and name != b'':
            next()
            if EOF(): return (name, b'')
            break
        elif c in SPACES:
            next()
            buf.skip(*SPACES)
            if get() != b'=':
                return (name, b'')
            next()
            break
        elif c in (b'/', b'>'):
            return (name, b'')
        else:
            name += c.lower()
        next()
    if EOF(): return (b'', b'')

    # getting value
    buf.skip(*SPACES)
    c = get()
    if c in (b'"', b"'"):
        next()
        while not EOF():
            if get() == c:
                next()
                return (name, value)
            else:
                value += get().lower()
            next()
        if EOF(): return (name, b'')

    elif c == b'>':
        return (name, b'')
    else:
        value += c.lower()
    next()
    while not EOF():
        if get() in (*SPACES, b'>'):
            return (name, value)
        else:
            value += get().lower()
        next()
    return (name, b'')


def _parse_content(value, jsonfile):
    # Return a tuple: (Encoding Label, Encoding Name).
    buf = Buffer(value)
    get = buf.get
    next = buf.next
    EOF = buf.is_eof

    # getting 'charset' and '='
    while not EOF():
        if get(7).lower() == b'charset':
            next(7)
            buf.skip(*SPACES)
            if get() != b'=':
                continue
            else:
                next()
                break
        next()
    if EOF(): return None, None

    # getting Encoding Label
    buf.skip(*SPACES)
    start = buf.pos
    if get() in (b'"', b"'"):
        quote = get()
        next()
        while not EOF():
            if get() == quote:
                end = buf.pos
                label = buf.buf[start + 1:end]
                return _get_an_encoding(label, jsonfile)
            next()
        return None, None
    else:
        while not EOF():
            if get() in (*SPACES, b';'):
                end = buf.pos
                break
            next()
        if EOF():
            end = buf.pos + 1
        label = buf.buf[start:end]
        return _get_an_encoding(label, jsonfile)


def _get_an_encoding(label, jsonfile=None):
    label = label.strip(b''.join(SPACES)).lower()
    label = label.decode('ascii', errors='ignore')
    table = _get_table(jsonfile)
    name = table.get(label, None)
    if name is None:
        return (None, None)
    else:
        return (label, name)


def _get_table(jsonfile=None):
    global TABLE
    if TABLE:
        return TABLE
    if jsonfile is None:
        d = os.path.abspath(os.path.dirname(__file__))
        jsonfile = os.path.join(d, 'encodings.json')
    with open(jsonfile) as f:
        data = json.load(f)
    TABLE = {
        label: encoding['name']
        for category in data
        for encoding in category['encodings']
        for label in encoding['labels']
    }
    return TABLE


def _get_python_codec_name(name):
    return PYTHON_NAMES.get(name, name)


def get(buf, length=1024, jsonfile=None):
    """Prescan a byte string and return WHATWG and Python encoding names.

    :param buf: input byte string. It must be a ``bytes`` type.
    :param length: scan to this byte position at most.
    :param jsonfile: a filename to open.
            if ``None``, the library uses the local copy of
            WHATWG's ``encodings.json`` to resolve Encoging Labels to Names.
            if other than ``None``, the library uses that instead.
            So it must be the same format.

    :return: tuple (Scan, buf)

    ``Scan`` is a ``namedtuple`` with fields::

        label:  Encoding Label
        name:   Encoding Name
        pyname: Python codec name
        start:  start position of the match
        end:    end position of the match
        match:  matched substring

    The ``match`` is from ``'<meta'`` to the byte position
    where successful parsing returned.

    ---

    First, it checks UTF-8 and UTF-16 BOM, and if it finds one,
    it returns ``Scan`` and BOM-stripped buf.

    ``label``, ``name``, and ``pyname`` are always the same,
    ``start`` is ``0``, ``end`` is BOM end (``1`` or ``2``),
    and ``match`` is a BOM hint
    (unicode string 'EFBBBF', 'FEFF', or 'FFFE').

    e.g. ``(UTF-8, UTF-8, UTF-8, 0, 2, 'EFBBBF')``.

    ---

    Second, it does prescan, retrieve WHATWG Encoding Name or ``None``.

    Third, it resolves the Name to a Python counterpart
    (just codec name, not codec object).
    If the Name is 'replacement', ``pyname`` is ``None``.

    Return ``Scan`` and buf (unchanged).

    ---

    Note:

    In prescan, invalid Labels are discarded,
    so the ``label`` and ``name`` are always
    either ``None, None`` or ``(valid) Label, (valid) Name``.

    Thus, the combinations of ``None`` in the encoding fields are just two.
    ``None, None, None``
    or ``'<one of replacement Labels>', 'replacement', None``.
    """
    if not isinstance(buf, bytes):
        raise ValueError('Input must be bytes. got %r.' % type(buf))

    encoding, end, bom, buf = _detect_bom(buf)
    if encoding:
        return Scan(encoding, encoding, encoding, 0, end, bom), buf

    label, name, start, end = _prescan(buf, length, jsonfile)
    match = buf[start:end]
    pyname = _get_python_codec_name(name)
    if pyname:
        match = match.decode(pyname, 'backslashreplace')
    else:
        match = match.decode('ascii', 'backslashreplace')
    return Scan(label, name, pyname, start, end, match), buf


def main():
    import sys
    if len(sys.argv) == 1:
        print(get(sys.stdin.buffer.read())[0])
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
