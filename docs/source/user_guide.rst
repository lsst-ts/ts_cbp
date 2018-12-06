User Guide
==========

This is for using the CBP CSC as a remote by a control script(or whatever it ends up being called) writer.

.. code-block:: python

    from lsst.ts.salobj.remote import *
    import SALPY_CBP
    import asyncio

    async def main():
        cbp_remote = Remote(SALPY_CBP)
        move_azimuth_topic = cbp_remote.cmd_moveAzimuth.DataType()
        move_azimuth_topic.azimuth = 3
        move_azimuth_task = cbp_remote.cmd_moveAzimuth.start(move_azimuth_topic)
        move_altitude_topic = cbp_remote.cmd_moveAltitude.DataType()
        move_altitude_topic.altitude = 5
        move_altitude_task = cbp_remote.cmd_moveAltitude.start(move_altitude_topic)
        asyncio.gather([move_azimuth_task,move_altitude_task])

     if __name__ == "__main__":
        asyncio.get_event_loop().run_until_complete(main())


