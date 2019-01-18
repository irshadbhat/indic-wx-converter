#!/usr/bin/env python

import os
from setuptools import setup

os.environ['PBR_VERSION'] = '2.0.0'
os.environ['SKIP_WRITE_GIT_CHANGELOG'] = '1'
os.environ['SKIP_GENERATE_AUTHORS'] = '1'

setup(
    setup_requires=['pbr>=2.0', 'setuptools>=17.1'],
    pbr=True,
    include_package_data=True
)
