.. ts-cbp documentation master file, created by
   sphinx-quickstart on Thu Nov  8 14:05:48 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ts-cbp's documentation!
==================================

.. toctree::
   :hidden:
   :caption: Contents:

   api
   cli


Description
-----------
ts-cbp is a package that creates a python wrapper around Galil's DMC code which is the internal language of the
controller. This code was written by DFM Manufacturing, who are also the company that created the physical CBP.

Installation
------------
The following assumes that

* Centos 7 is the OS
* That ts_sal is installed according SAL user guide instructions
* Running code in python 3.6.^ virtualenv # Carrot indicates any minor release in 3.6 should work tested with 3.6.3 and 3.6.2
* That ts_salobj code is located in gitrepo directory
* That ts_salobj is version 3.3.0

.. code-block:: bash

   cd ~/gitrepo
   git clone https://github.com/lsst-ts/ts_CBP.git
   git clone https://github.com/lsst-ts/ts_salobj.git
   cd ts_salobj
   git checkout v3.3.0
   cd ~/gitrepo/ts_CBP
   virtualenv --python=python3 venv
   source venv/bin/activate
   source ~/gitrepo/ts_sal/setup.env
   pip install -e .
   export PYTHONPATH=$PYTHONPATH:~/gitrepo/ts_salobj/python

Making Documentation
--------------------

.. code-block:: bash

   cd docs
   make html


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
