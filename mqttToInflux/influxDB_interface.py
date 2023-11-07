import json

from influxdb import InfluxDBClient
import logging as log

class InfluxDBInterface:

    def __init__(self, host, port, database):
        log.info("Initialize instance of InfluxDBInterface")
        self.host = host
        self.port = port
        self.database = database
        
        ''' InfluxDB settings '''
        self.influxClient = InfluxDBClient(host=self.host, port=self.port)
        log.debug("InfluxDB client: %s", self.influxClient)
        self.influxClient.switch_database(self.database)
        
    def dictToDatabase(self, dictionary):
        keys = list(dictionary.keys())
        values = list(dictionary.values())
        length = len(keys)
        
        for i in range(length):
            checkData = True
            key = keys[i]
            value = values[i]
            
            log.debug("Check data %s: %s", key, value)
            log.info("Write %s - %s to database", key, value)
            jsonBody = self._getJSONBody(key, value)
            self._writeJSONToDatabase(jsonBody)
    
    def _writeJSONToDatabase(self, JSONBody):
        try:
            ret = self.influxClient.write_points(JSONBody)
            log.info("Wrote points successfully")
        except:
            log.info("Error writing point")
            
    def _getJSONBody(self, key, value):
        jsonBody = [
            {
                "measurement": key,
                "fields": {
                    "value": value
                }
            }
        ]
        
        log.info(jsonBody)
        
        return jsonBody
