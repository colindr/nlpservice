#!/usr/bin/env python

from setuptools import setup

setup(
    name='tweetnlp',
    version='0.0.0',
    description='A module for doing Natural Language Processing on tweets',
    author='Colin Downs-Razouk',
    author_email='colin@razouk.com',
    url='https://colindr.com/nlp/',
    packages=['tweetnlp'],
    install_requires=[
        'keras',
        'tensorflow',
        'numpy',
        'python-twitter'
    ]
)