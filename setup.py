from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='pytineye',
      version=version,
      description="Python client for the TinEye Commercial API.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='reverse image search',
      author='Id\xc3\xa9e Inc.',
      author_email='support@tineye.com',
      url='https://api.tineye.com/',
      license='MIT License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'pycrypto', 'simplejson', 'urllib3'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
