######
ts_CBP
######

CBP is a Commandable SAL Component for the `Vera C. Rubin Observatory <https://lsst.org>`_.
It controls a Collimated Beam Projector for the Main Telescope Calibration System.

Installation
============

pip/setuptools method

.. code::

    pip install -e .[dev]
    pytest --cov lsst.ts.cbp -ra

EUPs method

.. code::

    pip install .[dev]
    setup -kr .
    scons 

Requirements
------------
This project uses the ``black`` linter.

.. code::

    pip install .[dev]
    pre-commit install

``black`` will now run as a pre-commit git hook.

There is a GitHub action for running the ``black --check`` function that will catch any missing ``black`` linted files.

Usage
=====

.. code::

    from lsst.ts import salobj

    domain = salobj.Domain()

    cbp = salobj.Remote(name="CBP", domain=domain)

    await cbp.start_task

.. code::

    await cbp.cmd_moveAzimuth.set_start(azimuth=20, timeout=10)
    await cbp.cmd_moveAltitude.set_start(altitude=30, timeout=10)
    await cbp.changeMask.set_start(mask=1)

.. code::

    azimuth = await cbp.tel_azimuth.aget(timeout=2)
    altiude = await cbp.tel_altitude.aget(timeout=2)

.. code::

    await domain.close()

Support
=======

Open issues in the JIRA project.

Roadmap
=======
N/A

Contributing
============
N/A

License
=======
This project is licensed under the `GPLv3 <https://www.gnu.org/licenses/gpl-3.0.en.html>`_.
