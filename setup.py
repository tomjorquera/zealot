#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='zealot',
    version='0.0.1',
    author='Tom Jorquera',
    author_email='tjorquera@linagora.com',
    packages = find_packages(),
    classifiers=[
       'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)'
    ],
    entry_points = {
        'console_scripts' : ['zealot=zealot.main:zealot_main']
    },
    install_requires = [
        'sacred',
        'gitpython',
        'pymongo',
        'docker',
    ],
)
