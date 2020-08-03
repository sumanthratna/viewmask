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
   
viewmask is meant to be a quick-and-easy tool for visualizing masks and a quick-and-easy library for working with annotations. For a more powerful library, consider `HistomicsTK <https://github.com/DigitalSlideArchive/HistomicsTK>`_ (see `annotations and masks <https://digitalslidearchive.github.io/HistomicsTK/histomicstk.annotations_and_masks.html>`_).

Installation
============

pip
------------
::

 python3 -m pip install --upgrade pip
 python3 -m pip install viewmask

or:
::

 python3 -m pip install --upgrade pip
 python3 -m pip install git+git://github.com/sumanthratna/viewmask.git#egg=viewmask

Poetry
------------
::

 poetry run python -m pip install --upgrade pip
 poetry add viewmask

or:
::

 poetry run python -m pip install --upgrade pip
 poetry add git+https://github.com/sumanthratna/viewmask.git
