#!/usr/bin/python

import sys, pathlib
import logging as log
import time
import logging.handlers as log_handler
import raspi_cpu_information
from mqttToInflux import mqttInfluxInterface
from influxDB_interface import InfluxDBInterface
import threading

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
fileHandler = log_handler.RotatingFileHandler(filename=logFile, mode='a', maxBytes=10 * 1024 * 1024, backupCount=10,
                                              encoding=None, delay=False, errors=None)

fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = log.StreamHandler()
consoleHandler.setFormatter(logFormatter)

# TODO: Configuration of INFLUX and MQTT in an XML file
''' InfluxDB settings '''
influxHost = 'localhost'
influxPort = 8086
influxDatabase = 'home'

''' InfluxDB interface instance '''
influxDB_interface = InfluxDBInterface(influxHost, influxPort, influxDatabase)

''' MQTT settings '''
BROKER_ADDRESS = "localhost"

''' MQTT InfluxDB interface instance '''
mqttInfluxInterface = mqttInfluxInterface(BROKER_ADDRESS, influxDB_interface)

# TODO: Own class or file for this function
def thread_cpu_information_to_influx():
    while True:
        log.debug("New cycle")
        # Get CPU information in JSON format
        cpu_information = raspi_cpu_information.getCPUInformation()
        # Write CPU information in database
        influxDB_interface.dictToDatabase(cpu_information)
        # Wait before next cycle
        log.debug("Cycle done, go to sleep...")
        time.sleep(30)

TASK01_ENABLE = True
TASK02_ENABLE = True

def main(args):
    log.info("Start application")

    ''' TASK 01: MQTT TO INFLUX INTERFACE '''
    if TASK01_ENABLE:
        t1 = threading.Thread(target=mqttInfluxInterface.thread_mqtt_to_influx, args=())
        t1.start()

    ''' TASK 02: CPU INFORMATION TO INFLUX '''
    if TASK02_ENABLE:
        t2 = threading.Thread(target=thread_cpu_information_to_influx, args=())
        t2.start()

    if TASK01_ENABLE:
        t1.join()

    if TASK02_ENABLE:
        t2.join()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
