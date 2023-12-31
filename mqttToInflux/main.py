#!/usr/bin/python

import sys, pathlib
import logging as log
import time
import raspi_cpu_information
from mqttToInflux import mqttInfluxInterface, InfluxDBDatasets
from influxDB_interface import InfluxDBInterface
import threading
from setup import setup_logger
from enum import Enum

TEMPERATURE_MIN = -30.0 # unit: °C
TEMPERATURE_MAX = 80.0 # unit: °C
HUMIDITY_MIN = 0.0 # unit: %
HUMIDITY_MAX = 100.0 # unit: %
POWER_MIN = 0 # unit: W
POWER_MAX = 15000 # unit: W

# Enumeration for evaluation type
class EvaluationType(Enum):
    SINGLE_VALUE = "single"
    ELECTRICITY_SENSOR = "electricity_sensor"


# Get current path of main.py as string
currentPath = str(pathlib.Path(__file__).parent.resolve())

# Setup logging information
setup_logger(current_path=currentPath, log_level=log.DEBUG, log_file_size_mb=10, log_file_numbers=10)

# TODO: Configuration of INFLUX and MQTT in an XML file
''' InfluxDB settings '''
influxHost = 'localhost'
influxPort = 8086
influxDatabase = 'home'

''' InfluxDB interface instance '''
influxDB_interface = InfluxDBInterface(influxHost, influxPort, influxDatabase)

''' MQTT settings '''
BROKER_ADDRESS = "localhost"

'''' List of datasets '''
influxDBDatasets = InfluxDBDatasets()
influxDBDatasets.new_dataset(name="office-temperature", min_value=TEMPERATURE_MIN, max_value=TEMPERATURE_MAX,
                             evaluation_type=EvaluationType.SINGLE_VALUE)
influxDBDatasets.new_dataset(name="office-humidity", min_value=HUMIDITY_MIN, max_value=HUMIDITY_MAX,
                             evaluation_type=EvaluationType.SINGLE_VALUE)
influxDBDatasets.new_dataset(name="outside-temperature", min_value=TEMPERATURE_MIN, max_value=TEMPERATURE_MAX,
                             evaluation_type=EvaluationType.SINGLE_VALUE)
influxDBDatasets.new_dataset(name="outside-humidity", min_value=HUMIDITY_MIN, max_value=HUMIDITY_MAX,
                             evaluation_type=EvaluationType.SINGLE_VALUE)
influxDBDatasets.new_dataset(name="electricmeter-SENSOR", min_value=POWER_MIN, max_value=POWER_MAX,
                             evaluation_type=EvaluationType.ELECTRICITY_SENSOR)
influxDBDatasets.set_name_of_current_datasets()

''' MQTT InfluxDB interface instance '''
mqttInfluxInterface = mqttInfluxInterface(BROKER_ADDRESS, influxDB_interface, influxDBDatasets)


# TODO: Own class or file for this function
def thread_cpu_information_to_influx(time_sleep):
    """
    Get CPU information (CPU usage and processor temperature) and write information to database every <time_sleep>
    seconds
    :param time_sleep: sleeptime until new cycle
    """
    while True:
        log.debug("New cycle")
        # Get CPU information in JSON format
        cpu_information = raspi_cpu_information.getCPUInformation()
        # Write CPU information in database
        influxDB_interface.dictToDatabase(cpu_information)
        # Wait before next cycle
        log.debug("Cycle done, go to sleep...")
        time.sleep(time_sleep)


TASK01_ENABLE = True
TASK02_ENABLE = True


def main(args):
    log.info("Starting main application...")

    ''' TASK 01: MQTT TO INFLUX INTERFACE '''
    if TASK01_ENABLE:
        t1 = threading.Thread(target=mqttInfluxInterface.thread_mqtt_to_influx, args=())
        t1.start()

    ''' TASK 02: CPU INFORMATION TO INFLUX '''
    if TASK02_ENABLE:
        t2 = threading.Thread(target=thread_cpu_information_to_influx(30), args=())
        t2.start()

    if TASK01_ENABLE:
        t1.join()

    if TASK02_ENABLE:
        t2.join()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
