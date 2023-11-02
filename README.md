# home

Idea: Small weather station which records data from inside and outside.

In the source folder <b>sensors</b>, code files for ESP8266 with weather sensors (e. g. BME280 or DS18B20) are stored. The ESP8266 send data via MQTT protocol (via WiFi) to a RaspberryPi. The RasPi handle the incoming MQTT data and put them into an influx database (source folder <b>mqttToInflux</b>).
Additionally, CPU stats of the RasPi are written to the database.

All the data can be visualized via Grafana.
