#!/usr/bin/env python

from setuptools import setup, find_packages
import os

setup(name='django-linked-accounts',
      version='2.1.1',
      description='Link third-party service accounts to Django accounts.',
      author='Andrii Kurinnyi',
      author_email='andrew@zen4ever.com',
      url='http://github.com/zen4ever/django-linked-accounts',
      packages=find_packages(),
      keywords=['django', 'oauth', 'accounts', 'twitter', 'facebook'],
      classifiers=[
          'Development Status :: 1 - Planning',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Framework :: Django',
      ],
      install_requires=['oauth-flow'],
      long_description=open(
          os.path.join(os.path.dirname(__file__), 'README.rst'),
      ).read().strip(),
)
