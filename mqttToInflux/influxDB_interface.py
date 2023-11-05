from influxdb import InfluxDBClient
import logging as log

TEMPERATURE_MIN = -30.0
TEMPERATURE_MAX = 80.0
HUMIDITY_MIN = 0.0
HUMIDITY_MAX = 100.0

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
            checkData = self._checkData(key, value)
            
            if checkData:
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
    
    def _checkData(self, key, value):
        # Returns True if data check is ok, otherwise false
        # humidity must be between 0 [%] and 100 [%]
        # temperature must be between -30 [°] and 80 [°]
        log.debug("Check input data before writing to influxDB")
        
        if("temperature" in key):
            log.debug("Check temperature")
            if(value < TEMPERATURE_MIN):
                log.debug("Check data failed: Temperature is lower than %s", TEMPERATURE_MIN)
                return False
            
            if(value > TEMPERATURE_MAX):
                log.debug("Check data failed: Temperature is higher than %s", TEMPERATURE_MAX)
                return False
        
        if("humidity" in key):
            log.debug("Check humidity")
            if(value < HUMIDITY_MIN):
                log.debug("Check data failed: Temperature is lower than %s", HUMIDITY_MIN)
                return False
            
            if(value > HUMIDITY_MAX):
                log.debug("Check data failed: Temperature is higher than %s", HUMIDITY_MAX)        
                return False
            
        log.debug("Check data OK.")
        return True
