#!/usr/bin/python
# -*- encoding: utf-8 -*-

from setuptools import setup

setup(
    name='PyPocketExplore',
    version='v1.0.0',
    packages=['pypocketexplore', ],
    entry_points='''
        [console_scripts]
        pypocketexplore=pypocketexplore.cli:cli
    ''',
    license='The MIT License (MIT) Copyright © 2017 Florents Tselai.',
    description='PyPocketExplore - Unofficial API to Pocket Explore data',
    long_description=open('README.md', 'r').read(),
    author='Florents Tselai',
    author_email='florents.tselai@gmail.com',
    url='http://tselai.com/pypocketexplore-collecting-exploring-predicting-pocket-items-machine-learning',
    install_requires=open('requirements.txt').read().splitlines()
)
