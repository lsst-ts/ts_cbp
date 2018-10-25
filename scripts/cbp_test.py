#!/usr/bin/env python
import salobj
import SALPY_CBP
import asyncio
import logging
import argh


class CBPRemote():
    def __init__(self):
        self.remote = salobj.Remote(SALPY_CBP)
        self.log = logging.getLogger(__name__)

    async def standby(self):
        standby_topic = self.remote.cmd_standby.DataType()
        standby_ack = await self.remote.cmd_standby.start(standby_topic,timeout=10)
        self.log.info(standby_ack.ack.ack)
        asyncio.get_event_loop().run_until_complete(self.standby())

    async def disable(self):
        disable_topic = self.remote.cmd_disable.DataType()
        disable_ack = await self.remote.cmd_disable.start(disable_topic,timeout=10)
        self.log.info(disable_ack.ack.ack)
        asyncio.get_event_loop().run_until_complete(self.disable())

    async def start(self):
        start_topic = self.remote.cmd_start.DataType()
        start_ack = await self.remote.cmd_start.start(start_topic,timeout=10)
        self.log.info(start_ack.ack.ack)
        asyncio.get_event_loop().run_until_complete(self.start())

    async def enable(self):
        enable_topic = self.remote.cmd_enable.DataType()
        enable_ack = await self.remote.cmd_enable.start(enable_topic,timeout=10)
        self.log.info(enable_ack.ack.ack)
        asyncio.get_event_loop().run_until_complete(self.enable())

    async def move_azimuth(self, azimuth):
        move_azimuth_topic = self.remote.cmd_moveAzimuth.DataType()
        move_azimuth_topic.azimuth = azimuth
        move_azimuth_ack = await self.remote.cmd_moveAzimuth.start(move_azimuth_topic,timeout=10)
        self.log.info(move_azimuth_ack.ack.ack)
        asyncio.get_event_loop().run_until_complete(self.move_azimuth(azimuth))

    async def move_altitude(self, altitude):
        move_altitude_topic = self.remote.cmd_moveAltitude.DataType()
        move_altitude_topic.altitude = altitude
        move_altitude_ack = await self.remote.cmd_moveAltitude.start(move_altitude_topic,timeout=10)
        self.log.info(move_altitude_ack.ack.ack)
        asyncio.get_event_loop().run_until_complete(self.move_altitude(altitude))

    async def set_focus(self,focus):
        set_focus_topic = self.remote.cmd_setFocus.DataType()
        set_focus_topic.focus = focus
        set_focus_ack = await self.remote.cmd_setFocus.start(set_focus_topic,timeout=10)
        self.log.info(set_focus_ack.ack.ack)
        asyncio.get_event_loop().run_until_complete(self.set_focus(focus))

    async def park(self):
        park_topic = self.remote.cmd_park.DataType()
        park_ack = await self.remote.cmd_park.start(park_topic,timeout=10)
        self.log.info(park_ack.ack.ack)
        asyncio.get_event_loop().run_until_complete(self.park())


def do_stuff():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.info("Starting")
    cbp_remote = CBPRemote()
    parser = argh.ArghParser()
    parser.add_commands(
        [cbp_remote.standby,
         cbp_remote.start,
         cbp_remote.disable,
         cbp_remote.enable,
         cbp_remote.move_altitude,
         cbp_remote.move_azimuth,
         cbp_remote.set_focus,
         cbp_remote.park])
    parser.dispatch()

if __name__ == '__main__':
    do_stuff()