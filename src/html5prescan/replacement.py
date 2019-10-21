r"""
An implementation of the 'replacement' encoding.

For decoding,
If input is blank byte, return blank str.
Otherwise return one '\ufffd' for any length of bytes.

For IncrementalDecoder, resetting is possible.
Which means the next string is the second '\ufffd'.

For StreamReader, restting has no efect.

For encoding, raise UnicodeError.
(Codec.encode, IncrementalEncoder.encode, StreamWriter.encode)


    >>> encoding = Codec()
    >>> encoding.decode(b'')
    ('', 0)
    >>> encoding.decode(b'abcde')
    ('\ufffd', 5)

    >>> decoder = IncrementalDecoder()
    >>> tuple(decoder.decode(b) for b in b'abcde')
    ('\ufffd', '', '', '', '')
    >>> tuple(decoder.decode(b) for b in b'abcde')
    ('', '', '', '', '')
    >>> decoder.reset()
    >>> tuple(decoder.decode(b) for b in b'abcde')
    ('\ufffd', '', '', '', '')

    >>> import io
    >>> reader = StreamReader(io.BytesIO(b'abcde'))
    >>> reader.read()
    '\ufffd'
    >>> reader = StreamReader(io.BytesIO(b'abcde'))
    >>> reader.readline()
    '\ufffd'
    >>> reader = StreamReader(io.BytesIO(b'abcde'))
    >>> reader.readlines()
    ['\ufffd']
    >>> reader.seek(0, 0)
    >>> reader.read()
    ''
    >>> reader.reset()
    >>> reader.read()
    ''
"""

import codecs


class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        msg = "replacement encoding doesn't have an encoder"
        raise UnicodeError(msg)

    def decode(self, input, errors='strict'):
        if not input:
            return ('', 0)
        return ('\ufffd', len(input))


class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        msg = "replacement encoding doesn't have an encoder"
        raise UnicodeError(msg)


class IncrementalDecoder(codecs.IncrementalDecoder):
    def __init__(self, errors='strict'):
        super().__init__(errors)
        self.state = 0

    def decode(self, input, final=False):
        if not input:
            return ''
        if self.state:
            return ''
        else:
            self.state = 1
            return '\ufffd'

    def reset(self):
        self.state = 0

    def getstate(self):
        return (b'', self.state)

    def setstate(self, state):
        self.state = state[1]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    def __init__(self, stream, errors='strict'):
        super().__init__(stream, errors)
        self.state = 0

    def decode(self, input, final=False):
        if getattr(input, 'seek', None):
            input.seek(0, 2)
            length = input.tell()
        else:
            length = len(input)

        if length == 0:
            return ('', length)
        if self.state:
            return ('', length)
        else:
            self.state = 1
            return ('\ufffd', length)


def getregentry():
    return codecs.CodecInfo(
        name='replacement',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )


def register():
    def search_function(name):
        if name == 'replacement':
            return getregentry()
    codecs.register(search_function)
