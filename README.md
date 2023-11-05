# home

Idea: Small weather station which records data from inside and outside.

In the source folder <b>sensors</b>, code files for ESP8266 with weather sensors (e. g. BME280 or DS18B20) are stored. The ESP8266 send data via MQTT protocol (via WiFi) to a RaspberryPi. The RasPi handle the incoming MQTT data and put them into an influx database (source folder <b>mqttToInflux</b>).
Additionally, CPU stats of the RasPi are written to the database.

All the data can be visualized via Grafana.

<b>Example: Visualizing outside temperature</b>
![Screenshot_1](https://user-images.githubusercontent.com/64750042/280531911-fe6e3896-bf20-4ba2-893f-f5cd7d8f77eb.png)

<b>Example: Visualizing power usage</b>
![Screenshot_2](https://user-images.githubusercontent.com/64750042/280531923-a5fd93df-c5dd-49c6-ad1f-03fe3b4f8495.png)
