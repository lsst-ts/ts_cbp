*****
Intro
*****

..  todolist::


.. glossary::

    DMC
        The programming language used by Galil software. A variant of the c programming language.

    CSC
        Configurable SAL component

Errors
======
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
===========
ts_cbp is a package that creates a python wrapper around Galil's DMC code which is the internal language of the
controller. This code was written by DFM Manufacturing, who are also the company that created the physical CBP.

Installation
============
The following assumes that

* That the environment is setup according to the develop-env docker image
* That ts_salobj code is located in gitrepo directory

.. code-block:: console

   cd ~/gitrepo
   git clone https://github.com/lsst-ts/ts_CBP.git
   git clone https://github.com/lsst-ts/ts_salobj.git
   cd ~/gitrepo/ts_CBP
   pip install -e[dev]
   source ~/gitrepo/ts_sal/setup.env

Making Documentation
--------------------

.. code-block:: console

   cd docs
   package-docs build
