import pathlib
from . import component, mock_server
import asyncio
from lsst.ts import salobj

__all__ = ["CBPCSC"]


class CBPCSC(salobj.ConfigurableCsc):
    """This defines the CBP CSC using ts_salobj.

    Parameters
    ----------
    simulation_mode : `int`, optional
    initial_state : `lsst.ts.salobj.State`, optional
    config_dir : `None` or `str` or `pathlib.Path`, optional

    Attributes
    ----------

    component : `CBPComponent`
    simulator : `None` or `MockServer`
    telemetry_task : `asyncio.Future`

    """

    valid_simulation_modes = (0, 1)
    """The valid simulation modes for the CBP."""

    def __init__(
        self,
        simulation_mode=0,
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
        self.component = component.CBPComponent()
        self.simulator = None
        self.telemetry_task = salobj.make_done_future()
        self.log.info("CBP CSC initialized")

    async def do_move(self, data):
        """Move the CBP mount to a specified position.

        Parameters
        ----------
        data : `cmd_move.DataType`

        """
        self.log.debug("Begin move")
        self.assert_enabled("move")
        await asyncio.gather(
            self.component.move_elevation(data.elevation),
            self.component.move_azimuth(data.azimuth),
        )
        await asyncio.wait_for(self.in_position(), 20)

    async def telemetry(self):
        """Publish the updated telemetry.

        """
        while True:
            self.log.debug("Begin sending telemetry")
            await self.component.update_status()
            self.tel_azimuth.set_put(azimuth=self.component.azimuth)
            self.tel_elevation.set_put(elevation=self.component.elevation)
            self.tel_focus.set_put(focus=self.component.focus)
            self.tel_mask.set_put(
                mask=self.component.mask, mask_rotation=self.component.mask_rotation
            )
            self.tel_parked.set_put(
                autoparked=self.component.auto_park, parked=self.component.park
            )
            self.tel_status.set_put(
                panic=self.component.panic_status,
                azimuth=self.component.encoder_status.azimuth,
                elevation=self.component.encoder_status.elevation,
                mask=self.component.encoder_status.mask_select,
                mask_rotation=self.component.encoder_status.mask_rotate,
                focus=self.component.encoder_status.focus,
            )
            if self.component.panic_status:
                self.fault(1, "CBP Panicked. Check hardware and reset device.")

            await asyncio.sleep(self.heartbeat_interval)

    async def do_setFocus(self, data):
        """Sets the focus.

        Parameters
        ----------
        data : `cmd_setFocus.DataType`

        """
        self.assert_enabled("setFocus")
        await self.component.change_focus(data.focus)
        await asyncio.wait_for(self.in_position(), 20)

    async def do_park(self, data):
        """Park the CBP.

        Parameters
        ----------
        data : `cmd_park.DataType`

        """
        self.assert_enabled("park")
        await self.component.set_park()
        await asyncio.wait_for(self.in_position(), 20)

    async def do_unpark(self, data):
        """Unpark the CBP.

        Parameters
        ----------
        data : `cmd_unpark.DataType`
        """
        self.assert_enabled("unpark")
        await self.component.set_unpark()
        await asyncio.wait_for(self.in_position(), 20)

    async def do_changeMask(self, data):
        """Changes the mask.

        Parameters
        ----------
        data : `cmd_changeMask.DataType`

        """
        self.assert_enabled("changeMask")
        await self.component.set_mask(data.mask)
        await asyncio.wait_for(self.in_position(), 20)

    async def handle_summary_state(self):
        """Handle the summary state."""
        if self.disabled_or_enabled:
            if self.simulation_mode and self.simulator is None:
                self.simulator = mock_server.MockServer()
                await self.simulator.start()
            if self.telemetry_task.done():
                self.telemetry_task = asyncio.create_task(self.telemetry())
            if self.component.connected is False:
                await self.component.connect()
            if self.component.park is True:
                await self.component.set_unpark()
        else:
            if self.simulator is not None:
                await self.simulator.stop()
                self.simulator = None
            if self.component.connected is True:
                await self.component.disconnect()
            self.telemetry_task.cancel()

    async def configure(self, config):
        """Configure the CSC.

        Parameters
        ----------
        config : `types.SimpleNamespace`
        """
        self.component.configure(config)

    @staticmethod
    def get_config_pkg():
        """Return the name of the configuration repository."""
        return "ts_config_mtcalsys"

    async def close_tasks(self):
        await super().close_tasks()
        self.telemetry_task.cancel()
        await self.component.disconnect()
        if self.simulator is not None:
            await self.simulator.stop()
            self.simulator = None

    async def in_position(self):
        """Wait for CBP to be in position.

        * Publish the target event.
        * Publish the inPosition event.
        * Wait for CBP to be in position.
        * Publish the inPosition event.
        """
        self.evt_target.set_put(
            azimuth=self.component.azimuth_target,
            elevation=self.component.altitude_target,
            focus=self.component.focus_target,
            mask=self.component.mask_target,
            mask_rotation=self.component.mask_rotation_target,
        )
        await self.publish_in_position()
        while not self.component.in_position:
            await asyncio.sleep(self.heartbeat_interval)
        await self.publish_in_position()
        self.log.info("Motion finished")

    async def publish_in_position(self):
        """Publish inPosition event"""
        await self.component.update_status()
        self.evt_inPosition.set_put(
            azimuth=self.component.encoder_in_position.azimuth,
            elevation=self.component.encoder_in_position.elevation,
            focus=self.component.encoder_in_position.focus,
            mask=self.component.encoder_in_position.mask_select,
            mask_rotation=self.component.encoder_in_position.mask_rotate,
        )
