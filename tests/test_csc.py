import subprocess

import asynctest

from lsst.ts import salobj, cbp

STD_TIMEOUT = 15


class Harness:
    def __init__(self, initial_state):
        salobj.test_utils.set_random_lsst_dds_domain()
        self.csc = cbp.csc.CBPCSC(initial_state=initial_state)
        self.remote = salobj.Remote(domain=self.csc.domain, name="CBP", index=0)

    async def __aenter__(self):
        await self.csc.start_task
        return self

    async def __aexit__(self, *args):
        await self.csc.close()


class CscTestCase(asynctest.TestCase, salobj.BaseCscTestCase):
    def setUp(self):
        self.simulator_process = subprocess.Popen(
            ["lewis", "-k", "lsst.ts.cbp", "simulator"]
        )

    def tearDown(self):
        self.simulator_process.terminate()

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
