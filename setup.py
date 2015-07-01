import os.path
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

VERSION = "1.5.0"

setup(
    name = "python-converter-indic",
    version = VERSION,
    description="UTF to WX convertor and vice-versa for Indian Languages",
    long_description = open('README.rst', 'rb').read().decode('utf8'),
    keywords = ['UTF', 'WX', 'Unicode', 'computational linguistics',
		'ASCII', 'conll', 'ssf', 'bio', 'tnt'],
    author='Irshad Ahmad',
    author_email='irshad.bhat@research.iiit.ac.in',
    maintainer='Irshad Ahmad',
    maintainer_email='irshad.bhat@research.iiit.ac.in',
    license = "MIT",
    url="https://github.com/irshadbhat/python-converter-indic",
    package_dir={'convertor_indic':'converter_indic'},
    packages=['converter_indic']
)
