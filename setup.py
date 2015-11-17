#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Setup for the dbservice
"""

from setuptools import setup, find_packages

setup(
    name='dbservice',
    version='0.9',
    description="Database service for storing meter data",
    author="Søren Aagaard Mikkelsen",
    author_email='smik@eng.au.dk',
    url='https://github.com/dbservice/dbservice',
    packages=find_packages(),
    package_data={'': ['static/*.*', 'templates/*.*']},
    scripts=['manage.py'],
)
