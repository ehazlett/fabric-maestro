#!/usr/bin/env python
#    Copyright 2012 Maestro Project
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
from distutils.core import setup
import maestro

setup(name='maestro',
    version = maestro.__version__,
    author = 'Evan Hazlett',
    author_email = 'ejhazlett@gmail.com',
    packages = ['maestro'],
    description = 'DevOps management',
    url = 'https://github.com/ehazlett/maestro',
    license = 'License :: OSI Approved :: Apache Software License',
    long_description = """
    DevOps management""",
    install_requires = ['Fabric>=1.4.0', 'apache-libcloud>=0.9.1', 'argparse>=1.2'],
    platforms = [
        "All",
        ],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: System :: Systems Administration",
        ],
    )

