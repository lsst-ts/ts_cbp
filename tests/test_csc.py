import asynctest

from lsst.ts import salobj, cbp

STD_TIMEOUT = 15


class CscTestCase(asynctest.TestCase, salobj.BaseCscTestCase):
    async def setUp(self):
        self.server = cbp.MockServer()
        await self.server.start()

    async def tearDown(self):
        await self.server.stop()

    def basic_make_csc(self, initial_state, config_dir=None, **kwargs):
        return cbp.csc.CBPCSC(initial_state=initial_state)

    async def test_standard_state_transitions(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY):
            await self.check_standard_state_transitions(
                enabled_commands=(
                    "changeMask",
                    "clearFault",
                    "moveAltitude",
                    "moveAzimuth",
                    "park",
                    "setFocus",
                )
            )
