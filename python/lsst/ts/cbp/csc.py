import pathlib
from . import component, mock_server
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

    valid_simulation_modes = (0, 1)

    def __init__(
        self,
        simulation_mode,
        initial_state: salobj.State = salobj.State.STANDBY,
        config_dir=None,
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
        self.simulator = None
        self.telemetry_task = salobj.make_done_future()
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
        await asyncio.gather(
            self.model.move_elevation(data.elevation),
            self.model.move_azimuth(data.azimuth),
        )
        self.evt_target.set_put(
            azimuth=self.model.azimuth_target,
            elevation=self.model.altitude_target,
            focus=self.model.focus_target,
            mask=self.model.mask_target,
            mask_rotation=self.model.mask_rotation_target,
        )
        self.evt_inPosition.set_put(
            azimuth=self.model.encoder_motion.azimuth,
            elevation=self.model.encoder_motion.elevation,
            focus=self.model.encoder_motion.focus,
            mask=self.model.encoder_motion.mask_select,
            mask_rotation=self.model.encoder_motion.mask_rotate,
        )
        await asyncio.wait_for(self.in_position(), 20)
        self.evt_inPosition.set_put(
            azimuth=self.model.encoder_motion.azimuth,
            elevation=self.model.encoder_motion.elevation,
            focus=self.model.encoder_motion.focus,
            mask=self.model.encoder_motion.mask_select,
            mask_rotation=self.model.encoder_motion.mask_rotate,
        )

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
                autoparked=self.model.auto_park, parked=self.model.park
            )
            self.tel_status.set_put(
                panic=self.model.panic_status,
                azimuth=self.model.encoder_status.azimuth,
                elevation=self.model.encoder_status.elevation,
                mask=self.model.encoder_status.mask_select,
                mask_rotation=self.model.encoder_status.mask_rotate,
                focus=self.model.encoder_status.focus,
            )
            if self.model.panic_status:
                self.fault(1, "CBP Panicked. Check hardware and reset device.")

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
        self.evt_target.set_put(
            azimuth=self.model.azimuth_target,
            elevation=self.model.altitude_target,
            focus=self.model.focus_target,
            mask=self.model.mask_target,
            mask_rotation=self.model.mask_rotation_target,
        )
        self.evt_inPosition.set_put(
            azimuth=self.model.encoder_motion.azimuth,
            elevation=self.model.encoder_motion.elevation,
            focus=self.model.encoder_motion.focus,
            mask=self.model.encoder_motion.mask_select,
            mask_rotation=self.model.encoder_motion.mask_rotate,
        )
        await asyncio.wait_for(self.in_position(), 20)
        self.evt_inPosition.set_put(
            azimuth=self.model.encoder_motion.azimuth,
            elevation=self.model.encoder_motion.elevation,
            focus=self.model.encoder_motion.focus,
            mask=self.model.encoder_motion.mask_select,
            mask_rotation=self.model.encoder_motion.mask_rotate,
        )

    async def do_park(self, data):
        """Park the CBP.

        Returns
        -------
        None

        """
        self.assert_enabled("park")
        await self.model.set_park()
        self.evt_inPosition.set_put(
            azimuth=self.model.encoder_motion.azimuth,
            elevation=self.model.encoder_motion.elevation,
            focus=self.model.encoder_motion.focus,
            mask=self.model.encoder_motion.mask_select,
            mask_rotation=self.model.encoder_motion.mask_rotate,
        )
        await asyncio.wait_for(self.in_position(), 20)
        self.evt_inPosition.set_put(
            azimuth=self.model.encoder_motion.azimuth,
            elevation=self.model.encoder_motion.elevation,
            focus=self.model.encoder_motion.focus,
            mask=self.model.encoder_motion.mask_select,
            mask_rotation=self.model.encoder_motion.mask_rotate,
        )

    async def do_unpark(self, data):
        """Unpark the CBP."""
        self.assert_enabled("unpark")
        await self.model.set_unpark()
        self.evt_inPosition.set_put(
            azimuth=self.model.encoder_motion.azimuth,
            elevation=self.model.encoder_motion.elevation,
            focus=self.model.encoder_motion.focus,
            mask=self.model.encoder_motion.mask_select,
            mask_rotation=self.model.encoder_motion.mask_rotate,
        )
        await asyncio.wait_for(self.in_position(), 20)
        self.evt_inPosition.set_put(
            azimuth=self.model.encoder_motion.azimuth,
            elevation=self.model.encoder_motion.elevation,
            focus=self.model.encoder_motion.focus,
            mask=self.model.encoder_motion.mask_select,
            mask_rotation=self.model.encoder_motion.mask_rotate,
        )

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
        await self.model.set_mask(data.mask)
        self.evt_target.set_put(
            azimuth=self.model.azimuth_target,
            elevation=self.model.altitude_target,
            focus=self.model.focus_target,
            mask=self.model.mask_target,
            mask_rotation=self.model.mask_rotation_target,
        )
        self.evt_inPosition.set_put(
            azimuth=self.model.encoder_motion.azimuth,
            elevation=self.model.encoder_motion.elevation,
            focus=self.model.encoder_motion.focus,
            mask=self.model.encoder_motion.mask_select,
            mask_rotation=self.model.encoder_motion.mask_rotate,
        )
        await asyncio.wait_for(self.in_position(), 20)
        self.evt_inPosition.set_put(
            azimuth=self.model.encoder_motion.azimuth,
            elevation=self.model.encoder_motion.elevation,
            focus=self.model.encoder_motion.focus,
            mask=self.model.encoder_motion.mask_select,
            mask_rotation=self.model.encoder_motion.mask_rotate,
        )

    async def handle_summary_state(self):
        if self.disabled_or_enabled:
            if self.simulation_mode and self.simulator is None:
                self.simulator = mock_server.MockServer()
                await self.simulator.start()
            if self.telemetry_task.done():
                self.telemetry_task = asyncio.create_task(self.telemetry())
            if self.model.connected is False:
                await self.model.connect()
            if self.model.park is True:
                await self.model.set_unpark()
        else:
            if self.simulator is not None:
                await self.simulator.stop()
                self.simulator = None
            if self.model.connected is True:
                await self.model.disconnect()
            self.telemetry_task.cancel()

    async def configure(self, config):
        self.model.configure(config)

    @staticmethod
    def get_config_pkg():
        return "ts_config_mtcalsys"

    async def close_tasks(self):
        await super().close_tasks()
        self.telemetry_task.cancel()
        await self.model.disconnect()
        if self.simulator is not None:
            await self.simulator.stop()
            self.simulator = None

    async def in_position(self):
        while not self.model.in_position:
            await asyncio.sleep(self.heartbeat_interval)
        self.log.info("Motion finished")
