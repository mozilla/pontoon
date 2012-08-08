#!/usr/bin/env python
from setuptools import setup

setup(
    name='django-pontoon-hook',
    version='0.1',
    description='Pontoon hook for Django.',
    long_description=open('README.md').read(),
    author='Ratnadeep Debnath',
    author_email='rtnpro@gmail.com',
    packages=[
        'pontoon_hook',
    ],
    install_requires=['setuptools','mock',]
)
