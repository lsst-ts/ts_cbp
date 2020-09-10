__all__ = ["CBPComponent", "Status"]

import logging
import asyncio
import types
import enum


class Status(enum.Flag):
    """The status for the encoders.
    """

    AZIMUTH = enum.auto()
    ELEVATION = enum.auto()
    MASK_SELECT = enum.auto()
    MASK_ROTATE = enum.auto()
    FOCUS = enum.auto()


class CBPComponent:
    """This class is for implementing the CBP component.

    The component implements a python wrapper over :term:`DMC` code written by
    DFM Manufacturing.
    The following api exposes commands that move the motors of the CBP, sets
    the focus and selects the mask.

    Attributes
    ----------
    log : `logging.Logger`
        The logger for the component

    socket : `socket.Socket`
        The socket that handles the TCP/IP connection for the CBP

    altitude : `float`
        The value of the CBP altitude encoder in degrees.

    azimuth : `float`
        The value of the CBP azimuth encoder in degrees.

    mask : `str`
        The current mask name

    mask_rotation : `float`
        The current value of the mask rotation encoder in degrees.

    masks : `SimpleNamespace`
        A simplenamespace that contains the mask names and rotation values and
        id.

    focus : `float`
        The current value of the focus encoder in microns.

    panic_status : `float`
        The current value of the panic variable in the CBP dmc code.
        A non-zero value represents a panic state and causes the motors to
        cease functioning until panic is dealt with or goes away.
        This status is set by the values of the other statuses.

    auto_park : `float`
        The current value of the auto_park variable.
        If this value is one, that means that CBP suffered a power loss that
        lasted more than 12 seconds and was on battery back up.
        The CBP will then park itself automatically, moving azimuth to 0 and
        altitude to -70 and locking focus and mask.
        To un-park CBP, the park variable should be set to zero.

    park : `float`
        The current value of the park variable.
        This value can be set to one or zero, if set to one it will park the
        CBP if set to zero it will un-park.

    encoder_status : `Status`
        A flag enum that contains the status information for each encoder.

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

        self.altitude = None
        self.azimuth = None
        self.mask = None
        self.mask_rotation = None

        self.focus = None
        self.host = None
        self.port = None
        self.panic_status = None
        self.auto_park = None
        self.park = None
        self.simulation_mode = 0
        self.encoder_status = Status
        self.generate_mask_info()
        self.log.info("CBP component initialized")

    def generate_mask_info(self):
        """Generates initial mask info.
        """
        mask_dict = {
            f"{i}": types.SimpleNamespace(name=f"Empty {i}", rotation=0, id=i)
            for i in (1, 2, 3, 4, 5, 9)
        }
        mask_dict["9"].name = "Unknown"
        self.masks = types.SimpleNamespace(**mask_dict)
        self.log.info(f"{self.masks}")

    async def send_command(self, msg):
        """Sends the encoded command and reads the reply.

        Parameters
        ----------
        msg : `str`
            The string command to be sent.
        """
        async with self.lock:
            msg = msg + "\r"
            self.log.info(f"Writing: {msg}")
            self.writer.write(msg.encode("ascii"))
            await self.writer.drain()
            reply = await self.reader.readuntil(b"\r")
            reply = reply.decode("ascii").strip("\r")
            self.log.info(reply)
            if reply != "":
                reply = reply[0]
            return reply

    async def connect(self):
        """Creates a socket and connects to the CBP's static address and
        designated port.


        Returns
        -------
        None
            Nothing

        """
        async with self.lock:
            connect_task = asyncio.open_connection(host=self.host, port=self.port)
            self.reader, self.writer = await asyncio.wait_for(
                connect_task, timeout=self.long_timeout
            )

    async def disconnect(self):
        """Disconnects from the tcp socket.
        """
        async with self.lock:
            self.reader = None
            if self.writer is not None:
                try:
                    self.writer.write_eof()
                    await asyncio.wait_for(self.writer.drain(), timeout=self.timeout)
                finally:
                    self.writer.close()
                    self.writer = None

    async def get_azimuth(self):
        """Gets azimuth value from azimuth encoder which is in degrees.

        Returns
        -------
        None
        """
        self.azimuth = float(await self.send_command("az=?"))

    async def move_azimuth(self, position: float):
        """This moves the horizontal axis to the value sent by the user.

        Parameters
        ----------
        position: float
            This is the value in degrees that is sent to the CBP in order to
            move the horizontal axis.

        Returns
        -------
        None

        """
        if position < -45 or position > 45:
            raise ValueError("New azimuth value exceeds Azimuth limit.")
        else:
            await self.send_command(f"new_az={position}")

    async def get_altitude(self):
        """This gets the altitude value from the altitude encoder in degrees.

        Returns
        -------
        None

        """
        self.log.debug("get_altitude sent")
        self.altitude = float(await self.send_command("alt=?"))

    async def move_altitude(self, position: float):
        """This moves the vertical axis to the value that the user sent.

        Parameters
        ----------
        position: float
            The value to move the altitude to which is in degrees.

        Returns
        -------
        None

        """
        if position < -69 or position > 45:
            raise ValueError("New altitude value exceeds altitude limit.")
        else:
            await self.send_command(f"new_alt={position}")

    async def get_focus(self):
        """This gets the value of the focus encoder. Units: microns

        Returns
        -------
        None

        """
        self.focus = int(await self.send_command("foc=?"))

    async def change_focus(self, position: int):
        """This changes the focus to whatever value the user sent.

        Parameters
        ----------
        position: int
            The value of the new focus in microns.

        Returns
        -------
        None

        """
        if position < 0 or position > 13000:
            raise ValueError("New focus value exceeds focus limit.")
        else:
            await self.send_command(f"new_foc={position}")

    async def get_mask(self):
        """This gets the current mask value from the encoder which is converted
        into the name of the mask.

        Returns
        -------
        None

        """
        # If mask encoder is off then it will return "9.0" which is unknown
        # mask
        mask = str(int(float(await self.send_command("msk=?"))))
        self.mask = self.masks.__dict__.get(mask).name

    async def set_mask(self, mask: str):
        """This sets the mask value

        Parameters
        ----------
        mask: str
            This is the name of the mask which is converted to an int using a
            dictionary.

        Returns
        -------
        None

        """
        await self.send_command(f"new_msk={self.masks.__dict__.get(mask).id}")

    async def get_mask_rotation(self):
        """This gets the mask rotation value from the encoder which is in
        degrees.

        Returns
        -------
        None

        """
        self.mask_rotation = float(await self.send_command("rot=?"))

    async def set_mask_rotation(self, mask_rotation: float):
        """This sets the mask rotation

        Parameters
        ----------
        mask_rotation: float
            The mask_rotation value that will be sent.

        Returns
        -------
        None

        """
        if mask_rotation < 0 or mask_rotation > 360:
            raise ValueError("New mask rotation value exceeds mask rotation limits.")
        await self.send_command(f"new_rot={mask_rotation}")

    async def check_panic_status(self):
        """Gets the panic variable from CBP

        Returns
        -------
        None

        """
        self.panic_status = bool(await self.send_command("wdpanic=?"))

    async def check_auto_park(self):
        """Gets the autopark variable from CBP

        Returns
        -------
        None

        """
        self.auto_park = bool(await self.send_command("autopark=?"))

    async def check_park(self):
        """Gets the park variable from CBP

        Returns
        -------
        None

        """
        self.park = bool(await self.send_command("park=?"))

    async def set_park(self):
        """A function that tells the CBP to park or un-park depending on the
        value given.

        Parameters
        ----------
        park: int {0,1}
            A boolean int which tells the CBP to park or not.

        Returns
        -------
        None

        """
        await self.send_command(f"park=1")

    async def set_unpark(self):
        await self.send_command("park=0")

    async def check_cbp_status(self):
        """Checks the status of the encoders.

        Returns
        -------
        None

        """
        self.encoder_status.AZIMUTH = bool(await self.send_command("AAstat=?"))
        self.encoder_status.ELEVATION = bool(await self.send_command("ABstat=?"))
        self.encoder_status.MASK_SELECT = bool(await self.send_command("ACstat=?"))
        self.encoder_status.MASK_ROTATE = bool(await self.send_command("ADstat=?"))
        self.encoder_status.FOCUS = bool(await self.send_command("AEstat=?"))

    async def get_cbp_telemetry(self):
        """Gets the position data of the CBP.

        Returns
        -------
        None

        """
        await self.get_altitude()
        await self.get_azimuth()
        await self.get_focus()
        await self.get_mask()
        await self.get_mask_rotation()

    def configure(self, config):
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

    async def publish(self):
        """This updates the attributes within the component.

        Returns
        -------
        None

        """
        await self.check_panic_status()
        await self.check_cbp_status()
        await self.check_park()
        await self.check_auto_park()
        await self.get_cbp_telemetry()

    def set_simulation_mode(self, simulation_mode):
        self.simulation_mode = simulation_mode
