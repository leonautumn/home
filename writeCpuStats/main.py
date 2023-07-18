#!/usr/bin/python

import sys
import time
import pathlib
import logging as log
import logging.handlers as log_handler
from influxDB_interface import InfluxDBInterface
import raspi_cpu_information

''' Get current path of main.py as string '''
currentPath = str(pathlib.Path(__file__).parent.resolve())

''' Log settings '''
logFormat = "%(asctime)s %(levelname)s  %(message)s"
logFormatter = log.Formatter(logFormat)
logFile = currentPath + "/log/" + "Application.log"
log.basicConfig(level=log.DEBUG, format=logFormat)
rootLogger = log.getLogger()

''' Set rotating file handler with following settings:
        - Max. 10 MB per file
        - Max. 10 files in archive
'''
fileHandler = log_handler.RotatingFileHandler(filename=logFile, mode='a', maxBytes=10*1024*1024, backupCount=10,
                                              encoding=None, delay=False, errors=None)

fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = log.StreamHandler()
consoleHandler.setFormatter(logFormatter)

''' InfluxDB settings '''
influxHost = 'localhost'
influxPort = 8086
influxDatabase = 'home'

''' InfluxDB interface instance '''
influxDB_interface = InfluxDBInterface(influxHost, influxPort, influxDatabase)


def main(args):
    log.info("Start application")
    while True:
        log.debug("New cycle")
        # Get CPU information in JSON format
        cpu_information = raspi_cpu_information.getCPUInformation()
        # Write CPU information in database
        influxDB_interface.dictToDatabase(cpu_information)
        # Wait before next cycle
        log.debug("Cycle done, go to sleep...")
        time.sleep(30)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
