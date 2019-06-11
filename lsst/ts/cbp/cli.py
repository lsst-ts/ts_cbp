#!/usr/bin/env python
import asyncio
import logging
import argparse
import argh
from lsst.ts.cbp.statemachine import CBPCsc
logging.captureWarnings(True)


@argh.arg('-ll', '--log-level', choices=['info', 'debug'])
def start(log_level="info",simulation_mode=0):
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
    cbp=CBPCsc(simulation_mode=0)
    log.info("CBP CSC initialized")
    loop = asyncio.get_event_loop()
    try:
        log.info('Running CSC (Hit ctrl+c to stop it')
        loop.run_until_complete(cbp.done_task)
    except KeyboardInterrupt as kbe:
        log.info("Stopping CBP CSC")
        log.exception(kbe)
    except Exception as e:
        log.exception(e)
    finally:
        loop.close()


def create_parser():
    """Creates the parser.

    Returns
    -------

    """
    parser = argparse.ArgumentParser()
    argh.set_default_command(parser, start)
    return parser


def main():
    """Dispatches the command and runs the program.

    Returns
    -------

    """
    parser = create_parser()
    argh.dispatch(parser)


if __name__ == '__main__':
    main()
