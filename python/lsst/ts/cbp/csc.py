import pathlib
from . import component
import asyncio
from lsst.ts import salobj

__all__ = ["CBPCSC", "CBPModel"]


class CBPCSC(salobj.ConfigurableCsc):
    """This defines the CBP CSC using ts_salobj.

    Parameters
    ----------
    port : `str`
        This is the ip address of the CBP.

    address : `int`
        This is the port of the CBP

    speed : `float`
        The amount of time it takes to move the CBP into place.

    factor : `float`
        The factor to multiply the speed of the CBP.

    initial_state : `salobj.State`
        The initial state of the csc, typically STANDBY or OFFLINE

    Attributes
    ----------
    log : `logging.Logger`
        This is the log for the class.

    summary_state : `salobj.State`
        This is the current state for the csc.

    model : `CBPModel`
        This is the model that links the component to the CSC.

    cbp_speed : `float`
        The amount of time that it takes to move CBP's axes.

    factor : `float`
        The factor to add to the speed of the CBP.

    """

    def __init__(
        self,
        initial_state: salobj.State = salobj.State.STANDBY,
        config_dir=None,
        speed=3.5,
        factor=1.25,
        simulation_mode=0,
    ):

        schema_path = pathlib.Path(__file__).parents[4].joinpath("schema", "CBP.yaml")

        super().__init__(
            name="CBP",
            index=0,
            config_dir=config_dir,
            initial_state=initial_state,
            simulation_mode=simulation_mode,
            schema_path=schema_path,
        )
        self.model = CBPModel()
        self.cbp_speed = speed
        self.factor = factor
        self.log.info("CBP CSC initialized")

    async def do_moveAzimuth(self, data):
        """Moves the azimuth axis of the CBP.

        Parameters
        ----------
        data

        Returns
        -------
        None

        """
        self.log.debug("Begin moveAzimuth")
        self.assert_enabled("moveAzimuth")
        self.model.move_azimuth(data.azimuth)
        self.log.debug("moveAzimuth sent to model")
        self.cmd_moveAzimuth.ack_in_progress(data, "In progress")
        await asyncio.sleep(self.cbp_speed * self.factor)

    async def telemetry(self):
        """Actually updates all of the sal telemetry objects.

        Returns
        -------
        None

        """
        while True:
            self.log.debug("Begin sending telemetry")
            self.model.publish()
            self.tel_azimuth.set_put(azimuth=self.model.azimuth)
            self.tel_altitude.set_put(altitude=self.model.altitude)
            self.tel_focus.set_put(focus=self.model.focus)
            self.tel_mask.set_put(
                mask=self.model.mask, mask_rotation=self.model.mask_rotation
            )
            self.tel_parked.set_put(
                autoparked=self.model.auto_parked, parked=self.model.parked
            )
            self.tel_status.set_put(
                panic=self.model.panic_status,
                azimuth=self.model.azimuth_status,
                altitude=self.model.altitude_status,
                mask=self.model.mask_status,
                mask_rotation=self.model.mask_rotation_status,
                focus=self.model.focus_status,
            )
            if self.model.panic_status == 1:
                self.fault()

            await asyncio.sleep(self.heartbeat_interval)

    async def do_moveAltitude(self, data):
        """Moves the altitude axis of the CBP.

        Parameters
        ----------
        data

        Returns
        -------
        None

        """
        self.assert_enabled("moveAltitude")
        self.model.move_altitude(data.altitude)
        self.cmd_moveAltitude.ack_in_progress(data, "In progress")
        await asyncio.sleep(self.cbp_speed * self.factor)

    async def do_setFocus(self, data):
        """Sets the focus.

        Parameters
        ----------
        data

        Returns
        -------
        None

        """
        self.assert_enabled("setFocus")
        self.model.change_focus(data.focus)

    async def do_park(self, data):
        """Parks the CBP.

        Returns
        -------
        None

        """
        self.assert_enabled("park")
        self.model.park()

    async def do_changeMask(self, data):
        """Changes the mask.

        Parameters
        ----------
        data

        Returns
        -------
        None

        """
        self.assert_enabled("changeMask")
        self.model.change_mask(data.mask)

    async def do_clearFault(self, data):
        """

        Parameters
        ----------
        data

        Returns
        -------
        None

        """
        self.assert_enabled("clearFault")

    async def begin_enable(self, data):
        """Overrides the begin_enable function in salobj.BaseCsc to make sure the CBP is unparked.

        Parameters
        ----------
        data

        Returns
        -------
        None

        """
        self.model._cbp.set_park()

    async def end_start(self, data):
        self.model.connect()
        self.telemetry_task = asyncio.ensure_future(self.telemetry())

    async def end_standby(self, data):
        self.telemetry_task.cancel()
        self.model.disconnect()

    async def configure(self, config):
        try:
            self.model.configure(config)
        except Exception as e:
            self.log.error(e)

    @staticmethod
    def get_config_pkg():
        return "ts_config_mtcalsys"

    async def implement_simulation_mode(self, simulation_mode):
        if simulation_mode == 0:
            self.model._cbp.set_simulation_mode(simulation_mode)
        elif simulation_mode == 1:
            self.model._cbp.set_simulation_mode(simulation_mode)
        else:
            raise salobj.ExpectedError(f"{simulation_mode} is not a valid value")


class CBPModel:
    """This is the model that connects the CSC and the component together.

    Attributes
    ----------
    azimuth : `float`
        The last updated position of the azimuth encoder
    altitude : `float`
        The last updated position of the altitude encoder
    mask : `str`
        The last updated mask name of the mask encoder.
    mask_rotation : `float`
        The last updated mask rotation of the rotation encoder.
    focus : `float`
        The last updated focus of the focus encoder.
    panic_status : `int`
        The last updated panic_status of the status byte.
    azimuth_status : `int`
        The last updated azimuth_status of the status byte.
    altitude_status : `int`
        The last updated altitude_status of the status byte.
    mask_status : `int`
        The last updated mask_status of the status byte.
    mask_rotation_status : `int`
        The last updated mask_rotation_status of the status byte.
    focus_status : `int`
        The last updated focus_status of the status byte.
    auto_parked : `int`
        The last updated auto_parked attribute.
    parked : `int`
        The last updated parked attribute.
    """

    def __init__(self):
        self._cbp = component.CBPComponent()
        self.azimuth = self._cbp.azimuth
        self.altitude = self._cbp.altitude
        self.mask = self._cbp.mask
        self.mask_rotation = self._cbp.mask_rotation
        self.focus = self._cbp.focus
        self.panic_status = self._cbp.panic_status
        self.azimuth_status = self._cbp.encoder_status.AZIMUTH
        self.altitude_status = self._cbp.encoder_status.ELEVATION
        self.mask_status = self._cbp.encoder_status.MASK_SELECT
        self.mask_rotation_status = self._cbp.encoder_status.MASK_ROTATE
        self.focus_status = self._cbp.encoder_status.FOCUS
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
