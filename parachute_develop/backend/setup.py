# setup.py

from setuptools import setup, find_packages

setup(
    name='parachute',
    version='0.1.0',
    description='Parachute Project for Automated Tasks',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        'pandas==1.3.3',
        'schedule==1.1.0',
        'selenium==4.1.0',
        'python-dotenv==1.0.0'
    ],
    include_package_data=True,
    zip_safe=False
)
