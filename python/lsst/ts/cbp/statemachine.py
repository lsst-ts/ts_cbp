import logging
from lsst.ts.cbp.component import CBPComponent
import asyncio
from salobj.base_csc import BaseCsc
from salobj import State
import SALPY_CBP


class CBPCsc(BaseCsc):
    def __init__(self, port: str, address: int, frequency: float = 2, initial_state: State = State.STANDBY):
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
        self.parked_topic = self.tel_parked.DataType()
        asyncio.ensure_future(self.azimuth_telemetry())

    async def do_moveAzimuth(self, id_data):
        self.log.debug("Begin moveAzimuth")
        self.assert_enabled("moveAzimuth")
        self.model.move_azimuth(id_data.data.azimuth)
        self.log.debug("moveAzimuth sent to model")
        self.cmd_moveAzimuth.ackInProgress(id_data, "In progress")
        await asyncio.sleep(3*1.25)

    async def azimuth_telemetry(self):
        while True:
            self.log.debug("Begin sending telemetry")
            self.model.publish()
            self.azimuth_topic.azimuth = self.model.azimuth
            self.altitude_topic.altitude = self.model.altitude
            self.mask_topic.mask = self.model.mask
            self.mask_topic.mask_rotation = self.model.mask_rotation
            self.focus_topic.focus = self.model.focus
            self.status_topic.panic = self.model.panic_status
            self.status_topic.azimuth = self.model.azimuth_status
            self.status_topic.altitude = self.model.altitude_status
            self.status_topic.mask = self.model.mask_status
            self.status_topic.mask_rotation = self.model.mask_rotation_status
            self.status_topic.focus = self.model.focus_status
            self.parked_topic.autoparked = self.model.auto_parked
            self.parked_topic.parked = self.model.parked
            self.tel_azimuth.put(self.azimuth_topic)
            self.tel_altitude.put(self.altitude_topic)
            self.tel_mask.put(self.mask_topic)
            self.tel_focus.put(self.focus_topic)
            self.tel_status.put(self.status_topic)
            self.tel_parked.put(self.parked_topic)
            if self.model.panic_status == 1:
                self.fault()

            await asyncio.sleep(self.frequency)

    async def do_moveAltitude(self,id_data):
        self.assert_enabled("moveAltitude")
        self.model.move_altitude(id_data.data.altitude)
        self.cmd_moveAltitude.ackInProgress(id_data, "In progress")
        await asyncio.sleep(3*1.25)

    async def do_setFocus(self, id_data):
        self.assert_enabled("setFocus")
        self.model.change_focus(id_data.data.focus)

    async def do_park(self):
        self.assert_enabled("park")
        self.model.park()

    async def do_changeMask(self):
        pass # TODO: finish do_changeMask

    async def do_clearFault(self, id_data):
        pass #TODO: finish clearFault

    async def do_enterControl(self, id_data):
        pass #TODO: finish enterControl

    async def begin_enable(self, id_data):
        self.model._cbp.set_park()


class CBPModel:
    # TODO: write docstrings
    def __init__(self,port: str, address: int):
        # TODO: write docstrings
        self._cbp = CBPComponent(port, address)
        self.azimuth = self._cbp.azimuth
        self.altitude = self._cbp.altitude
        self.mask = self._cbp.mask
        self.mask_rotation = self._cbp.mask_rotation
        self.focus = self._cbp.focus
        self.panic_status = self._cbp.panic_status
        self.azimuth_status = self._cbp.azimuth_status
        self.altitude_status = self._cbp.altitude_status
        self.mask_status = self._cbp.mask_select_status
        self.mask_rotation_status = self._cbp.mask_rotate_status
        self.focus_status = self._cbp.focus_status
        self.auto_parked = self._cbp.auto_park
        self.parked = self._cbp.park

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

    def park(self):
        self._cbp.set_park(1)

    def publish(self):
        # TODO: write docstrings
        self._cbp.publish()
