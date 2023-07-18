#include <Wire.h>
#include <ESP8266WiFi.h>
#include <Pinger.h>
#include <PubSubClient.h>

// Sensor libraries
#include <OneWire.h>
#include <DallasTemperature.h>

/* General definitions */
unsigned long delayTime = 30000;                // Delay time until new cycle starts

/* Wifi definitions */
const char* WIFI_SSID = "WIFI_SSID";    // Wifi WIFI_SSID
const char* WIFI_PSK = "WIFI_PSK";  // Wifi password
WiFiClient espClient;                           // Wifi client instance

/* MQTT definitions */
const char* MQTT_BROKER = "192.168.178.36";     // MQTT IP address
int MQTT_PORT = 1883;                           // MQTT port
PubSubClient client(espClient);                 // MQTT client instance
String mqttTopicRoom = "/home/data/outside/";   // MQTT topic (first part)

/* Ping definitions */
Pinger pinger;                                  // Object to ping devices

/* Sensor definitions */
const int oneWireBus = 4;                       // GPIO where the DS18B20 is connected to
OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);


void setup() {
  Serial.begin(9600);

  bool status;

  /* Set up WiFi connection */
  wifi_setup();
  
  /* MQTT initialization */
  client.setServer(MQTT_BROKER, MQTT_PORT);

  /* Sensor initialization */
  sensors.begin();

  Serial.println();
}

void wifi_setup() {
  
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);

  /* Connect to WiFi network */
  WiFi.begin(WIFI_SSID, WIFI_PSK);

  /* Try to connect until connection is established */
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  /* Print out WiFi information */
  Serial.println("");
  Serial.println("    WiFi connected");
  Serial.print("    IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println();
}

void mqtt_reconnect() {
  
  /* Try to ping MQTT broker */
  Serial.print("Try to ping 192.168.178.36...");
  IPAddress ip (192, 168, 178, 36);
  bool ret = pinger.Ping(ip);
  Serial.println(ret);
  
  /* Try to connect to the MQTT broker */
  WiFi.mode(WIFI_STA);
  while (!client.connected()) {
    Serial.println("Reconnecting...");

    /* Set a random client ID */
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);

    /* Try to connect until connection is established */
    if (!client.connect(clientId.c_str())) {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

void loop() {
  Serial.println("Start new cycle...");
  
  /* Connect to MQTT broker */
  if (!client.connected()) {
    mqtt_reconnect();
  } else {
    Serial.println("Client is connected to MQTT broker");
  }
  client.loop();

  // Get sensor values and send to MQTT broker
  Serial.println("Get sensor values and send to MQTT broker");
  getAndSendValues();

  Serial.println();
  delay(delayTime);
}

void getAndSendValues() {
  
  String mqttPubTopicStr;
  int retVal;

  /* TEMPERATURE */
  // Get value
  sensors.requestTemperatures(); 
  float temperature_degree = sensors.getTempCByIndex(0);  
  Serial.print("Temperature: ");
  Serial.print(String(temperature_degree,2));
  Serial.println(" °C");

  // Write to MQTT broker
  mqttPubTopicStr = mqttTopicRoom + "temperature";
  retVal = publishFloatValueToMqttBroker(mqttPubTopicStr, temperature_degree);

  return;
}

int publishFloatValueToMqttBroker(String topic, float value) {
  /* Return value
   *   1 = Publishing succesful
   *  -1 = Publishing not succesful
   */
  int  ret = 0;
  bool publishReturn;
  
  /* Topic and payload definitions */
  char mqttPubTopic[50];
  String mqttPubPayloadStr;
  char mqttPubPayload[50];
  
  /* Set topic as char array */
  topic.toCharArray(mqttPubTopic, topic.length() + 1);
  Serial.print(mqttPubTopic);
  Serial.print(" - ");

  /* Set payload as char array */
  mqttPubPayloadStr = String(value, 2); // Convert float to string with two decimals
  mqttPubPayloadStr.toCharArray(mqttPubPayload, mqttPubPayloadStr.length() + 1);
  Serial.println(mqttPubPayload);
  
  /* Publish message to broker */
  publishReturn = client.publish(mqttPubTopic, mqttPubPayload);

  if (publishReturn) {
    Serial.println("Pusblish was succesful");
    ret = 1;
  } else {
    Serial.println("Error publishing message");
    ret = client.state();
  }
  return ret;
}
