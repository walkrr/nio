import re

from setuptools import setup, find_packages

with open('nio/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='nio',
    description='A framework for building blocks and modules for the nio Platform',
    long_description=readme(),
    keywords=['nio'],
    version=version,
    packages=find_packages(
        exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),

    install_requires=['safepickle>=0.1.0'],

    tests_require=[
        'requests>=2.3.0'
    ],
	
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
    ],

    license='Apache 2.0',
    author='niolabs',
    author_email='support@n.io',
    url='https://github.com/niolabs/nio'
)
