from lewis.adapters.stream import StreamInterface, Cmd, scanf


class CBPStreamInterface(StreamInterface):
    commands = {
        Cmd("get_azimuth", r"^az=\?$"),
        Cmd("set_azimuth", scanf("new_az=%f"), argument_mappings=(float,)),
        Cmd("get_altitude", r"^alt=\?$"),
        Cmd("set_altitude", scanf("new_alt=%f"), argument_mappings=(float,)),
        Cmd("get_focus", r"^foc=\?$"),
        Cmd("set_focus", scanf("new_foc=%f"), argument_mappings=(float,)),
        Cmd("get_mask", r"^msk=\?$"),
        Cmd("set_mask", scanf("new_msk=%f"), argument_mappings=(float,)),
        Cmd("get_mask_rotation", r"^rot=\?$"),
        Cmd("set_mask_rotation", scanf("new_rot=%f"), argument_mappings=(float,)),
        Cmd("check_park", r"^park=\?$"),
        Cmd("set_park", scanf("park=%f"), argument_mappings=(float,)),
        Cmd("check_auto_park", r"^autopark=\?$"),
        Cmd("check_panic", r"^wdpanic=\?$"),
        Cmd("check_encoder_1", r"^AAstat=\?$"),
        Cmd("check_encoder_2", r"^ABstat=\?$"),
        Cmd("check_encoder_3", r"^ACstat=\?$"),
        Cmd("check_encoder_4", r"^ADstat=\?$"),
        Cmd("check_encoder_5", r"^AEstat=\?$"),
    }

    in_terminator = "\r"
    out_terminator = "\r"

    def get_azimuth(self):
        return self.device.azimuth

    def set_azimuth(self, new_azimuth):
        self.device.target_azimuth = new_azimuth
        return ""

    def get_altitude(self):
        return self.device.altitude

    def set_altitude(self, new_altitude):
        self.device.target_altitude = new_altitude
        return ""

    def get_focus(self):
        return self.device.focus

    def set_focus(self, new_focus):
        self.device.focus = new_focus
        return ""

    def get_mask(self):
        return self.device.mask

    def set_mask(self, new_mask):
        self.device.mask = new_mask
        return ""

    def get_mask_rotation(self):
        return self.device.mask_rotation

    def set_mask_rotation(self, new_mask_rotation):
        self.device.target_mask_rotation = new_mask_rotation
        return ""

    def check_park(self):
        return self.device.status_parked

    def check_auto_park(self):
        return self.device.status_parked

    def set_park(self, park):
        self.device.status_parked = park
        return ""

    def check_panic(self):
        return self.device.status_panic

    def check_encoder_1(self):
        return self.device.status_encoder_1

    def check_encoder_2(self):
        return self.device.status_encoder_2

    def check_encoder_3(self):
        return self.device.status_encoder_3

    def check_encoder_4(self):
        return self.device.status_encoder_4

    def check_encoder_5(self):
        return self.device.status_encoder_5
