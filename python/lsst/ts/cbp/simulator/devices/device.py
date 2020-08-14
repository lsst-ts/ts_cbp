from lewis.devices import StateMachineDevice
from collections import OrderedDict
from . import states
from lewis.core.statemachine import State


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
        self.status_encoder_5 = 1

    def _get_state_handlers(self):
        return {
            "idle": State(),
            "moving": states.DefaultMovingState(),
            "parked": states.DefaultParkedState(),
        }

    def _get_initial_state(self):
        return "idle"

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                (
                    ("idle", "moving"),
                    lambda: (
                        self.azimuth != self.target_azimuth
                        or self.altitude != self.target_altitude
                        or self.mask_rotation != self.target_mask_rotation
                    ),
                ),
                (
                    ("moving", "idle"),
                    lambda: (
                        self.azimuth == self.target_azimuth
                        or self.altitude == self.target_altitude
                        or self.mask_rotation == self.target_mask_rotation
                    ),
                ),
            ]
        )

    @property
    def state(self):
        return self._csm.state
