# -*- coding: utf-8 -*-
from setuptools import setup
from fortranmagic import __version__

long_description = (open('README.rst').read() + '\n\n' +
                    open('CHANGES.rst').read())

setup(
    name='fortran-magic',
    version=__version__,
    description='An extension for IPython that help to use Fortran in '
                'your interactive session.',
    long_description=long_description,
    author='Martin Gaitan',
    author_email='gaitan@gmail.com',
    url='https://github.com/mgaitan/fortran_magic',
    license='BSD',
    keywords="ipython notebook fortran f2py science",
    py_modules=['fortranmagic'],
    install_requires=['ipython', 'numpy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: IPython',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Fortran',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering'
    ],
)
