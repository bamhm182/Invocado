#!/usr/bin/env python

import setuptools

with open('README.md', 'r') as fp:
    long_descripton = fp.read()

setuptools.setup(
    name='Invocado',
    version='0.0.0',
    author='bamhm182',
    author_email='bamhm182@gmail.com',
    description='A package to facilitate listening for actions from Apache Guacamole and executing Terraform configs accordingly',
    long_descripton=long_descripton,
    long_descroption_content_type='text/markdown',
    url='https://www.github.com/bamhm182/Invocado',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
    packages=['invocado', 'invocado.plugins'],
    package_data={
        'synack.db': ['alembic.ini', 'alembic/*', 'alembic/**/*', 'models/*'],
    },
    package_dir={'': 'src/middleware'},
    install_requires=[
        "alembic==1.11.3",
        "GitPython==3.1.32",
        "pathlib2==2.3.7.post1",
        "requests==2.31.0",
        "tabulate==0.9.0"
    ]
)
