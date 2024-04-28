from setuptools import setup

setup(
    name='nhldata',
    version='0.0.1',
    install_requires=[
        'requests'
    ],
    author='Tony Price',
    license='MIT',
    packages=[
        'nhldata','nhldata.moneypuck','nhldata.nhl'
    ]
)