import subprocess
import asyncio

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


class CscTestCase(asynctest.TestCase):
    def setUp(self):
        self.simulator_process = subprocess.Popen(["lewis", "-k", "lsst.ts.cbp", "simulator"])

    def tearDown(self):
        self.simulator_process.terminate()

    async def test_standard_state_transitions(self):
        async with Harness(initial_state=salobj.State.STANDBY) as harness:
            asyncio.sleep(5)
            state = await harness.remote.evt_summaryState.next(flush=False, timeout=STD_TIMEOUT)
            self.assertEqual(state.summaryState, salobj.State.STANDBY)

            await harness.remote.cmd_start.set_start(settingsToApply="default")
            self.assertEqual(harness.csc.summary_state, salobj.State.DISABLED)
            state = await harness.remote.evt_summaryState.next(flush=False, timeout=STD_TIMEOUT)
            self.assertEqual(state.summaryState, salobj.State.DISABLED)

            await harness.remote.cmd_enable.start()
            self.assertEqual(harness.csc.summary_state, salobj.State.ENABLED)
            state = await harness.remote.evt_summaryState.next(flush=False, timeout=STD_TIMEOUT)
            self.assertEqual(state.summaryState, salobj.State.ENABLED)

            await harness.remote.cmd_disable.start()
            self.assertEqual(harness.csc.summary_state, salobj.State.DISABLED)
            state = await harness.remote.evt_summaryState.next(flush=False, timeout=STD_TIMEOUT)
            self.assertEqual(state.summaryState, salobj.State.DISABLED)

            await harness.remote.cmd_standby.start()
            self.assertEqual(harness.csc.summary_state, salobj.State.STANDBY)
            state = await harness.remote.evt_summaryState.next(flush=False, timeout=STD_TIMEOUT)
            self.assertEqual(state.summaryState, salobj.State.STANDBY)
