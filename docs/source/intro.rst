Intro
=====

..  todolist::


.. glossary::

    DMC
        The programming language used by Galil software. A variant of the c programming language.

    CSC
        Configurable SAL component

Errors
------
Position Error
    Commanded position and actual position exceeded difference threshold for an extended period of time. Trips panic.
Serial Encoder Error
    The serial encoder is returning invalid data. Trips panic.
Software Lower Motion Limit
    Software lower limit reached.
Software Upper Motion Limit
    Software upper limit reached.
Hardware Lower Motion Limit
     Hardware lower motion tripped. Trips panic.
Hardware Upper Motion Limit
    Hardware upper motion tripped. Trips panic.
Torque Limit
    Motor sustained high torque speed. Trips panic.

Anything that trips panic must be dealt with physically. Once the problem has been dealt with, the panic mode can be
reset by powercycling the CBP.

Description
-----------
ts_cbp is a package that creates a python wrapper around Galil's DMC code which is the internal language of the
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
