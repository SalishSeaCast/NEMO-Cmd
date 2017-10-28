# Copyright 2013-2017 The Salish Sea MEOPAR Contributors
# and The University of British Columbia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""NEMO-Cmd -- NEMO command processor
"""
import sys
from setuptools import find_packages, setup

from nemo_cmd import __pkg_metadata__

python_classifiers = [
    'Programming Language :: Python :: {0}'.format(py_version)
    for py_version in ['2', '2.7', '3', '3.4', '3.5', '3.6']
]
other_classifiers = [
    'Development Status :: ' + __pkg_metadata__.DEV_STATUS,
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: Implementation :: CPython',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Unix',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Education',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
]
try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''
install_requires = [
    # see environment-dev.yaml for conda environment dev installation
    # see requirements.txt for package versions used during recent development
    'arrow',
    'attrs',
    'cliff!=2.9.0',
    'python-hglib',
    'PyYAML',
]
if sys.version_info[0] == 2:
    install_requires.append('pathlib2')

setup(
    name=__pkg_metadata__.PROJECT,
    version=__pkg_metadata__.VERSION,
    description=__pkg_metadata__.DESCRIPTION,
    long_description=long_description,
    author='Doug Latornell',
    author_email='dlatornell@eoas.ubc.ca',
    url='http://nemo-cmd.readthedocs.io/en/latest/',
    license='Apache License, Version 2.0',
    classifiers=python_classifiers + other_classifiers,
    platforms=['MacOS X', 'Linux'],
    install_requires=install_requires,
    packages=find_packages(),
    entry_points={
        # The nemo command:
        'console_scripts': ['nemo = nemo_cmd.main:main'],
        # Sub-command plug-ins:
        'nemo.app': [
            'combine = nemo_cmd.combine:Combine',
            'deflate = nemo_cmd.deflate:Deflate',
            'gather = nemo_cmd.gather:Gather',
            'prepare = nemo_cmd.prepare:Prepare',
            'run = nemo_cmd.run:Run',
        ],
    },
)
