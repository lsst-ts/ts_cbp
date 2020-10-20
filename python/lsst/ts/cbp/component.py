__all__ = ["CBPComponent", "EncoderStatus", "ActuatorInPosition"]

import logging
import asyncio
import types


class EncoderStatus:
    """The status for the encoders.

    If values are false, then the encoder(s) are fine.
    If the values are true, they are not fine.

    Attributes
    ----------
    azimuth : `bool`
    elevation : `bool`
    mask_select : `bool`
    mask_rotate : `bool`
    focus : `bool`
    """

    def __init__(self):
        self.azimuth = False
        self.elevation = False
        self.mask_select = False
        self.mask_rotate = False
        self.focus = False


class ActuatorInPosition:
    """The motion status of the actuators.

    Attributes
    ----------
    azimuth : `bool`
    elevation : `bool`
    mask_select : `bool`
    mask_rotate : `bool`
    focus : `bool`
    """

    def __init__(self):
        self.azimuth = False
        self.elevation = False
        self.mask_select = False
        self.mask_rotate = False
        self.focus = False


class CBPComponent:
    """This class is for implementing the CBP component.

    The component implements a python wrapper over :term:`DMC` code written by
    DFM Manufacturing.
    The following api exposes commands that move the motors of the CBP, sets
    the focus and selects the mask.

    Attributes
    ----------
    log : `logging.Logger`
    reader : `asyncio.StreamReader`
    writer : `asyncio.StreamWriter`
    lock : `asyncio.Lock`
    timeout : `int`
    long_timeout : `int`
    altitude : `None` or `float`
    azimuth : `None` or `float`
    mask : `None` or `str`
    mask_rotation : `None` or `float`
    focus : `None` or `int`
    altitude_target : `float`
    azimuth_target : float`
    mask_target : `str`
    mask_rotation_target : `float`
    focus_target : `int`
    host : `str`
    port : `int`
    panic_status : `None` or `bool`
    auto_park : `None` or `bool`
    park : `None` or `bool`
    simulation_mode : `int`
    encoder_status : `EncoderStatus`
    encoder_in_position : `ActuatorInPosition`
    connected : `bool`
    error_tolerance : `float`

    Notes
    -----

    The class uses the python socket module to build TCP/IP connections to the
    Galil controller for the CBP.
    The underlying api is built on :term:`DMC`.
    """

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.reader = None
        self.writer = None
        self.lock = asyncio.Lock()
        self.timeout = 5
        self.long_timeout = 30

        self.elevation = None
        self.azimuth = None
        self.mask = None
        self.mask_rotation = None
        self.focus = None

        self.altitude_target = 0
        self.azimuth_target = 0
        self.mask_target = "Mask 1"
        self.mask_rotation_target = 0
        self.focus_target = 0

        self.host = None
        self.port = None
        self.panic_status = None
        self.auto_park = None
        self.park = None
        self.simulation_mode = 0
        self.encoder_status = EncoderStatus()
        self.encoder_in_position = ActuatorInPosition()
        self.in_position = False
        self.connected = False
        self.error_tolerance = 0.3
        self.generate_mask_info()
        self.log.info("CBP component initialized")

    def generate_mask_info(self):
        """Generate initial mask info."""
        mask_dict = {
            f"{i}": types.SimpleNamespace(name=f"Empty {i}", rotation=0, id=i)
            for i in (1, 2, 3, 4, 5, 9)
        }
        mask_dict["9"].name = "Unknown"
        self.masks = types.SimpleNamespace(**mask_dict)

    def get_in_position_status(self):
        """Get the in position status of each actuator."""
        self.encoder_in_position.azimuth = (
            abs(self.azimuth - self.azimuth_target) < self.error_tolerance
        )
        self.encoder_in_position.elevation = (
            abs(self.elevation - self.altitude_target) < self.error_tolerance
        )
        self.encoder_in_position.mask_select = self.mask == self.mask_target
        self.encoder_in_position.mask_rotate = (
            abs(self.mask_rotation - self.mask_rotation_target) < self.error_tolerance
        )
        self.encoder_in_position.focus = (
            abs(self.focus - self.focus_target) < self.error_tolerance
        )
        self.in_position = (
            self.encoder_in_position.azimuth
            and self.encoder_in_position.elevation
            and self.encoder_in_position.mask_select
            and self.encoder_in_position.mask_rotate
            and self.encoder_in_position.focus
        )
        self.log.info(f"In position:{self.in_position}")

    async def send_command(self, msg):
        """Send the encoded command and read the reply.

        Parameters
        ----------
        msg : `str`
            The string command to be sent.

        Returns
        -------
        reply : `str`
            The reply to the command sent.
        """
        async with self.lock:
            msg = msg + "\r"
            self.log.info(f"Writing: {msg}")
            self.writer.write(msg.encode("ascii"))
            await self.writer.drain()
            reply = await self.reader.readuntil(b"\r")
            reply = reply.decode("ascii").strip("\r")
            if reply != "":
                self.log.info(f"reply={reply}")
            return reply

    async def connect(self):
        """Create a socket and connect to the CBP's static address and
        designated port.

        """
        async with self.lock:
            connect_task = asyncio.open_connection(host=self.host, port=self.port)
            self.reader, self.writer = await asyncio.wait_for(
                connect_task, timeout=self.long_timeout
            )
            self.connected = True

    async def disconnect(self):
        """Disconnect from the tcp socket.

        Safe to call even if already disconnected.
        """
        async with self.lock:
            self.reader = None
            if self.writer is not None:
                try:
                    self.writer.write_eof()
                    await asyncio.wait_for(self.writer.drain(), timeout=self.timeout)
                finally:
                    self.writer.close()
                    await self.writer.wait_closed()
                    self.writer = None
                    self.connected = False

    async def get_azimuth(self):
        """Get the azimuth value.
        """
        self.azimuth = float(await self.send_command("az=?"))

    async def move_azimuth(self, position: float):
        """Move the azimuth encoder.

        Parameters
        ----------
        position : `float`
            The desired azimuth (degrees).

        Raises
        ------
        ValueError
            Raised when the new value falls outside the accepted range.

        """
        if position < -45 or position > 45:
            raise ValueError("New azimuth value exceeds Azimuth limit.")
        else:
            self.azimuth_target = position
            await self.send_command(f"new_az={position}")

    async def get_elevation(self):
        """Read and record the mount elevation encoder, in degrees.

        Note that the low-level controller calls this axis "altitude".

        """
        self.elevation = float(await self.send_command("alt=?"))

    async def move_elevation(self, position: float):
        """Move the elevation encoder.

        Parameters
        ----------
        position : `float`
            The desired elevation (degrees)

        Raises
        ------
        ValueError
            Raised when the new value falls outside the accepted range.

        """
        if position < -69 or position > 45:
            raise ValueError("New altitude value exceeds altitude limit.")
        else:
            self.altitude_target = position
            await self.send_command(f"new_alt={position}")

    async def get_focus(self):
        """Get the focus value.

        """
        self.focus = int(await self.send_command("foc=?"))

    async def change_focus(self, position: int):
        """Change focus.

        Parameters
        ----------
        position : `int`
            The value of the new focus (microns).

        Raises
        ------
        ValueError
            Raised when the new value falls outside the accepted range.
        """
        if position < 0 or position > 13000:
            raise ValueError("New focus value exceeds focus limit.")
        else:
            self.focus_target = int(position)
            await self.send_command(f"new_foc={int(position)}")

    async def get_mask(self):
        """Get mask value.

        """
        # If mask encoder is off then it will return "9.0" which is unknown
        # mask
        mask = str(int(float(await self.send_command("msk=?"))))
        self.mask = self.masks.__dict__.get(mask).name

    async def set_mask(self, mask: str):
        """Set the mask value

        Parameters
        ----------
        mask : `str`
            This is the name of the mask which is converted to an int using a
            dictionary.

        Raises
        ------
        KeyError
            Raised when new mask is not a key in the dictionary.

        """
        self.mask_target = self.masks.__dict__.get(mask).name
        self.mask = self.masks.__dict__.get(mask).name
        await self.send_command(f"new_msk={self.masks.__dict__.get(mask).id}")

    async def get_mask_rotation(self):
        """Get the mask rotation value.

        """
        self.mask_rotation = float(await self.send_command("rot=?"))

    async def set_mask_rotation(self, mask_rotation: float):
        """Set the mask rotation

        Parameters
        ----------
        mask_rotation : `float`
            The mask_rotation value that will be sent.


        Raises
        ------
        ValueError
            Raised when the new value falls outside the accepted range.

        """
        if mask_rotation < 0 or mask_rotation > 360:
            raise ValueError("New mask rotation value exceeds mask rotation limits.")
        self.mask_rotation_target = mask_rotation
        await self.send_command(f"new_rot={mask_rotation}")

    async def check_panic_status(self):
        """Get the panic variable from CBP.

        """
        self.panic_status = bool(int(await self.send_command("wdpanic=?")))

    async def check_auto_park(self):
        """Get the autopark variable from CBP
        """
        self.auto_park = bool(int(await self.send_command("autopark=?")))

    async def check_park(self):
        """Get the park variable from CBP.

        """
        self.park = bool(int(await self.send_command("park=?")))
        self.log.info(f"Park: {self.park}")

    async def set_park(self):
        """Park the CBP.
        """
        await self.send_command("park=1")

    async def set_unpark(self):
        """Unpark the CBP."""
        await self.send_command("park=0")

    async def check_cbp_status(self):
        """Read and record the status of the encoders.

        """
        self.encoder_status.azimuth = bool(int(await self.send_command("AAstat=?")))
        self.encoder_status.elevation = bool(int(await self.send_command("ABstat=?")))
        self.encoder_status.mask_select = bool(int(await self.send_command("ACstat=?")))
        self.encoder_status.mask_rotate = bool(int(await self.send_command("ADstat=?")))
        self.encoder_status.focus = bool(int(await self.send_command("AEstat=?")))

    async def get_cbp_telemetry(self):
        """Get the position data of the CBP.

        """
        await self.get_elevation()
        await self.get_azimuth()
        await self.get_focus()
        await self.get_mask()
        await self.get_mask_rotation()

    def configure(self, config):
        """Configure the CBP.

        Parameters
        ----------
        config : `types.SimpleNamespace`
        """
        self.host = config.address
        self.port = config.port
        self.masks.__dict__.get("1").name = config.mask1["name"]
        self.masks.__dict__.get("1").rotation = config.mask1["rotation"]
        self.masks.__dict__.get("2").name = config.mask2["name"]
        self.masks.__dict__.get("2").rotation = config.mask2["rotation"]
        self.masks.__dict__.get("3").name = config.mask3["name"]
        self.masks.__dict__.get("3").rotation = config.mask3["rotation"]
        self.masks.__dict__.get("4").name = config.mask4["name"]
        self.masks.__dict__.get("4").rotation = config.mask4["rotation"]
        self.masks.__dict__.get("5").name = config.mask5["name"]
        self.masks.__dict__.get("5").rotation = config.mask5["rotation"]

    async def update_status(self):
        """Update the status.

        """
        await self.check_panic_status()
        await self.check_cbp_status()
        await self.check_park()
        await self.check_auto_park()
        await self.get_cbp_telemetry()
        self.get_in_position_status()

    def set_simulation_mode(self, simulation_mode):
        """Set the simulation mode.

        Parameters
        ----------
        simulation_mode : `int`
        """
        self.simulation_mode = simulation_mode
