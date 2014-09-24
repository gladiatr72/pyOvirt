from __future__ import with_statement

try:
    from setuptools import setup, find_packages
except ImportError:
    # Distribute is not actually required to install
    from distutils.core import setup

__AUTHOR__ = 'Stephen Spencer'
__AUTHOR_EMAIL__ = 'gladiatr72@gmail.com'

readme = open('README.rst').read() + '\n\n' + open('CHANGELOG.rst').read()

import pyOvirt

VERSION = '.'.join(str(x) for x in pyOvirt.__version__)

packages=find_packages()

setup(name='saltovirt',
      version=VERSION,
      description='A python2[567] library for manipulating ovirt/rhev-m virtualization managers',
      author=__AUTHOR__,
      author_email=__AUTHOR_EMAIL__,
      maintainer=__AUTHOR__,
      maintainer_email=__AUTHOR_EMAIL__,
      url='https://github.com/gladiatr72/pyOvirt',
      license='MIT',
      keywords='saltstack ovirt rhev-m',
      packages=packages,
      platforms=['any'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Plugins',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Linux',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
      ],
    )

