__all__ = ["MockServer"]

import asyncio
import re
import logging


class MockServer:
    def __init__(self, log=None):
        self.host = "127.0.0.1"
        self.port = 9999
        self.timeout = 5
        self.long_timeout = 30
        self.azimuth = 0
        self.altitude = 0
        self.focus = 0
        self.mask = 1
        self.panic_status = False
        self.encoders = [False, False, False, False, False]
        self.park = False
        self.auto_park = False
        self.masks = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        self.command_calls = {
            "az": self.do_azimuth,
            "alt": self.do_altitude,
            "foc": self.do_focus,
            "msk": self.do_mask,
            "rot": self.do_rotation,
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
        ]
        self.log = logging.getLogger(__name__)

    async def start(self):
        self.log.info("Starting Server")
        self.server = await asyncio.start_server(
            client_connected_cb=self.cmd_loop, host=self.host, port=self.port
        )

    async def stop(self):
        self.log.info("Closing Server")
        self.server.close()
        await asyncio.wait_for(self.server.wait_closed(), timeout=self.timeout)
        self.log.info("Server closed")

    async def cmd_loop(self, reader, writer):
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

    async def do_azimuth(self, azimuth=None):
        if azimuth is None:
            return f"{self.azimuth}"
        else:
            self.azimuth = azimuth

    async def do_altitude(self, altitude):
        if altitude is None:
            return f"{self.altitude}"
        else:
            self.altitude = altitude

    async def do_focus(self, focus):
        if focus is None:
            return f"{self.focus}"
        else:
            self.focus = focus

    async def do_mask(self, mask):
        if mask is None:
            return f"{self.mask}"
        else:
            self.mask = mask

    async def do_rotation(self, rotation):
        if rotation is None:
            return f"{self.masks[self.mask]}"
        else:
            self.masks[self.mask] = rotation

    async def do_park(self, park):
        if park is None:
            return f"{int(self.park)}"
        else:
            self.park = bool(park)
            return ""

    async def do_panic(self):
        return f"{int(self.panic_status)}"

    async def do_aastat(self):
        return f"{int(self.encoders[0])}"

    async def do_abstat(self):
        return f"{int(self.encoders[1])}"

    async def do_acstat(self):
        return f"{int(self.encoders[2])}"

    async def do_adstat(self):
        return f"{int(self.encoders[3])}"

    async def do_aestat(self):
        return f"{int(self.encoders[4])}"

    async def do_autopark(self):
        return f"{int(self.auto_park)}"
