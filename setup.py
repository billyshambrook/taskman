from setuptools import find_packages
from setuptools import setup


setup(
    name='taskman',
    version='0.0.2',
    license='BSD',
    url='http://github.com/billyshambrook/taskman',
    author='Billy Shambrook',
    author_email='billy.shambrook@gmail.com',
    description='A python task manager using Consul for its backend.',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    test_suite='tests',
    install_requires=[
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'pytest'
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
