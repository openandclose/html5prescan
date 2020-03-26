
MEMO
====

Method
------

Since ``validator``, ``jsdom`` and ``html5lib`` don't have
convenient entrypoints for (Python) prescan testing,
I created a simple commandline program for each,
with the same API as this library (reading standard input).

``validator``:
    By using ``validator.htmlparser.io.MetaSniffer:sniff``.
    It doesn't do BOM checking (in this stage), so I skipped BOM related tests.

``jsdom``:
    There is a independent prescan program ``html-encoding-sniffer``.
    So I used this.

``html5lib-python``:
    By using ``html5lib._inputstream.EncodingParser:getEncoding``.
    Skipped BOM related tests and 'utf-16be/utf-16le -> utf-8' conversion tests.

``html5-chardet:``
    It has it's own ``test-prescan`` commandline program.
    So I used this directly (with ``printf`` formats edited).
    Skipped BOM related tests. Line numbers are a bit different.


Results
-------

::

    The line format is: <filename> <line number> <returned> <expected> <input byte string>.

    python check_metasniffer.py (validator):
    prescan1.dat  64 iso-8859-2 None b'<!DOCTYPE HTML>\n<meta http-equiv="Content-Type content="text/html; charset=iso8859-2">'
    prescan1.dat 161 iso-8859-2 None b'<!DOCTYPE HTML>\n<meta charset=iso8859-2">\n<p>"</p>'
    prescan1.dat 313 iso-8859-2 None b'<!DOCTYPE HTML>\n<script>document.write(\'<meta charset="ISO-8859-\' + \'2">\')</script>'
    prescan3.dat  67 None ISO-8859-2 b'<!-- no-space-separated charset following invalid charset -->\n<meta http-equiv="Content-Type" content="charsetxxxxxcharset=iso-8859-2">'
    prescan3.dat  73 None ISO-8859-2 b'<!-- no-space-separated charset immediately following invalid charset -->\n<meta http-equiv="Content-Type" content="charsetcharset=iso-8859-2">'

    python check_html_encoding_sniffer.py (jsdom):
    prescan1.dat 130 None ISO-8859-2 b'<!DOCTYPE HTML>\n<meta content="\ntext/html; charset=iso8859-2\n" http-equiv="Content-Type">'
    prescan1.dat 325 None ISO-8859-2 b'<!DOCTYPE HTML>\n<script type="text/plain"><meta charset="iso8859-2"></script>'
    prescan1.dat 331 None ISO-8859-2 b'<!DOCTYPE HTML>\n<style type="text/plain"><meta charset="iso8859-2"></style>'
    prescan1.dat 337 None ISO-8859-2 b'<!DOCTYPE HTML>\n<p><meta charset="iso8859-2"></p>'
    prescan3.dat   1 None ISO-8859-2 b"<!-- 'abrupt-closing-of-empty-comment' -->\n<!--><meta charset=iso-8859-2>-->"
    prescan3.dat   7 None ISO-8859-2 b"<!-- 'abrupt-closing-of-empty-comment' 2 -->\n<!---><meta charset=iso-8859-2>-->"
    prescan3.dat  43 None ISO-8859-2 b'<!-- insignificant spaces in quote (only in content attribute) -->\n<meta http-equiv="Content-Type" content="  text/html; charset=iso-8859-2  ">'
    prescan3.dat  67 (FREEZED) b'ISO-8859-2' b'<!-- no-space-separated charset following invalid charset -->\n<meta http-equiv="Content-Type" content="charsetxxxxxcharset=iso-8859-2">'
    prescan3.dat  73 (FREEZED) b'ISO-8859-2' b'<!-- no-space-separated charset immediately following invalid charset -->\n<meta http-equiv="Content-Type" content="charsetcharset=iso-8859-2">'
    prescan3.dat 100 None ISO-8859-2 b'<!-- https://github.com/html5lib/html5lib-python/issues/92 -->\n<meta http-equiv="Content-Type" content="charset=iso8859-2;text/html">'
    prescan3.dat 129 ISO-8859-2 None b'<meta http-equiv="refresh" http-equiv="Content-Type" content="text/html; charset=iso8859-2">'
    prescan3.dat 134 None UTF-8 b'<!-- cnn.com -->\n<meta content="IE=edge,chrome=1" http-equiv="X-UA-Compatible"><meta charset="utf-8">'

    python check_encodingparser.py (html5lib):
    prescan3.dat   1 None ISO-8859-2 b"<!-- 'abrupt-closing-of-empty-comment' -->\n<!--><meta charset=iso-8859-2>-->"
    prescan3.dat   7 None ISO-8859-2 b"<!-- 'abrupt-closing-of-empty-comment' 2 -->\n<!---><meta charset=iso-8859-2>-->"
    prescan3.dat  67 None ISO-8859-2 b'<!-- no-space-separated charset following invalid charset -->\n<meta http-equiv="Content-Type" content="charsetxxxxxcharset=iso-8859-2">'
    prescan3.dat  73 None ISO-8859-2 b'<!-- no-space-separated charset immediately following invalid charset -->\n<meta http-equiv="Content-Type" content="charsetcharset=iso-8859-2">'
    prescan3.dat 100 None ISO-8859-2 b'<!-- https://github.com/html5lib/html5lib-python/issues/92 -->\n<meta http-equiv="Content-Type" content="charset=iso8859-2;text/html">'
    prescan3.dat 106 None ISO-8859-2 b"<!-- continuous open tag '<' -->\n<<meta charset=iso-8859-2>"
    prescan3.dat 112 iso-8859-2 None b'<!-- just skip to \'>\' when \'</\' is found -->\n</xxx<attribute="<meta charset=iso-8859-2>"'
    prescan3.dat 118 iso-8859-2 ISO-8859-3 b'<!-- just skip to \'>\' when \'</\' is found 2 -->\n</xxx<attribute="<meta charset=iso-8859-2><meta charset=iso-8859-3>"'
    prescan3.dat 129 iso-8859-2 None b'<meta http-equiv="refresh" http-equiv="Content-Type" content="text/html; charset=iso8859-2">'

    [...]/html5-chardet/test-prescan -v prescan*.dat (html5-chardet):
    prescan3.dat  71 (null) iso-8859-2 '<!-- no-space-separated charset following invalid charset -->\n<meta http-equiv="Content-Type" content="charsetxxxxxcharset=iso-8859-2">'
    prescan3.dat  77 (null) iso-8859-2 '<!-- no-space-separated charset immediately following invalid charset -->\n<meta http-equiv="Content-Type" content="charsetcharset=iso-8859-2">'


2020/03/26
----------

``validator/htmlparser`` had two kinds of bugs, which the maintainer confirmed.

* https://github.com/validator/validator/issues/874
* https://github.com/validator/validator/issues/877

``jsdom/html-encoding-sniffer`` had five kinds of bugs,
four of which I reported and the maintainer confirmed and fixed.
(one is fixed independently from me).

* https://github.com/jsdom/html-encoding-sniffer/issues/4
* https://github.com/jsdom/html-encoding-sniffer/issues/6
* https://github.com/jsdom/html-encoding-sniffer/issues/7
* https://github.com/jsdom/html-encoding-sniffer/issues/8

* https://github.com/jsdom/html-encoding-sniffer/commit/0c03ceb824db737bdf0ed54de2224b740832d9da

I think ``html5lib/html5lib-python`` has five kinds of bugs
(I've got no responses yet).

* https://github.com/html5lib/html5lib-python/issues/427
* https://github.com/html5lib/html5lib-python/issues/434
* https://github.com/html5lib/html5lib-python/issues/435
* https://github.com/html5lib/html5lib-python/issues/436
* https://github.com/html5lib/html5lib-python/issues/437
