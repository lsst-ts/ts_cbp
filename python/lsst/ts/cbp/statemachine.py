import logging
from lsst.ts.cbp.component import CBPComponent
import asyncio
from salobj.base_csc import BaseCsc
from salobj import State
import SALPY_CBP


class CBPCsc(BaseCsc):
    def __init__(self, port: str, address: int, frequency: float = 0.5, initial_state: State = State.STANDBY, index: int= 0):
        super().__init__(SALPY_CBP)
        self.log = logging.getLogger(__name__)
        self.log.debug("logger initialized")
        self.summary_state = initial_state
        self.model = CBPModel(port, address)
        self.frequency = frequency
        self.log.info("CBP CSC initialized")
        self.azimuth_topic = self.tel_azimuth.DataType()
        self.altitude_topic = self.tel_altitude.DataType()
        self.mask_topic = self.tel_mask.DataType()
        self.focus_topic = self.tel_focus.DataType()
        self.status_topic = self.tel_status.DataType()
        asyncio.ensure_future(self.azimuth_telemetry())

    async def do_moveAzimuth(self, id_data):
        self.log.debug("Begin moveAzimuth")
        self.assert_enabled("moveAzimuth")
        self.model.move_azimuth(id_data.data.azimuth)
        self.log.debug("moveAzimuth sent to model")
        self.cmd_moveAzimuth.ackInProgress(id_data, "In progress")
        await asyncio.sleep(4.5)

    async def azimuth_telemetry(self):
        while True:
            self.log.debug("Begin sending azimuth telemetry")
            self.model.publish()
            self.azimuth_topic.azimuth = self.model.azimuth
            #self.altitude_topic.altitude = None
            #self.mask_topic.mask = None
            #self.focus_topic.focus = None
            #self.status_topic = None
            self.tel_azimuth.put(self.azimuth_topic)
            await asyncio.sleep(self.frequency)

    async def do_moveAltitude(self,id_data):
        pass #TODO: finish moveAltitude
    async def do_setFocus(self, id_data):
        pass #TODO: finish setFocus
    async def do_changeMask(self):
        pass # TODO: finish do_changeMask
    async def do_clearFault(self, id_data):
        pass #TODO: finish clearFault
    async def do_enterControl(self, id_data):
        pass #TODO: finish enterControl


class CBPModel:
    # TODO: write docstrings
    def __init__(self,port: str, address: int):
        # TODO: write docstrings
        self._cbp = CBPComponent(port, address)
        self.azimuth = self._cbp.azimuth
        self.altitude = self._cbp.altitude
        self.mask = self._cbp.mask
        self.focus = self._cbp.focus
        self.status = self._cbp.panic_status

    def move_azimuth(self, azimuth: float):
        # TODO: write docstrings
        self._cbp.move_azimuth(azimuth)

    def move_altitude(self, altitude: float):
        # TODO: write docstrings
        self._cbp.move_altitude(altitude)

    def change_mask(self, mask: str):
        # TODO: write docstrings
        pass # TODO: write change_mask function

    def change_focus(self, focus: int):
        # TODO: write docstrings
        self._cbp.change_focus(focus)

    def publish(self):
        # TODO: write docstrings
        self._cbp.publish() # TODO: write get_status function
