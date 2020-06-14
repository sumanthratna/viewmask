viewmask
========
A Python package and CLI to view XML annotations and NumPy masks.

|PyPI version fury.io|
|PyPI downloads|
|HitCount|
|Documentation Status|
|Travis build|
|PyPI license|

.. |PyPI version fury.io| image:: https://badge.fury.io/py/viewmask.svg
   :target: https://pypi.python.org/pypi/viewmask/

.. |PyPI downloads| image:: https://img.shields.io/pypi/dm/viewmask
   :target: https://pypistats.org/packages/viewmask

.. |HitCount| image:: https://hits.dwyl.com/sumanthratna/viewmask.svg
   :target: https://hits.dwyl.com/sumanthratna/viewmask

.. |Documentation Status| image:: https://readthedocs.org/projects/viewmask/badge/?version=latest
   :target: https://viewmask.readthedocs.io/?badge=latest

.. |Travis build| image:: https://travis-ci.com/sumanthratna/viewmask.svg?branch=master
   :target: https://travis-ci.com/sumanthratna/viewmask

.. |PyPI license| image:: https://img.shields.io/pypi/l/viewmask.svg
   :target: https://pypi.python.org/pypi/viewmask/

Features
========
* edit and view annotations quickly with napari
* launch a highly scalable and secure web app for collaborative annnotation editing

Installation
============

If you only want to view TCGA annotations, run :code:`python3 -m pip install viewmask`. If you get an error due to napari's installation, try running :code:`python3 -m pip install --upgrade pip`.

If you want to install the viewmask collaborate web app, run :code:`python3 -m pip install "viewmask[collaborate]"`
