
"""html5prescan setup file."""

from setuptools import setup, find_packages

description = """
Prescan a byte string and return WHATWG and Python encoding names.
"""

readme = """
%s

See https://github.com/openandclose/html5prescan

License: MIT
"""

description = description.strip()
readme = readme.strip() % description

with open('VERSION') as f:
    version = f.read().strip()


setup(
    name='html5prescan',
    version=version,
    url='https://github.com/openandclose/html5prescan',
    license='MIT',
    author='Open Close',
    author_email='openandclose23@gmail.com',
    description=description,
    long_description=readme,
    # https://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Utilities',
    ],
    keywords='html html5 WHATWG prescan sniff meta charset',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'html5prescan = html5prescan.scan:main',
        ],
    },
    python_requires='~=3.5',
    zip_safe=False,
)
