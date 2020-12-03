#!/usr/bin/env python

import asyncio
from lsst.ts.cbp.csc import CBPCSC

asyncio.run(CBPCSC.amain(index=None))
