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

TEMPERATURE_MIN = -30.0
TEMPERATURE_MAX = 80.0
HUMIDITY_MIN = 0.0
HUMIDITY_MAX = 100.0


class EvaluationType(Enum):
    SINGLE_VALUE = "single"
    ELECTRICITY_SENSOR = "electricity_sensor"


# Get current path of main.py as string
currentPath = str(pathlib.Path(__file__).parent.resolve())

# Setup logging information
setup_logger(current_path=currentPath, log_level=log.INFO, log_file_size_mb=10, log_file_numbers=10)

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
# TODO: Define different "evaluation types"
influxDBDatasets = InfluxDBDatasets()
influxDBDatasets.new_dataset(name="office-temperature", min_value=TEMPERATURE_MIN, max_value=TEMPERATURE_MAX,
                             evaluation_type=EvaluationType.SINGLE_VALUE)
influxDBDatasets.new_dataset(name="office-humidity", min_value=HUMIDITY_MIN, max_value=HUMIDITY_MAX,
                             evaluation_type=EvaluationType.SINGLE_VALUE)
influxDBDatasets.new_dataset(name="outside-temperature", min_value=TEMPERATURE_MIN, max_value=TEMPERATURE_MAX,
                             evaluation_type=EvaluationType.SINGLE_VALUE)
influxDBDatasets.new_dataset(name="outside-humidity", min_value=HUMIDITY_MIN, max_value=HUMIDITY_MAX,
                             evaluation_type=EvaluationType.SINGLE_VALUE)
influxDBDatasets.new_dataset(name="electricmeter-SENSOR", min_value=0, max_value=999999,
                             evaluation_type=EvaluationType.ELECTRICITY_SENSOR)
influxDBDatasets.set_name_of_current_datasets()

''' MQTT InfluxDB interface instance '''
mqttInfluxInterface = mqttInfluxInterface(BROKER_ADDRESS, influxDB_interface, influxDBDatasets)


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
    log.info("Starting main application...")

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
