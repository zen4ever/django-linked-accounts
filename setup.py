#!/usr/bin/env python

from distutils.core import setup
import os

setup(name='django-linked-accounts',
      version='1.0',
      description='Link third-party service accounts to Django accounts.',
      author='Andrii Kurinnyi',
      author_email='andrew@zen4ever.com',
      url='http://github.com/zen4ever/django-linked-accounts',
      packages=['linked_accounts',],
      keywords=['django', 'oauth', 'accounts', 'twitter', 'facebook'],
      classifiers=[
          'Development Status :: 1 - Planning',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Framework :: Django',
      ],
      long_description=open(
          os.path.join(os.path.dirname(__file__), 'README.rst'),
      ).read().strip(),
)
