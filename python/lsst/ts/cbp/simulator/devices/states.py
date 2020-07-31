from lewis.core.statemachine import State
from lewis.core import approaches


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
            self._context.mask_rotation = approaches.linear(
                old_mask_rotation,
                self._context.target_mask_rotation,
                20,
                dt)
        self.log.info(f'Moved azimuth ({old_azimuth} -> {self._context.azimuth})')
        self.log.info(f'Moved altitude ({old_altitude} -> {self._context.altitude})')
        self.log.info(f'Rotating mask ({old_mask_rotation}-> {self._context.mask_rotation})')


class DefaultParkedState(State):
    def in_state(self, dt):
        self._context.altitude = -70
