#!/usr/bin/env python
from lsst.ts.cbp.statemachine import CBPCsc
import argh
import asyncio
import logging
import argparse
logging.captureWarnings(True)


@argh.arg('-ll','--log-level',choices=['info','debug'])
def start(log_level="info"):
    """Starts the CSC.

    """
    log = logging.getLogger()
    ch = logging.StreamHandler()
    if log_level == "info":
        log.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    elif log_level == "debug":
        log.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    cbp=CBPCsc("140.252.33.12",5000)
    log.info("CBP CSC initialized")
    loop = asyncio.get_event_loop()
    try:
        log.info('Running CSC (Hit ctrl+c to stop it')
        loop.run_forever()
    except KeyboardInterrupt as kbe:
        log.info("Stopping CBP CSC")
    except Exception as e:
        log.error(e)
    finally:
        loop.close()


def create_parser():
    parser = argparse.ArgumentParser()
    argh.set_default_command(parser,start)
    return parser


def main():
    parser = create_parser()
    argh.dispatch(parser)



if __name__ == '__main__':
    main()