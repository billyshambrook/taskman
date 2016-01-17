from setuptools import find_packages
from setuptools import setup

import taskman


setup(
    name='taskman',
    version=taskman.__version__,
    license='BSD',
    url='http://github.com/billyshambrook/taskman',
    author='Billy Shambrook',
    author_email='billy.shambrook@gmail.com',
    description='A python task manager using Consul for its backend.',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    install_requires=[
        'consulate'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
    ],
    keywords=[
        'task', 'manager', 'consul', 'queue', 'worker'
    ]
)
