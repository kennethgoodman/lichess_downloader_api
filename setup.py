from setuptools import setup

setup(
   name='lichess_downloader_api',
   version='1.0',
   description='Used to download and read lichess large data dumps',
   author='Kenneth Goodman',
   author_email='ken@kennethgoodman.me',
   packages=['lichess_downloader_api'],  # same as name
   install_requires=['requests', 'python-chess'],  # external packages as dependencies
)