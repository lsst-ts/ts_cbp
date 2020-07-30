from lewis.devices import StateMachineDevice

from lewis.core.statemachine import State
from lewis.core import approaches
from lewis.adapters.stream import StreamInterface, Cmd, scanf

from collections import OrderedDict


class DefaultMovingState(State):
    def in_state(self, dt):
        old_altitude = self._context.altitude
        old_azimuth = self._context.azimuth
        old_mask_rotation = self._context.mask_rotation
        if self._context.altitude != self._context.target_altitude:
            self._context.altitude = approaches.linear(old_altitude, self._context.target_altitude, 20, dt)
        if self._context.azimuth != self._context.target_azimuth:
            self._context.azimuth = approaches.linear(old_azimuth, self._context.target_azimuth, 20, dt)
        if self._context.mask_rotation != self._context.target_mask_rotation:
            self._context.mask_rotation = approaches.linear(old_mask_rotation, self._context.target_mask_rotation, 20, dt)
        self.log.info(f'Moved azimuth ({old_azimuth} -> {self._context.azimuth})')
        self.log.info(f'Moved altitude ({old_altitude} -> {self._context.altitude})')
        self.log.info(f'Rotating mask ({old_mask_rotation}-> {self._context.mask_rotation})')


class DefaultParkedState(State):
    def in_state(self, dt):
        self._context.altitude = -70


class SimulatedCBP(StateMachineDevice):
    def _initialize_data(self):
        self.altitude = 0
        self.target_altitude = 0
        self.azimuth = 0
        self.target_azimuth = 0
        self.mask = 0
        self.target_mask = 0
        self.mask_rotation = 0
        self.target_mask_rotation = 0
        self.focus = 0
        self.target_focus = 0

        self.status_parked = 0
        self.status_panic = 0
        self.status_encoder_1 = 1
        self.status_encoder_2 = 1
        self.status_encoder_3 = 1
        self.status_encoder_4 = 1
        self._statusencoder_5 = 1
        
    def _get_state_handlers(self):
        return {
            'idle': State(),
            'moving': DefaultMovingState(),
            'parked': DefaultParkedState()
        }

    def _get_initial_state(self):
        return 'idle'

    def _get_transition_handlers(self):
        return OrderedDict([
            (('idle', 'moving'), lambda: self.azimuth != self.target_azimuth or self.altitude != self.target_altitude or self.mask_rotation != self.target_mask_rotation),
            (('moving', 'idle'), lambda: self.azimuth == self.target_azimuth or self.altitude == self.target_altitude or self.mask_rotation == self.target_mask_rotation)
        ])

    @property
    def state(self):
        return self._csm.state

    
class CBPStreamInterface(StreamInterface):
    commands = {
        Cmd('get_azimuth', r'^az=\?$'),
        Cmd('set_azimuth', scanf("new_az=%f"), argument_mappings=(float,)),
        Cmd('get_altitude', r'^alt=\?$'),
        Cmd('set_altitude', scanf("new_alt=%f"), argument_mappings=(float,)),
        Cmd('get_focus', r'^foc=\?$'),
        Cmd('set_focus', scanf("new_foc=%f"), argument_mappings=(float,)),
        Cmd('get_mask', r'^msk=\?$'),
        Cmd('set_mask', scanf("new_msk=%f"), argument_mappings=(float,)),
        Cmd('get_mask_rotation', r'^rot=\?$'),
        Cmd('set_mask_rotation', scanf("new_rot=%f"), argument_mappings=(float,)),
        Cmd('check_park', r'^park=\?$'),
        Cmd('set_park', scanf("park=%f"), argument_mappings=(float,)),
        Cmd('check_panic', r'^wdpanic=\?$'),
        Cmd('check_encoder_1', r'^AAstat=\?$'),
        Cmd('check_encoder_2', r'^ABstat=\?$'),
        Cmd('check_encoder_3', r'^ACstat=\?$'),
        Cmd('check_encoder_4', r'^ADstat=\?$'),
        Cmd('check_encoder_5', r'^AEstat=\?$')
    }

    in_terminator = '\r'
    out_terminator = '\r'

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
