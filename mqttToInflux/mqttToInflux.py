#!/usr/bin/python

import logging as log
import paho.mqtt.client as mqtt



class mqttInfluxInterface:

    def __init__(self, broker_address, influxDbInterface):
        self.influxDB_interface = influxDbInterface
        self.broker_address = broker_address

    def on_message(self, client, userdata, message):
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
        self.influxDB_interface.dictToDatabase(influx_dict)


    def on_connect(self, client, userdata, flags, rc):
        # Subscribe to topic
        client.subscribe('/home/data/#')

    def thread_mqtt_to_influx(self):
        log.debug("Thread MQTT to influx")
        while True:
            client = mqtt.Client()
            # Define callbacks for connect and message
            client.on_connect = self.on_connect
            client.on_message = self.on_message

            # Connect to MQTT broker
            #   TODO: Evaluate return of connect function
            client.connect(self.broker_address)

            print("Connected to MQTT Broker: " + self.broker_address)
            client.loop_forever()