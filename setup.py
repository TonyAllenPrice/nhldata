from setuptools import setup

setup(
    name='nhlstats',
    version='0.0.1',
    install_requires=[
        'requests',
        'csv',
        'zipfile'
    ],
    author='Tony Price',
    license='MIT',
    packages=[
        'nhlstats','nhlstats.moneypuck','nhlstats.nhl'
    ]
)