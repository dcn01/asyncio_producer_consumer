#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('requirements/base.pip') as f:
    BASE_REQS = f.read().splitlines()

with open('requirements/setup.pip') as f:
    SETUP_REQS = f.read().splitlines()

with open('requirements/test.pip') as f:
    TEST_REQS = f.read().splitlines()

with open('requirements/dev.pip') as f:
    DEV_REQS = f.read().splitlines()

with open('requirements/docs.pip') as f:
    DOCS_REQS = f.read().splitlines()

setup(
    name='async_producer_consumer',
    author='yoyonel',
    url='',
    use_scm_version=False,
    packages=['yoyonel.{}'.format(x) for x in find_packages('src/yoyonel')],
    package_dir={'': 'src'},
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    keywords=[

    ],
    install_requires=BASE_REQS,
    setup_requires=SETUP_REQS,
    extras_require={
        'test': TEST_REQS,
        'develop': TEST_REQS + DEV_REQS,
        'docs': DOCS_REQS
    },
    entry_points={
        'console_scripts': []
    },
    python_requires='>=3.7'
)
