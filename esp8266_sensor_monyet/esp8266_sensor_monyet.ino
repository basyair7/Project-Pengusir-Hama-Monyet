#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include <Ticker.h>
#include "secrets.h"  // Contains WIFI_SSID, WIFI_PASSWORD, MQTT_HOST, THINGNAME, certificates

// Time Zone offset (in hours)
#define TIME_ZONE -5

// PIR sensor pin
#define PIR_PIN D7

// MQTT Publish Topic
#define MQTT_PUBLISH_TOPIC "esp8266/pub"
#define WDT_TIMEOUT 8  // 8 seconds watchdog timeout

// Motion detection settings
volatile int motionSensitivity = 2;  // 1=Low, 2=Medium, 3=High
volatile unsigned long motionDebounceTime = 2000;  // Default 2 seconds
volatile unsigned long lastMotionTime = 0;

// WiFi client for local Mosquitto
WiFiClient net;
PubSubClient client(net);

// Ticker objects for non-blocking tasks
Ticker mqttTicker;
Ticker sensorTicker;
Ticker wifiCheckTicker;

// Shared variables (no mutex needed in single-threaded ESP8266)
volatile int pirState = LOW;
volatile bool motionDetected = false;
volatile bool mqttConnected = false;
volatile bool shouldCheckWiFi = false;

// ========== WiFi Connection ==========
void connectWiFi()
{
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(500);
    yield();  // Allow background processing
  }

  Serial.println("\nWiFi connected.");
}


// ========== MQTT Client Setup ==========
void setupMQTTClient()
{
  client.setServer(MQTT_HOST, 1883);
  client.setCallback(mqttCallback);
}

// ========== MQTT Callback ==========
void mqttCallback(char* topic, byte* payload, unsigned int length)
{
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  // Convert payload to string
  String message = "";
  for (int i = 0; i < length; i++)
  {
    message += (char)payload[i];
  }
  Serial.println(message);
  
  // Parse JSON command
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, message);
  
  if (!error)
  {
    // Handle sensitivity adjustment
    if (doc.containsKey("sensitivity"))
    {
      int newSensitivity = doc["sensitivity"];
      if (newSensitivity >= 1 && newSensitivity <= 3)
      {
        motionSensitivity = newSensitivity;
        // Adjust debounce time based on sensitivity
        switch (motionSensitivity)
        {
          case 1:  // Low sensitivity
            motionDebounceTime = 5000;  // 5 seconds
            break;
          case 2:  // Medium sensitivity
            motionDebounceTime = 2000;  // 2 seconds
            break;
          case 3:  // High sensitivity
            motionDebounceTime = 500;   // 0.5 seconds
            break;
        }
        
        Serial.print("Sensitivity set to: ");
        Serial.println(newSensitivity);
      }
    }
  }
}

// ========== Publish Motion Status ==========
void publishMotionStatus()
{
  StaticJsonDocument<200> doc;
  doc["motion"] = 1;
  doc["sensorid"] = SENSORID;
  doc["time"] = millis();
  doc["sensitivity"] = motionSensitivity;
  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer);

  if (client.publish(MQTT_PUBLISH_TOPIC, jsonBuffer))
  {
    Serial.println("Publish successful.");
  }
  else
  {
    Serial.println("Publish failed.");
  }
}

// ========== WiFi Check Function ==========
void checkWiFi()
{
  shouldCheckWiFi = true;
}

// ========== MQTT Task Function ==========
void mqttTask()
{
  // Handle WiFi check if needed
  if (shouldCheckWiFi)
  {
    shouldCheckWiFi = false;
    if (WiFi.status() != WL_CONNECTED)
    {
      Serial.println("WiFi disconnected! Reconnecting...");
      WiFi.disconnect();
      WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
      
      // Non-blocking WiFi connection attempt
      int retries = 0;
      while (WiFi.status() != WL_CONNECTED && retries < 10)
      {
        Serial.print(".");
        delay(200);
        retries++;
        yield(); // Allow ESP8266 background tasks
      }
      
      if (WiFi.status() == WL_CONNECTED)
      {
        Serial.println("\nWiFi reconnected!");
      }
      else
      {
        Serial.println("\nWiFi reconnection failed!");
      }
    }
  }
  
  // Only attempt MQTT if WiFi is connected
  if (WiFi.status() == WL_CONNECTED)
  {
    // Maintain MQTT connection
    if (!client.connected())
    {
      Serial.println("Reconnecting to MQTT...");
      if (client.connect(THINGNAME))
      {
        Serial.println("MQTT connected!");
        client.subscribe("esp8266/sub");
        mqttConnected = true;
      }
      else
      {
        Serial.println("MQTT connection failed.");
        mqttConnected = false;
      }
    }
    
    // Process MQTT messages
    if (client.connected())
    {
      client.loop();
      
      // Check for motion to publish
      if (motionDetected)
      {
        motionDetected = false;
        publishMotionStatus();
      }
    }
  }
  else
  {
    // WiFi not connected, mark MQTT as disconnected
    mqttConnected = false;
  }
}

// ========== Sensor Task Function ==========
void sensorTask()
{
  static int lastPirState = LOW;
  
  int currentPirState = digitalRead(PIR_PIN);
  unsigned long currentTime = millis();
  
  if (currentPirState == HIGH && lastPirState == LOW)
  {
    unsigned long timeSinceLastMotion = currentTime - lastMotionTime;
    
    // Check if enough time has passed since last motion
    if (timeSinceLastMotion >= motionDebounceTime)
    {
      Serial.println("Motion detected!");
      motionDetected = true;
      lastMotionTime = currentTime;
    }
  }
  
  lastPirState = currentPirState;
}

// ========== Setup ==========
void setup()
{
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
  
  // Enable hardware watchdog with 8 second timeout
  ESP.wdtEnable(8000);
  Serial.println("Hardware watchdog enabled (8s timeout)");
  
  connectWiFi();
  setupMQTTClient();
  
  // Start periodic tasks using Ticker
  mqttTicker.attach(0.1, mqttTask);        // Run MQTT task every 100ms
  sensorTicker.attach(0.05, sensorTask);   // Run sensor task every 50ms
  wifiCheckTicker.attach(10.0, checkWiFi); // Check WiFi every 10 seconds
  
  Serial.println("Ticker-based tasks started!");
}

// ========== Main Loop ==========
void loop()
{
  // Feed watchdog in main loop
  ESP.wdtFeed();
  
  // Allow ESP8266 background tasks (WiFi, etc.)
  yield();
  
  // Small delay to prevent tight loop
  delay(10);
}