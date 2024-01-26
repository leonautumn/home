#!/usr/bin/python
import json
import logging as log
import paho.mqtt.client as mqtt


class mqttInfluxInterface:

    def __init__(self, broker_address, influxDBInterface, influxDBDatasets):
        self.influxDB_interface = influxDBInterface
        self.broker_address = broker_address
        self.mqttDatasets = influxDBDatasets

    def on_message(self, client, userdata, message):
        # Decode message in utf-8 format
        msg = str(message.payload.decode("utf-8"))
        log.info(msg)

        # Split topic into several elements
        msg_arr = message.topic.split("/")
        log.info(msg_arr)

        # Get topic element 3 and 4, put them together
        #   E. g.: "office/temperature" --> "office-temperature"
        key = msg_arr[3] + '-' + msg_arr[4]
        log.debug(key)

        # Check if received data should be written to InfluxDB
        # TODO: Distinguish between evaluation types by own function(s)
        if key in self.mqttDatasets.datasets_name:
            log.debug("Key " + key + " is part of datasets.")
            dataset = self.mqttDatasets.get_dataset_by_name(key)
            log.info("Get dataset: " + dataset)
            influx_dict = {} # Empty dict

            if not key == "electricmeter-SENSOR":
                # Convert value [payload] into float data type
                val = float(msg)
                if self._checkData(val, dataset): influx_dict.update({key: val})
            else:
                msg = json.loads(msg)

                # TODO: Own dataset for overall consumption
                key = "Eges"
                val = float((msg.get("MT681")).get("Total_in"))
                # Minimum: 10000 kwh
                if val > 10000 and val < 50000: influx_dict.update({key: val})

                key = "Pges"
                val = float((msg.get("MT681")).get("Power_cur"))
                if self._checkData(val, dataset): influx_dict.update({key: val})

                key = "Power_P1"
                val = float((msg.get("MT681")).get("Power_p1"))
                if self._checkData(val, dataset): influx_dict.update({key: val})

                key = "Power_P2"
                val = float((msg.get("MT681")).get("Power_p2"))
                if self._checkData(val, dataset): influx_dict.update({key: val})

                key = "Power_P3"
                val = float((msg.get("MT681")).get("Power_p3"))
                if self._checkData(val, dataset): influx_dict.update({key: val})

            # Write dict to database
            log.info(influx_dict)
            if (len(influx_dict) > 0):
                self.influxDB_interface.dictToDatabase(influx_dict)
        else:
            log.debug("Key " + key + " is not part of datasets.")

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

    def _checkData(self, value, dataset):
        # Returns True if data check is ok, otherwise False

        log.info("Check input data before writing to influxDB")
        min_val = json.loads(dataset).get("min value")
        log.debug("Min val: " + str(min_val))
        max_val = json.loads(dataset).get("max value")
        log.debug("Max val: " + str(max_val))

        if value < min_val:
            log.info("Value " + str(value) + " is smaller than min value " + str(min_val))
            return False

        if value > max_val:
            log.info("Value " + str(value) + " is greater than min value " + str(max_val))
            return False

        log.info("Check data OK.")
        return True


class InfluxDBDatasets:

    def __init__(self):
        log.info("Init mqttDataset")
        self.datasets = []
        self.datasets_name = []

    def new_dataset(self, name, min_value, max_value, evaluation_type):
        # Create dict from the data
        dataset = {
            "name": name,
            "min value": min_value,
            "max value": max_value,
            "evaluation type": str(evaluation_type)
        }

        # Convert dict to json object
        dataset_json = json.dumps(dataset)
        log.info("Created dataset: " + dataset_json)

        # Append object to list of objects
        self.datasets.append(dataset_json)

    def set_name_of_current_datasets(self):
        # Empty list of current dataset names
        self.datasets_name = []

        # Go through all datasets
        for dataset in self.datasets:
            log.debug(dataset)

            # Convert list element to json object
            json_data = json.loads(dataset)

            # Get "name" from json object
            dataset_name = json_data.get("name")
            log.debug(dataset_name)

            # Append name to lust of current dataset names
            self.datasets_name.append(dataset_name)

        log.info(self.datasets_name)

    def get_dataset_by_name(self, name):
        # Get dataset by name
        log.debug("Get dataset " + name)
        for dataset in self.datasets:
            log.debug(dataset)
            log.debug(json.loads(dataset).get("name"))
            if json.loads(dataset).get("name") == name:
                return dataset
