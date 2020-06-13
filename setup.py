# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.rst')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')

DESCRIPTION = 'A Python package and CLI to view XML annotations and NumPy '\
    'masks.'
setup(
    long_description=readme,
    name='viewmask',
    version='0.2.0',
    description=DESCRIPTION,
    python_requires='==3.*,>=3.6.0',
    project_urls={"documentation": "https://viewmask.readthedocs.io/en/stable",
                  "repository": "https://github.com/sumanthratna/viewmask"},
    author='Sumanth Ratna',
    author_email='sumanthratna@gmail.com',
    license='MIT',
    entry_points={"console_scripts": ["viewmask = viewmask.cli:cli"]},
    packages=['viewmask', 'viewmask.collaborate'],
    package_dir={"": "."},
    package_data={},
    install_requires=[
        'click==7.*,>=7.1.2',
        'dask-image==0.*,>=0.3.0',
        'napari[pyside2]==0.*,>=0.3.4',
        'numpy==1.*,>=1.18.4',
        'opencv-python-headless==4.*,>=4.2.0',
        'openslide-python==1.*,>=1.1.1',
        'pillow-simd==7.*,>=7.0.0',
        'scikit-image==0.*,>=0.17.2',
        'toolz==0.*,>=0.10.0'
    ],
    extras_require={"collaborate": [
        "django >= 3.0.7"
    ]},
)
