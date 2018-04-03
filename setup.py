# GOAL: build a universal wheel
# supporting both python 2 and 3
from setuptools import setup, find_packages
setup(
    name = 'CAM2CameraDatabaseClient',
    packages = find_packages(exclude = ['contrib', 'docs', 'tests']),
    version = '0.0',
    description = 'A python wrapper of CAM2 database API',
    author = 'Purdue CAM2 Research Group',
    author_email = 'cam2proj@ecn.purdue.edu',
    #license='Apache License 2.0',
    url = 'https://github.com/PurdueCAM2Project/CameraDatabaseClient',
    keywords = ['API','client', 'database', 'CAM2'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2', 
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        #'License :: OSI Approved :: Apache Software License'
    ],
    python_requires = '>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    #install_requires = []
)