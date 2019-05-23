import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


setup(
    name='git-sae-ops',
    author='ikethecoder',
    author_email='',
    version='1.0.0',
    description="GIT Secure Analysis Environment Ops",
    long_description=read('README.md'),
    license='Apache 2.0',

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'boto3',
        'flask',
        'flask-compress',
        'gevent',
        'pyyaml',
        'requests'
    ],
    setup_requires=[
    ],
    tests_require=[
    ]
)
