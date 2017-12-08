#!/usr/bin/env python

import os
from setuptools import setup

os.environ['PBR_VERSION'] = '1.2.3'
os.environ['SKIP_WRITE_GIT_CHANGELOG'] = '1'
os.environ['SKIP_GENERATE_AUTHORS'] = '1'

setup(
    setup_requires=['pbr'],
    pbr=True,
)
