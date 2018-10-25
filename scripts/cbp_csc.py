#!/usr/bin/env python
from lsst.ts.cbp.statemachine import CBPCsc
import argh
import asyncio
import sys
import logging
logging.captureWarnings(True)

@argh.arg('-v','--verbose',choices=['info','debug'])
def main(verbose="info"):
    log = logging.getLogger()
    ch = logging.StreamHandler()
    if verbose == "info":
        log.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    elif verbose == "debug":
        log.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    parser = argh.ArghParser()
    cbp=CBPCsc("140.252.33.12",5000)
    log.info("CBP initialized")
    loop = asyncio.get_event_loop()
    try:
        log.info('Running CSC (Hit ctrl+c to stop it')
        loop.run_forever()
    except KeyboardInterrupt as e:
        log.info("Stopping CBP CSC")
    except Exception as e:
        log.error(e)
    finally:
        loop.close()



if __name__ == '__main__':
    argh.dispatch_command(main)