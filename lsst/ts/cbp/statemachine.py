import logging
import pathlib
from . import component
import asyncio
import SALPY_CBP
from lsst.ts import salobj


class CBPCsc(salobj.ConfigurableCsc):
    """This defines the CBP :term:`CSC` using ts_salobj.

    Parameters
    ----------
    port: str
        This is the ip address of the CBP.

    address: int
        This is the port of the CBP

    frequency: float
        This is the amount of seconds to query the device for telemetry.

    initial_state: salobj.State
        The initial state of the csc, typically STANDBY or OFFLINE

    Attributes
    ----------
    log: logging.Logger
        This is the log for the class.

    summary_state: salobj.State
        This is the current state for the csc.

    model: CBPModel
        This is the model that links the component to the CSC.

    frequency: float
        The amount of time in seconds to wait for querying the device.

    azimuth_topic: salobj.ControllerTelemetry
        topic for the azimuth telemetry as defined in the XML.

    altitude_topic: salobj.ControllerTelemetry
        topic for altitude telemetry as defined in the XML.

    mask_topic: salobj.ControllerTelemetry
        Topic for mask telemetry as defined in the XML.

    focus_topic: salobj.ControllerTelemetry
        Topic for focus telemetry as defined in the XML.

    status_topic: salobj.ControllerTelemetry
        Topic for status telemetry as defined in the XML.

    parked_topic: salobj.ControllerTelemetry
        Topic for parked telemetry as defined in the XML.

    """
    def __init__(
            self,
            frequency: float = 2,
            initial_state: salobj.State = salobj.State.STANDBY,
            speed=3.5,
            factor=1.25,
            simulation_mode=0,
            schema=pathlib.Path(__file__).parents[3].joinpath("schema", "CBP.yaml")):
        super().__init__(
            SALPY_CBP,
            None,
            schema)
        self.summary_state = initial_state
        self.model = CBPModel()
        self.frequency = frequency
        self.cbp_speed = speed
        self.factor = factor
        self.log.info("CBP CSC initialized")
        self.azimuth_topic = self.tel_azimuth.DataType()
        self.altitude_topic = self.tel_altitude.DataType()
        self.mask_topic = self.tel_mask.DataType()
        self.focus_topic = self.tel_focus.DataType()
        self.status_topic = self.tel_status.DataType()
        self.parked_topic = self.tel_parked.DataType()
        asyncio.ensure_future(self.azimuth_telemetry())

    async def do_moveAzimuth(self, id_data):
        """Moves the azimuth axis of the CBP.

        Parameters
        ----------
        id_data

        Returns
        -------
        None

        """
        self.log.debug("Begin moveAzimuth")
        self.assert_enabled("moveAzimuth")
        self.model.move_azimuth(id_data.data.azimuth)
        self.log.debug("moveAzimuth sent to model")
        self.cmd_moveAzimuth.ackInProgress(id_data, "In progress")
        await asyncio.sleep(self.cbp_speed*self.factor)

    async def azimuth_telemetry(self):
        """Actually updates all of the sal telemetry objects.

        Returns
        -------
        None

        """
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

    async def do_moveAltitude(self, id_data):
        """Moves the altitude axis of the CBP.

        Parameters
        ----------
        id_data

        Returns
        -------
        None

        """
        self.assert_enabled("moveAltitude")
        self.model.move_altitude(id_data.data.altitude)
        self.cmd_moveAltitude.ackInProgress(id_data, "In progress")
        await asyncio.sleep(self.cbp_speed*self.factor)

    async def do_setFocus(self, id_data):
        """Sets the focus.

        Parameters
        ----------
        id_data

        Returns
        -------
        None

        """
        self.assert_enabled("setFocus")
        self.model.change_focus(id_data.data.focus)

    async def do_park(self):
        """Parks the CBP.

        Returns
        -------
        None

        """
        self.assert_enabled("park")
        self.model.park()

    async def do_changeMask(self, id_data):
        """Changes the mask.

        Parameters
        ----------
        id_data

        Returns
        -------
        None

        """
        self.assert_enabled("changeMask")
        self.model.change_mask(id_data.data.mask)

    async def do_clearFault(self, id_data):
        """

        Parameters
        ----------
        id_data

        Returns
        -------
        None

        """
        pass  # TODO: finish clearFault

    async def do_enterControl(self, id_data):
        """

        Parameters
        ----------
        id_data

        Returns
        -------
        None

        """
        pass  # TODO: finish enterControl

    async def begin_enable(self, id_data):
        """Overrides the begin_enable function in salobj.BaseCsc to make sure the CBP is unparked.

        Parameters
        ----------
        id_data

        Returns
        -------
        None

        """
        self.model._cbp.set_park()

    async def end_start(self, id_data):
        self.model.connect()
        self.telemetry_task = asyncio.ensure_future(self.telemetry())

    async def end_standby(self, id_data):
        self.telemetry_task.set_result('done')
        self.model.disconnect()

    def configure(self, config):
        try:
            self.model.configure(config)
        except Exception as e:
            self.log.error(e)

    def get_config_pkg(self):
        return "ts_config_mtcalsys"

    async def implement_simulation_mode(self, simulation_mode):
        if simulation_mode == 0:
            self.model._cbp.set_simulation_mode(simulation_mode)
        elif simulation_mode == 1:
            self.model._cbp.set_simulation_mode(simulation_mode)
        else:
            raise salobj.ExpectedError(f"{simulation mode} is not a valid value")


class CBPModel:
    """This is the model that connects the CSC and the component together.

    Parameters
    ----------
    port: str
        The ip address of the CBP.
    address: int
        The port of the CBP.

    Attributes
    ----------
    azimuth: float
        The last updated position of the azimuth encoder
    altitude: float
        The last updated position of the altitude encoder
    mask: str
        The last updated mask name of the mask encoder.
    mask_rotation: float
        The last updated mask rotation of the rotation encoder.
    focus: float
        The last updated focus of the focus encoder.
    panic_status: int
        The last updated panic_status of the status byte.
    azimuth_status: int
        The last updated azimuth_status of the status byte.
    altitude_status: int
        The last updated altitude_status of the status byte.
    mask_status: int
        The last updated mask_status of the status byte.
    mask_rotation_status: int
        The last updated mask_rotation_status of the status byte.
    focus_status: int
        The last updated focus_status of the status byte.
    auto_parked: int
        The last updated auto_parked attribute.
    parked: int
        The last updated parked attribute.
    """
    def __init__(self):
        self._cbp = component.CBPComponent()
        self.publish()
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
        """Calls the move_azimuth function of the component.

        Parameters
        ----------
        azimuth: float
            The azimuth in degrees to move to.

        Returns
        -------
        None

        """
        self._cbp.move_azimuth(azimuth)

    def move_altitude(self, altitude: float):
        """Calls the move_altitude function of the component.

        Parameters
        ----------
        altitude: float
            The altitude in degrees to move CBP to.

        Returns
        -------
        None

        """
        self._cbp.move_altitude(altitude)

    def change_mask(self, mask: str):
        """Calls the change_mask function of the component.

        Parameters
        ----------
        mask: str
            The name of the mask to change to.

        Returns
        -------
        None

        """
        mask_rotation = self._cbp.mask_dictionary[mask].rotation
        self._cbp.set_mask(mask)
        self._cbp.set_mask_rotation(mask_rotation)

    def change_focus(self, focus: int):
        """Calls the change_focus function of the CBP component,

        Parameters
        ----------
        focus: int
            The focus in microns to change to.

        Returns
        -------
        None

        """
        self._cbp.change_focus(focus)

    def park(self):
        """Calls the park function of the component.

        Returns
        -------
        None

        """
        self._cbp.set_park(1)

    def connect(self):
        self._cbp.connect()

    def disconnect(self):
        self._cbp.disconnect()

    def configure(self, config):
        self._cbp.configure(config)

    def publish(self):
        """Calls the publish function of the component.

        Returns
        -------
        None

        """
        self._cbp.publish()
