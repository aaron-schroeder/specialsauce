import os
from setuptools import setup, find_packages


def read(rel_path):
  """Read a file so python does not have to import it.
  
  Inspired by (taken from) pip's `setup.py`.
  """
  here = os.path.abspath(os.path.dirname(__file__))
  with open(os.path.join(here, rel_path), 'r') as fp:
    return fp.read()


def get_version(rel_path):
  """Manually read through a file to retrieve its `__version__`.
  
  Inspired by (taken from) pip's `setup.py`.
  """
  for line in read(rel_path).splitlines():
    if line.startswith('__version__'):
      delim = "'" if "'" in line else '"'
      return line.split(delim)[1]
  raise RuntimeError('Unable to find version string.')


with open('README.md') as f:
  README = f.read()


setup(
  name='specialsauce',
  version=get_version(f'specialsauce/__init__.py'),
  description='Physiological formulas in Python',
  long_description=README,
  long_description_content_type='text/markdown',
  author='Aaron Schroeder',
  author_email='aaron@trailzealot.com',
  install_requires=[line.rstrip('\n') for line in open('requirements.txt')],
  url='https://github.com/aaron-schroeder/specialsauce',
  # project_urls={
  #   'Documentation': 'https://specialsauce.readthedocs.io/en/stable/',
  # },
  license='MIT',
  packages=find_packages(),
  classifiers=[
    'License :: OSI Approved :: MIT License',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
  ]
)

