__all__ = ["Encoders", "MockServer"]

import asyncio
import re
import logging

from lsst.ts import simactuators


class Encoders:
    """Mocks the CBP encoders.

    Attributes
    ----------
    AZIMUTH : `lsst.ts.simactuators.PointToPointActuator`
    ELEVATION : `lsst.ts.simactuators.PointToPointActuator`
    FOCUS : `lsst.ts.simactuators.PointToPointActuator`
    MASK_SELECT : `lsst.ts.simactuators.PointToPointActuator`
    MASK_ROTATE : `lsst.ts.simactuators.CircularPointToPointActuator`
    """

    def __init__(self):
        self.AZIMUTH = simactuators.PointToPointActuator(
            min_position=-45, max_position=45, speed=10, start_position=0
        )
        self.ELEVATION = simactuators.PointToPointActuator(
            min_position=-69, max_position=45, speed=10, start_position=0
        )
        self.FOCUS = simactuators.PointToPointActuator(
            min_position=0, max_position=13000, speed=200, start_position=0
        )
        self.MASK_SELECT = simactuators.PointToPointActuator(
            min_position=1, max_position=5, speed=1, start_position=1
        )
        self.MASK_ROTATE = simactuators.CircularPointToPointActuator(speed=10)


class MockServer:
    """Mocks the CBP server.

    Parameters
    ----------
    log : `logging.Logger`, optional

    Attributes
    ----------
    host : `str`
    port : `int`
    timeout : `int`
    long_timeout : `int`
    azimuth : `float`
    altitude : `float`
    focus : `int`
    mask : `str`
    panic_status : `bool`
    encoders : `Encoders`
    park : `bool`
    auto_park : `bool`
    masks : `dict` of `str`:`float`
    command_calls : `dict` of `str`:`functools.partial`
    commands : `list` of `re.Pattern`
    log : `logging.Logger`
    """

    def __init__(self, log=None):
        self.host = "127.0.0.1"
        self.port = 9999
        self.timeout = 5
        self.long_timeout = 30
        self.azimuth = 0
        self.altitude = 0
        self.focus = 0
        self.mask = "1"
        self.panic_status = False
        self.encoders = Encoders()
        self.park = False
        self.auto_park = False
        self.masks = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        self.command_calls = {
            "az": self.do_azimuth,
            "new_az": self.do_new_azimuth,
            "alt": self.do_altitude,
            "new_alt": self.do_new_altitude,
            "foc": self.do_focus,
            "new_foc": self.do_new_focus,
            "msk": self.do_mask,
            "new_msk": self.do_new_mask,
            "rot": self.do_rotation,
            "new_rot": self.do_new_rotation,
            "wdpanic": self.do_panic,
            "autopark": self.do_autopark,
            "park": self.do_park,
            "AAstat": self.do_aastat,
            "ABstat": self.do_abstat,
            "ACstat": self.do_acstat,
            "ADstat": self.do_adstat,
            "AEstat": self.do_aestat,
        }
        self.commands = [
            re.compile(r"^(?P<cmd>az)=\?$"),
            re.compile(r"^(?P<cmd>wdpanic)=\?$"),
            re.compile(r"^(?P<cmd>park)=\?$"),
            re.compile(r"^(?P<cmd>park)=(?P<parameter>[01])$"),
            re.compile(r"^(?P<cmd>A[ABCDE]stat)=\?$"),
            re.compile(r"^(?P<cmd>autopark)=\?$"),
            re.compile(r"^(?P<cmd>alt)=\?$"),
            re.compile(r"^(?P<cmd>foc)=\?$"),
            re.compile(r"^(?P<cmd>msk)=\?$"),
            re.compile(r"^(?P<cmd>rot)=\?$"),
            re.compile(r"^(?P<cmd>new_alt)=(?P<parameter>-?[0-6]\d?\.?\d?)"),
            re.compile(r"^(?P<cmd>new_az)=(?P<parameter>-?[0-3][0-5]?\.?\d?)"),
            re.compile(r"^(?P<cmd>new_msk)=(?P<parameter>[1-5])"),
            re.compile(r"^(?P<cmd>new_foc)=(?P<parameter>[0-1]?[0-6]?\d?\d?\d)"),
        ]
        self.log = logging.getLogger(__name__)

    async def start(self):
        """Start the server."""
        self.log.info("Starting Server")
        self.server = await asyncio.start_server(
            client_connected_cb=self.cmd_loop, host=self.host, port=self.port
        )

    async def stop(self):
        """Stop the server."""
        self.log.info("Closing Server")
        self.server.close()
        await asyncio.wait_for(self.server.wait_closed(), timeout=self.timeout)
        self.log.info("Server closed")

    async def cmd_loop(self, reader, writer):
        """Run the command loop.

        Parameters
        ----------
        reader : `asyncio.StreamReader`
        writer : `asyncio.StreamWriter`

        Raises
        ------
        Exception
            Raised when command is not implemented.
        """
        while True:
            line = await reader.readuntil(b"\r")
            self.log.info(f"Received: {line}")
            if not line:
                writer.close()
                return
            line = line.decode().strip("\r")
            self.log.info(f"Decoded {line}")
            for command in self.commands:
                matched_command = command.match(line)
                self.log.info(f"{matched_command}")
                if matched_command:
                    command_group = matched_command.group("cmd")
                    self.log.info(f"Matched {command_group}")
                    if command_group in self.command_calls:
                        self.log.info(f"{command_group}")
                        called_command = self.command_calls[command_group]
                        try:
                            parameter = matched_command.group("parameter")
                            self.log.info(f"{parameter}")
                        except IndexError:
                            parameter = None
                        if parameter is None:
                            msg = await called_command() + "\r"
                        else:
                            msg = await called_command(parameter) + "\r"
                        msg = msg.encode("ascii")
                        writer.write(msg)
                        self.log.info(f"Wrote {msg}")
                        await writer.drain()
                    else:
                        raise Exception("Command is not implemented")

    async def do_azimuth(self):
        """Return azimuth position.

        Returns
        -------
        str
        """
        return f"{self.encoders.AZIMUTH.position()}"

    async def do_new_azimuth(self, azimuth):
        """Set the new azimuth position.

        Parameters
        ----------
        azimuth : `float`

        Returns
        -------
        str
        """
        self.encoders.AZIMUTH.set_position(float(azimuth))
        return ""

    async def do_altitude(self):
        """Return the altitude position.

        Returns
        -------
        str
        """
        return f"{self.encoders.ELEVATION.position()}"

    async def do_new_altitude(self, altitude):
        """Set the new altitude position.

        Parameters
        ----------
        altitude : `float`

        Returns
        -------
        str
        """
        self.encoders.ELEVATION.set_position(float(altitude))
        return ""

    async def do_focus(self):
        """Return the focus value.

        Returns
        -------
        str
        """
        return f"{int(self.encoders.FOCUS.position())}"

    async def do_new_focus(self, focus):
        """Set the new focus value.

        Parameters
        ----------
        focus

        Returns
        -------
        str
        """
        self.encoders.FOCUS.set_position(int(focus))
        return ""

    async def do_mask(self):
        """Return the mask value.

        Returns
        -------
        str
        """
        return f"{self.mask}"

    async def do_new_mask(self, mask):
        """Set the new mask value.

        Parameters
        ----------
        mask : `str`

        Returns
        -------
        str
        """
        self.mask = str(mask)
        return ""

    async def do_rotation(self):
        """Return the mask rotation value.

        Returns
        -------
        str
        """
        return f"{self.masks[self.mask]}"

    async def do_new_rotation(self, rotation):
        """Set the new mask rotation value.

        Parameters
        ----------
        rotation : `float`

        Returns
        -------
        str
        """
        self.masks[self.mask] = float(rotation)
        return ""

    async def do_park(self, park=None):
        """Park or unpark the CBP.

        Parameters
        ----------
        park : `int`, optional

        Returns
        -------
        str
        """
        if park is None:
            self.log.info(f"Park: {self.park}")
            return f"{int(self.park)}"
        else:
            self.log.info(f"Park: {park}")
            self.park = bool(int(park))
            self.log.info(f"Park: {self.park}")
            return ""

    async def do_panic(self):
        """Return the panic status value.

        Returns
        -------
        str
        """
        return f"{int(self.panic_status)}"

    async def do_aastat(self):
        """Return the azimuth encoder status.

        Returns
        -------
        str
        """
        return "0"

    async def do_abstat(self):
        """Return the altitude encoder status.

        Returns
        -------
        str
        """
        return "0"

    async def do_acstat(self):
        """Return the focus encoder status.

        Returns
        -------
        str
        """
        return "0"

    async def do_adstat(self):
        """Return the mask selection encoder status.

        Returns
        -------
        str
        """
        return "0"

    async def do_aestat(self):
        """Return the mask rotation encoder status.

        Returns
        -------
        str
        """
        return "0"

    async def do_autopark(self):
        """Return the autopark value.

        Returns
        -------
        str
        """
        return "0"
