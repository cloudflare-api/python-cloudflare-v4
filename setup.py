from setuptools import setup, find_packages

setup(
    name='python-cloudflare-v4',
    version='1.0',
    description='Python wrapper for the CloudFlare v4 API',
    author='gnowxilef',
    author_email='felix@fawong.com',
    url='http://github.com/python-cloudflare/python-cloudflare-v4',
    packages=find_packages()
    )

package_dir = {'cloudflare_v4': 'lib'}
