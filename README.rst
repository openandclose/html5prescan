
html5prescan
============

This is a python3.5+ library, mainly does what WHATWG html5 spec calls 'prescan'.

1. (Additionally) Check UTF-8 and UTF-16 BOM
2. Prescan (parse <meta> tag to get Encoding Name)
3. (Try to) Resolve the retrieved Name to a Python codec name

Note It just returns Python codec *name*, not codec object.


Install
-------

.. code-block:: bash

    $ pip install html5prescan


API
---

.. code-block:: python

    html5prescan.get(buf, length=1024, jsonfile=None)

Parse input byte string ``buf``, and return ``(Scan, buf)``.

``Scan`` is a ``namedtuple`` with fields::

    label:  Encoding Label
    name:   Encoding Name
    pyname: Python codec name
    start:  start position of the match
    end:    end position of the match
    match:  matched substring

The ``match`` is from ``'<meta'`` to the byte position
where successful parsing returned.

``Encoding Label`` and ``Encoding Name`` are defined
in `WHATWG Encoding <https://encoding.spec.whatwg.org/#names-and-labels>`__.
The site provides ``encodings.json`` file for convenience,
and the library uses the copy of it, when ``jsonfile`` argument is ``None``.

See the docstring of ``html5prescan.get`` for the details
(e.g. ``$ pydoc 'html5prescan.get'``).

---

As a commandline script, if there is no argument,
it reads standard input, and return ``Scan``.

.. code-block:: bash

    $ html5prescan
    <meta charset=greek>
    (CTRL+D)
    Scan(label='greek', name='ISO-8859-7', pyname='ISO-8859-7',
        start=0, end=20, match='<meta charset=greek>')

In any other cases, it just prints help message.


Testing
-------

To test, run ``make test``.


Test Data
---------

The test data files are derived from ``html5lib/encoding/tests*.dat`` files.
The original ones are tests for the entire html parsing, not for prescan proper,
so I edited them (``prescan1.dat`` and ``prescan2.dat``).

See the first six commits for the diffs.

I also added some more tests ad hoc (``prescan3.dat``).

Then, I tested the test data against well-known libraries
(``validator``, ``jsdom``, ``html5lib``).
For non-obvious inconsistencies, that is,
the ones I particularly wanted to make sure, I reported them upstream.

For validator, I think the reporting is done.
(So the library is, in a way, a validator conformant).

For the details, see ``test/resource/memo/201910-comparison.rst``.


Performance
-----------

The library imitates WHATWG prescan algorithm in Python code
(countless small bytes slicing and copying).
So it is naturally slow.
But It is better to know how slow.

``scrapy/w3lib`` uses well maintained, therefore, relatively complex, regex search
to get encoding declaration.
(I think regex is mostly done in C or below in Python.)

From my humble tests,
I've got the result that the library is about 20 times slower than w3lib.

I think this is in the range of expectation,
not good, but not bad either.

For the details, see ``test/resource/memo/201910-performance.rst``.


Replacement Encoding
--------------------

Around 2013, WHATWG introduced a new encoding called 'replacement'.
It is to mask some insecure non-ascii-compatible encodings,
and it just *decodes* to one ``U+FFFD`` unicode for any length of the input bytes.

Python doesn't have a codec corresponding to this encoding,
and this library returns ``None`` for ``pyname``.
Users may need to add an extra check for this encoding.

The library includes an implementation of this codec (``replacement.py``).
So in very rare cases, users may want to look at it.

If users want to register this codec, call ``replacement.register()``.


Similar projects
----------------

https://github.com/zackw/html5-chardet

It is a C version of validator's ``MetaScanner.java``.
He also uses html5lib tests edited for prescan.
So I am obviously following his path.


Reference
---------

Relevant WHATWG html specs for prescan are:

* https://html.spec.whatwg.org/multipage/parsing.html#prescan-a-byte-stream-to-determine-its-encoding
* https://html.spec.whatwg.org/multipage/parsing.html#concept-get-attributes-when-sniffing
* https://html.spec.whatwg.org/multipage/urls-and-fetching.html#extracting-character-encodings-from-meta-elements

Is is just a part of the initial encode determination process.

* https://html.spec.whatwg.org/multipage/parsing.html#determining-the-character-encoding

---

validator, jsdom, html5-lib, w3lib:

* https://github.com/validator/htmlparser
* https://github.com/jsdom/html-encoding-sniffer
* https://github.com/html5lib/html5lib-python
* https://github.com/scrapy/w3lib


License
-------

The software is licensed under The MIT License. See `LICENSE`_.

.. _LICENSE: https://github.com/openandclose/html5prescan/blob/master/LICENSE
