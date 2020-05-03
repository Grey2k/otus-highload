from sys import path

from setuptools import setup, find_packages

if '' not in path:
    path.insert(0, '')

setup(
    name='app',
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    tests_require=[
        'flask-testing',
    ],
    test_suite='tests',
)
