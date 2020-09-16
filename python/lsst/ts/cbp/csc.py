import pathlib
from . import component
import asyncio
from lsst.ts import salobj

__all__ = ["CBPCSC"]


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
        self.model = component.CBPComponent()
        self.cbp_speed = speed
        self.factor = factor
        self.log.info("CBP CSC initialized")

    async def do_move(self, data):
        """Move the CBP mount to a specified position.

        Parameters
        ----------
        data

        Returns
        -------
        None

        """
        self.log.debug("Begin move")
        self.assert_enabled("move")
        await asyncio.join(
            [
                self.model.move_elevation(data.elevation),
                self.model.move_azimuth(data.azimuth),
            ]
        )
        self.cmd_move.ack_in_progress(data, "In progress")
        await asyncio.sleep(self.cbp_speed * self.factor)

    async def telemetry(self):
        """Actually updates all of the sal telemetry objects.

        Returns
        -------
        None

        """
        while True:
            self.log.debug("Begin sending telemetry")
            await self.model.publish()
            self.tel_azimuth.set_put(azimuth=self.model.azimuth)
            self.tel_elevation.set_put(elevation=self.model.elevation)
            self.tel_focus.set_put(focus=self.model.focus)
            self.tel_mask.set_put(
                mask=self.model.mask, mask_rotation=self.model.mask_rotation
            )
            self.tel_parked.set_put(
                autoparked=self.model.auto_parked, parked=self.model.parked
            )
            self.tel_status.set_put(
                panic=self.model.panic_status,
                azimuth=self.model.encoder_status.AZIMUTH,
                altitude=self.model.encoder_status.ELEVATION,
                mask=self.model.encoder_status.MASK_SELECT,
                mask_rotation=self.model.encoder_status.MASK_ROTATE,
                focus=self.model.encoder_status.FOCUS,
            )
            if self.model.panic_status == 1:
                self.fault("CBP Panicked. Check hardware and reset device.")

            await asyncio.sleep(self.heartbeat_interval)

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
        await self.model.change_focus(data.focus)

    async def do_park(self, data):
        """Park the CBP.

        Returns
        -------
        None

        """
        self.assert_enabled("park")
        await self.model.set_park()

    async def do_unpark(self, data):
        """Unpark the CBP."""
        self.assert_enabled("unpark")
        await self.model.set_unpark()

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
        await self.model.change_mask(data.mask)

    async def begin_enable(self, data):
        """Overrides the begin_enable function in salobj.BaseCsc to make sure
        the CBP is un-parked.

        Parameters
        ----------
        data

        Returns
        -------
        None

        """
        await self.model.set_unpark()

    async def end_start(self, data):
        await self.model.connect()
        self.telemetry_task = asyncio.ensure_future(self.telemetry())

    async def end_standby(self, data):
        self.telemetry_task.cancel()
        await self.model.disconnect()

    async def configure(self, config):
        self.model.configure(config)

    @staticmethod
    def get_config_pkg():
        return "ts_config_mtcalsys"

    async def implement_simulation_mode(self, simulation_mode):
        if simulation_mode == 0:
            self.model.set_simulation_mode(simulation_mode)
        elif simulation_mode == 1:
            self.model.set_simulation_mode(simulation_mode)
        else:
            raise salobj.ExpectedError(f"{simulation_mode} is not a valid value")
