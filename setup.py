#!/usr/bin/env python

import os
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='python-cloudflare-v4',
    version='1.1',
    description='Python wrapper for the CloudFlare v4 API',
    author='gnowxilef,Martin J. Levy',
    author_email='felix@fawong.com,martin@cloudflare.com',
    url='https://github.com/cloudflare/python-cloudflare',
    packages=['cli4']+find_packages(),
    install_requires=required,
    entry_points={
	'console_scripts': [
	    'cli4 = cli4.__main__:main'
	]
    }
)

package_dir = {'CloudFlare': 'lib'}
