"""
Publish a new version:
$ git tag X.Y.Z -m "Release X.Y.Z"
$ git push --tags
$ pip install --upgrade twine wheel
$ python setup.py sdist bdist_wheel
$ twine upload dist/*
"""
import codecs
from setuptools import setup


LGTV_VERSION = '0.1'
LGTV_DOWNLOAD_URL = (
    'https://github.com/klattimer/LGWebOSRemote/tarball/' + LGTV_VERSION
)


def read_file(filename):
    """
    Read a utf8 encoded text file and return its contents.
    """
    with codecs.open(filename, 'r', 'utf8') as f:
        return f.read()

setup(
    name='LGTV',
    packages=['LGTV'],
    version=LGTV_VERSION,
    description='LG WebOS TV Controller.',
    long_description=read_file('README.md'),
    license='MIT',
    author='Karl Lattimer',
    author_email='karl@qdh.org.uk',
    url='https://github.com/klattimer/LGWebOSRemote',
    download_url=LGTV_DOWNLOAD_URL,
    keywords=[
        'smarthome', 'smarttv', 'lg', 'tv', 'webos', 'remote'
    ],
    dependency_links=['https://github.com/Lawouach/WebSocket-for-Python.git'],
    install_requires=[
        'wakeonlan'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Natural Language :: English',
    ],
)
