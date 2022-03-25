
# -*- coding: utf-8 -*-
from setuptools import setup

import codecs

INSTALL_REQUIRES = []

setup_kwargs = {
    'name': 'plog',
    'version': '1.0',
    'description': 'log the invoke-status for a function',
    'license': 'UNKNOWN',
    'author': 'Cread Sun',
    'author_email': 'Cread Sun <865363864@qq.com>',
    'url': 'https://github.com/creadsun/plog_wrapper',
    'packages': [],
    'package_data': {'': ['*'], 'plog': ['**/*']},
    'long_description_content_type': 'text/markdown',
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Senses-AI',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Build Tools',
    ],
    'install_requires': INSTALL_REQUIRES,
    'python_requires': '>=3.8,<4.0',

}


setup(**setup_kwargs)
