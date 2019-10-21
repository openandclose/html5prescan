
MEMO
====

I did basic performance tests against top 500 most popular websites.


Preliminary Test
----------------

I created long strings in the form::

    <NUM bytes of random characters><encode declaration>

random characters::

    ''.join(random.choices(string.printable)[0] for _ in range(NUM)).encode('ascii')

declarations::

    b'<meta charset="utf-8">'
    b'<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'

To parse 2000 of which:

html5prescan::

    NUM: 100        0.358 seconds
    NUM: 500        0.772 seconds
    NUM: 800        1.090 seconds

w3lib::

    NUM: 100        0.016 seconds
    NUM: 500        0.017 seconds
    NUM: 800        0.017 seconds


Data Preparation
----------------

I collected 500 urls from https://moz.com/top500 (``test/resource/top500.txt``).

I downloaded 483 files, using roughly::

    $ curl --user-agent [...] --referer <url>;auto --location --output <url> <url>

If I omit ``--user-agent`` and ``--referer`` options,
I've got mojibake files (I didn't look into the details).
An example::

    $ curl --location --output amazon.co.jp amazon.co.jp

'biglobe.ne.jp' and 'chinadaily.com.cn' returned 200 bytes of htmls,
since they use 'refresh' without redirection status code (3xx), ``curl`` didn't follow them.
I downloaded them again, changing urls to
'https://www.biglobe.ne.jp' and 'http://www.chinadaily.com.cn'.

For the 17 sites not downloaded::

    akamaihd.net
    bp.blogspot.com
    businesswire.com
    clickbank.net
    cocolog-nifty.com
    dropboxusercontent.com
    fda.gov
    geocities.jp
    gesetze-im-internet.de
    ggpht.com
    googleusercontent.com
    megaupload.com
    nhk.or.jp
    rapidshare.com
    spiegel.de
    ssl-images-amazon.com
    ytimg.com

In addition, I excluded 3 sites since they returned non-htmls::

    list-manage.com         (non-html) text
    storage.googleapis.com  xml
    photos1.blogger.com     gif

The rest are 480 sites.

As the following show,
html5prescan actually got an encoding for only 449 sites.
So I had to investigate.

I checked the existence of literal b'charset' (using ``bytes.find(b'charset')``).

15 sites (of the 31) didn't have the word::

    ask.fm
    behance.net
    bloomberg.com
    disney.com
    feedproxy.google.com
    linkedin.com
    nature.com
    office.com
    php.net
    secureserver.net
    stackoverflow.com
    symantec.com
    t.co
    thefreedictionary.com
    tinyurl.com

I checked manually the remaining 16 sites::

    adssettings.google.com
    bandcamp.com
    cnbc.com
    gizmodo.com
    goodreads.com
    groups.google.com
    issuu.com
    maps.google.com
    mashable.com
    myaccount.google.com
    news.google.com
    play.google.com
    policies.google.com
    quora.com
    support.google.com
    usatoday.com

It seems all usage of the word are
for form, javascript or style encoding declaration (except one below).

Noteworthy is 'usatody.com'.
It uses invalid ``'<meta content="text/html; charset=UTF-8" name="Content-Type" />'``.

I think I've done the preparation.
There are 480 test files, 449 of which prescan parsers should get an encoding.


Reliability
-----------

According to the byte length to parse, the results vary.
The spec recommendation (1024 bytes) only gets 88%. ::

    length: 512     passed: 343     76.391982%
    length: 1024    passed: 394     87.750557%
    length: 4096    passed: 431     95.991091%
    length: 10240   passed: 440     97.995546%
    length: 40960   passed: 447     99.554566%
    length: 102400  passed: 449     100%

For w3lib, I checked 4096 (default) and 409600 bytes,
using ``w3lib.encoding.html_body_declared_encoding``. ::

    w3lib (4096):       427
    w3lib (409600):     446

Diff between the library and w3lib (449 vs. 446)::

    books.google.com    <meta http-equiv="content-type"content="text/html; charset=UTF-8">
    mega.nz             <meta http-equiv="Content-Type" content="text/html, charset=UTF-8" />
    stuff.co.nz         <meta charset="utf-8"/>


Performance
-----------

To parse 480 inputs in memory, and get the results::

    html5prescan (1024)     0.198 seconds   (see ``Example`` below)
    html5prescan (4096)     0.350 seconds
    html5prescan (10240)    0.492 seconds
    html5prescan (102400)   2.110 seconds

    w3lib (4096)            0.019 seconds
    w3lib (409600)          0.036 seconds

Comparing at 4096, the library is about 18 times slower than w3lib.

I also checked the performance of ``lxml``'s parsing (DOM tree building)
and a DOM version of encode getting::

    lxml (parse)            2.266 seconds
    lxml (get encoding)     0.018 seconds

'2.266 seconds' seems rather long. So I might have done something wrong.
But consider that the 480 files are 123MB in size.

(Simulation of) encode getting is done by roughly::

    .xpath('/html/head/meta/@charset')
    or .xpath('/html/head/meta[@http-equiv="Content-Type"]/@content')

I also checked ``html5-chardet``,
creating a shared library from ``prescan.c``,
and calling ``prescan_a_byte_stream_to_determine_its_encoding`` from Python ``ctypes``. ::

    html5-chardet (1024)    0.001 seconds


Example
-------

To parse the first 1024 bytes of 480 webpages::

       634859 function calls in 0.196 seconds

       Ordered by: cumulative time
       List reduced from 54 to 20 due to restriction <20>

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            1    0.000    0.000    0.196    0.196 [...]/benchmark.py:231(repeat)
          480    0.001    0.000    0.195    0.000 [...]/html5prescan/scan.py:323(get)
          478    0.026    0.000    0.194    0.000 [...]/html5prescan/scan.py:80(_prescan)
         5064    0.064    0.000    0.128    0.000 [...]/html5prescan/scan.py:183(_get_an_attribute)
       222596    0.041    0.000    0.041    0.000 [...]/html5prescan/scan.py:48(get)
       144926    0.021    0.000    0.021    0.000 [...]/html5prescan/scan.py:52(next)
       145707    0.018    0.000    0.018    0.000 [...]/html5prescan/scan.py:56(is_eof)
          353    0.008    0.000    0.016    0.000 [...]/html5prescan/scan.py:245(_parse_content)
         8156    0.005    0.000    0.008    0.000 [...]/html5prescan/scan.py:61(skip)
        91702    0.006    0.000    0.006    0.000 {method 'lower' of 'bytes' objects}
          393    0.001    0.000    0.001    0.000 [...]/html5prescan/scan.py:290(_get_an_encoding)
          480    0.000    0.000    0.001    0.000 [...]/html5prescan/scan.py:70(_detect_bom)
         3229    0.001    0.000    0.001    0.000 {method 'find' of 'bytes' objects}
          831    0.000    0.000    0.001    0.000 [...]/html5prescan/scan.py:43(__init__)
         3674    0.000    0.000    0.000    0.000 {method 'isalpha' of 'bytes' objects}
         1436    0.000    0.000    0.000    0.000 {method 'startswith' of 'bytes' objects}
          393    0.000    0.000    0.000    0.000 [...]/html5prescan/scan.py:301(_get_table)
          478    0.000    0.000    0.000    0.000 [...]/html5prescan/scan.py:319(_get_python_codec_name)
          871    0.000    0.000    0.000    0.000 {method 'get' of 'dict' objects}
         1073    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
