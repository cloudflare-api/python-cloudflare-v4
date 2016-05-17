#!/usr/bin/env python

import os
from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='cloudflare',
    version='1.0.3',
    description='Python wrapper for the CloudFlare v4 API',
    long_description=long_description,
    author='Martin J. Levy',
    author_email='martin@cloudflare.com',
    maintainer='Martin J. Levy',
    maintainer_email='mahtin@mahtin.com',
    url='https://github.com/cloudflare/python-cloudflare',
    license='MIT',
    packages=['cli4']+find_packages(),
    install_requires=['requests'],
    keywords='cloudflare',
    entry_points={
	'console_scripts': [
	    'cli4 = cli4.__main__:main'
	]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)

package_dir = {'CloudFlare': 'lib'}
