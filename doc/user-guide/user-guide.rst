..
  This is a template for the user-guide documentation that will accompany each CSC.
  This template is provided to ensure that the documentation remains similar in look, feel, and contents to users.
  The headings below are expected to be present for all CSCs, but for many CSCs, additional fields will be required.

  ** All text in square brackets [] must be re-populated accordingly **

  See https://developer.lsst.io/restructuredtext/style.html
  for a guide to reStructuredText writing.

  Use the following syntax for sections:

  Sections
  ========

  and

  Subsections
  -----------

  and

  Subsubsections
  ^^^^^^^^^^^^^^

  To add images, add the image file (png, svg or jpeg preferred) to the
  images/ directory. The reST syntax for adding the image is

  .. figure:: /images/filename.ext
   :name: fig-label

   Caption text.

  Feel free to delete this instructional comment.

.. Fill out data so contacts section below is auto-populated
.. add name and email between the *'s below e.g. *Marie Smith <msmith@lsst.org>*
.. |CSC_developer| replace::  *Replace-with-name-and-email*
.. |CSC_product_owner| replace:: *Replace-with-name-and-email*

.. _User_Guide:

#######################
CBP User Guide
#######################

The CBP has two directions for axial movement, the azimuth (side-to-side) and altitude (bottom-to-top).
It also allows for up to five masks to be added as a means of characterizing beam projection.
Limits are in place for each axis to prevent damage to the device.
The CBP also has the ability to be parked, where the altitude is at -70 degrees and the motors cannot be moved.
This ability can be manually commanded, but is automatically triggered if an internal battery source detects that the power has been lost for more than ~3 seconds.


CBP Interface
======================

A link to the SAL API can be found at the top of the :doc:`index </index>`.

The main commands that will likely be used are 

:ref:`ts_xml:CBP:Commands:moveAzimuth`

:ref:`ts_xml:CBP:Commands:moveAltitude`

:ref:`ts_xml:CBP:Commands:changeMask`

The relevant telemetry includes

:ref:`ts_xml:CBP:Telemetry:azimuth`

:ref:`ts_xml:CBP:Telemetry:altitude`

:ref:`ts_xml:CBP:Telemetry:mask`

:ref:`ts_xml:CBP:Telemetry:status`

Example Use-Case
================

Starting the CSC

.. code::

    from lsst.ts import salobj

    cbp = salobj.Remote(name="CBP", domain=salobj.Domain())

    await cbp.start_task

Un-parking the CSC

.. code::

    await cbp.cmd_park.set_start(park=False, timeout=10)

Moving the CBP in azimuth

.. code::

    await cbp.cmd_moveAzimuth.set_start(azimuth=30, timeout=10)

Moving the CBP in altitude

.. code::

    await cbp.cmd_moveAltitude.set_start(altitude=45, timeout=10)

Changing CBP's mask.

.. code::

    await cbp.cmd_changeMask(mask="Mask 1")

Getting telemetry from the CBP

.. code::

    azimuth = await cbp.tel_azimuth.aget(timeout=2)
    altiude = await cbp.tel_altitude.aget(timeout=2)

