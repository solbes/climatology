import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as fh:
    long_description = fh.read()

setup(
    name='climatology',
    version='0.0.1',
    packages=['climatology'],
    url='https://github.com/solbes/climatology',
    author='Antti Solonen',
    author_email='antti.solonen@gmail.com',
    description='Global historical weather data API based on CDS data',
    keywords=['weather data', 'climatology'],
    install_requires=[
        'flask',
        'matplotlib',
        'numpy',
        'pandas',
        'xarray',
        'cdsapi',
        'netcdf4',
        'h5netcdf',
        'dask'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
