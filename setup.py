from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='nhldata',
    version='0.0.2',
    description='Low-dependency pacakge for pulling NHL data across multiple sources',
    long_description = long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'requests'
    ],
    url='https://github.com/TonyAllenPrice/nhldata',
    author='Tony Price',
    author_email='tony@tonyallenprice.com',
    license='MIT',
    packages=[
        'nhldata',
        'nhldata.moneypuck',
        'nhldata.nhl',
        'nhldata.tools'
    ]
)