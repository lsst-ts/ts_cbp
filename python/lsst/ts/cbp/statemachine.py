import logging
from lsst.ts.cbp.component import CBPComponent
import asyncio
from salobj.base_csc import BaseCsc
from salobj import State
import SALPY_CBP


class CBPCsc(BaseCsc):
    def __init__(self, port: str, address: int, frequency: float = 0.5, initial_state: State = State.STANDBY, index: int= 0):
        super(BaseCsc, self).__init__(SALPY_CBP, index)
        self.log = logging.getLogger(__name__)
        self.log.debug("logger initialized")
        self.summary_state = initial_state
        self.model = CBPModel(port, address, frequency)
        self.frequency = self.model._cbp.frequency
        self.log.info("CBP CSC initialized")
        self.azimut_topic = self.tel_azimuth.DataType()
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
            self.model._cbp.publish()
            self.azimut_topic.azimuth = float(self.model._cbp.azimuth.split("\r")[0])
            self.tel_azimuth.put(self.azimut_topic)
            await asyncio.sleep(self.frequency)

    # TODO: write do_moveAltitude
    # TODO: write altitude_telemetry
    # TODO: write do_setFocus
    # TODO: write focus_telemetry
    # TODO: write do_changeMask
    # TODO: write mask_telemetry


class CBPModel:
    # TODO: write docstrings
    def __init__(self,port: str, address: int, frequency: float = 0.05):
        # TODO: write docstrings
        self._cbp = CBPComponent(port, address, frequency)
        self.azimuth = None
        self.altitude = None
        self.mask = None
        self.focus = None
        self.status = None

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

    def get_status(self):
        # TODO: write docstrings
        pass # TODO: write get_status function
