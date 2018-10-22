import salobj
import SALPY_CBP
import asyncio
import logging


async def do_stuff():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.info("Starting")
    cbp = salobj.Remote(SALPY_CBP,0)
    start_topic = cbp.cmd_start.DataType()
    disable_topic = cbp.cmd_disable.DataType()
    enable_topic = cbp.cmd_enable.DataType()
    moveAzimuth_topic = cbp.cmd_moveAzimuth.DataType()
    moveAzimuth_topic.azimuth = 2
    start_ack = await cbp.cmd_start.start(start_topic, timeout=5)
    print(start_ack.ack.ack)
    #await cbp.cmd_enable.start(enable_topic,timeout=5)
    ack = await cbp.cmd_moveAzimuth.start(moveAzimuth_topic,timeout=10)
    print(ack.ack.ack)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(do_stuff())