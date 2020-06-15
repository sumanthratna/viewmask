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

:code:`collaborate` Deployment
==============================
.. code-block:: sh

   mkdir collaborate && cd collaborate
   git clone git@github.com:sumanthratna/viewmask.git public/
   touch run.sh

:code:`run.sh` should have the following contents:

.. code-block:: bash

   #!/usr/bin/env bash

   export DEBUG=FALSE

   if [ ! -f ../Python-3.6.10/python3.6 ]; then
     echo '===========INSTALLING PYTHON 3.6.10==========='
     # https://randomwalk.in/python/2019/10/27/Install-Python-copy.html
     cd ..
     wget https://www.python.org/ftp/python/3.6.10/Python-3.6.10.tgz
     tar zxfv Python-3.6.10.tgz
      rm Python-3.6.10.tgz
     find ./Python-3.6.10/Python -type d | xargs chmod 0755
     cd Python-3.6.10
     ./configure --prefix=$PWD/Python-3.6.10/Python
     make
     make install
     ln -s python python3.6
     cd ../public
   fi
   export PATH=../Python-3.6.10:$PATH

   if [ ! -O venv ]; then
     echo '===========RECREATING VENV==========='
     rm -rf venv/
     python3.6 -m venv venv
     source venv/bin/activate
     python3.6 -m pip install --upgrade pip
   else
     source venv/bin/activate
   fi

   echo '===========INSTALLING PACKAGE==========='
   python3.6 -m pip install --upgrade ".[collaborate]"

   export DJANGO_SETTINGS_MODULE='settings'
   cd viewmask/collaborate

   echo '===========BUILDING STATIC FILES==========='
   rm -rf staticfiles/
   mkdir staticfiles/
   python3.6 manage.py collectstatic --no-input
   cd theme/static_src
   npm i
   npm run build:clean && npm run build:sass && npm run build:postcss && npm run build:cleancss
   npx purgecss --css ../static/css/styles.css ../../staticfiles/css/*.css --content ../../templates/**/*.html --config postcss.config.js --output ../../staticfiles/css
   cd ../../../

   echo '===========KILLING UWSGI PROCESSES==========='
   uwsgi --stop /tmp/viewmask-collaborate.pid
   killall -s INT uwsgi
   fuser -k $PORT/tcp
   pkill -f uwsgi -9

   echo '===========SERVING APP VIA UWSGI==========='
   uwsgi --ini collaborate/uwsgi.ini --http-socket 127.0.0.1:$PORT
   deactivate
