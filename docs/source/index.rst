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
.. code-block:: bash

   git clone https://github.com/lsst-ts/ts_CBP.git
   setup salobj $USER
   source ~/gitrepo/ts_sal/setup.env
   cd gitrepo
   pip install -e .


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
