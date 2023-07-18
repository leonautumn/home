#!/usr/bin/python

import sys, pathlib
import logging as log
import paho.mqtt.client as mqtt
import logging.handlers as log_handler
from influxDB_interface import InfluxDBInterface

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

''' InfluxDB settings '''
influxHost = 'localhost'
influxPort = 8086
influxDatabase = 'home'

''' InfluxDB interface instance '''
influxDB_interface = InfluxDBInterface(influxHost, influxPort, influxDatabase)

''' MQTT settings '''
BROKER_ADDRESS = "localhost"


def on_message(client, userdata, message):
    # Decode message in utf-8 format
    msg = str(message.payload.decode("utf-8"))

    # Convert value [payload] into float data type
    val = float(msg)

    # Split topic into several elements
    msg_arr = message.topic.split("/")
    log.info(msg_arr)

    # Get topic element 3 and 4, put them together
    #   E. g.: "office/temperature" --> "office-temperature"
    key = msg_arr[3] + '-' + msg_arr[4]
    log.info(key)

    # Safe topic and payload into dictionary
    influx_dict = {key: val}
    log.info(influx_dict)

    # Write dict to database
    influxDB_interface.dictToDatabase(influx_dict)


def on_connect(client, userdata, flags, rc):
    # Subscribe to topic
    client.subscribe('/home/data/#')


def main(args):
    log.info("Start application")
    while True:
        client = mqtt.Client()

        # Define callbacks for connect and message
        client.on_connect = on_connect
        client.on_message = on_message

        # Connect to MQTT broker
        #   TODO: Evaluate return of connect function
        client.connect(BROKER_ADDRESS)

        print("Connected to MQTT Broker: " + BROKER_ADDRESS)
        client.loop_forever()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
