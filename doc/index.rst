###
CBP
###

.. image:: https://img.shields.io/badge/SAL-API-gray.svg
    :target: https://ts-xml.lsst.io/sal_interfaces/CBP.html
.. image:: https://img.shields.io/badge/GitHub-gray.svg
    :target: https://github.com/lsst-ts/ts_CBP
.. image:: https://img.shields.io/badge/Jira-gray.svg
    :target: https://jira.lsstcorp.org/issues/?jql=labels+%3D+ts_CBP
.. image:: https://img.shields.io/badge/Jenkins-gray.svg
    :target: https://tssw-ci.lsst.org/job/LSST_Telescope-and-Site/job/ts_CBP/

.. _index:overview:

Overview
========

:ref:`Contact info <ts_xml:index:master-csc-table:CBP>`

`Docushare collection <https://docushare.lsst.org/docushare/dsweb/View/Collection-6513>`_

The Collimated Beam Projector (CBP) is a Commandable SAL Component that provides horizontal and vertical axis control of an integrating sphere in conjunction with a projecting light source for calibrating the Main Telescope.
Primarily, commands deal with moving the CBP in the azimuth and elevation directions and changing the masks.
The CBP will be used as part of the Calibration system of the Main Telescope.

.. note:: If you are interested in viewing other branches of this repository append a ``/v`` to the end of the url link. For example https://ts-cbp.lsst.io/v/


.. _index:user-documentation:

User Documentation
==================

User-level documentation, found at the link below, is aimed at personnel looking to perform the standard use-cases/operations with the CBP.

.. toctree::
    user-guide/user-guide
    :maxdepth: 2

.. _index:configuration:

Configuring the CBP
===================

The configuration for the CBP is described at the following link.

.. toctree::
    configuration/configuration
    :maxdepth: 1


.. _index:development-documentation:

Development Documentation
=========================

This area of documentation focuses on the classes used, API's, and how to participate to the development of the CBP software packages.

.. toctree::
    developer-guide/developer-guide
    :maxdepth: 1

.. _index:version-history:

Version History
===============

The version history of the CBP is found at the following link.

.. toctree::
    version-history
    :maxdepth: 1
