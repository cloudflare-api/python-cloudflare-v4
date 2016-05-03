#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='python-cloudflare-v4',
    version='1.1',
    description='Python wrapper for the CloudFlare v4 API',
    author='gnowxilef,Martin J. Levy',
    author_email='felix@fawong.com,mahtin@mahin.com',
    url='https://github.com/mahtin/python-cloudflare-v4',
    packages=['cli4']+find_packages(),
    entry_points={
	'console_scripts': [
	    'cli4 = cli4.__main__:main'
	]
    }
)

package_dir = {'CloudFlare': 'lib'}
