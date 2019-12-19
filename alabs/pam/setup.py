# coding: utf-8
from codecs import open
from setuptools import setup, find_packages

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='alabs.pam',
    version='1.0.1',
    packages=find_packages(),
    description='ARGOS-LABS PAM',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='',
    author='Duk Kyu Lim',
    author_email='deokyu@argoslabs.com',
    url='',
    download_url='',
    install_requires=['alabs.common', 'gevent', 'flask', 'flask-restplus',
                      'PyYaml', 'chardet', 'requests', 'requirements-parser',
                      'bs4', 'pyautogui', 'pyscreenshot',
                      'opencv-contrib-python'],
    classifiers=['Programming Language :: Python :: 3.6',
                 'Intended Audience :: Financial and Insurance Industry',
                 'License :: OSI Approved :: Closed Sorce Software']
    )
