#include <WiFi.h>
#include <WiFiClient.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include <esp_task_wdt.h>
#include "secrets.h"  // Contains WIFI_SSID, WIFI_PASSWORD, MQTT_HOST, THINGNAME, cacert, client_cert, privkey

#define TIME_ZONE -5
#define PIR_PIN 27  // GPIO pin (e.g., 27)

#define MQTT_PUBLISH_TOPIC "esp8266/pub"
#define WDT_TIMEOUT 10  // 10 seconds watchdog timeout

// Motion detection settings
volatile int motionSensitivity = 2;  // 1=Low, 2=Medium, 3=High
volatile unsigned long motionDebounceTime = 2000;  // Default 2 seconds
volatile unsigned long lastMotionTime = 0;

// WiFi client for local Mosquitto
WiFiClient net;
PubSubClient client(net);

// Task handles
TaskHandle_t mqttTaskHandle = NULL;
TaskHandle_t sensorTaskHandle = NULL;

// Shared variables with mutex protection
SemaphoreHandle_t xMutex;
volatile int pirState = LOW;
volatile bool motionDetected = false;
volatile bool mqttConnected = false;

// ========== WiFi Connection ==========
void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }

  Serial.println("\nWiFi connected.");
}


// ========== MQTT Client Setup ==========
void setupMQTTClient() {
  client.setServer(MQTT_HOST, 1883);
  client.setCallback(mqttCallback);
}

// ========== MQTT Callback ==========
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  // Convert payload to string
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  
  // Parse JSON command
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, message);
  
  if (!error) {
    // Handle sensitivity adjustment
    if (doc.containsKey("sensitivity")) {
      int newSensitivity = doc["sensitivity"];
      if (newSensitivity >= 1 && newSensitivity <= 3) {
        xSemaphoreTake(xMutex, portMAX_DELAY);
        motionSensitivity = newSensitivity;
        // Adjust debounce time based on sensitivity
        switch (motionSensitivity) {
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
        xSemaphoreGive(xMutex);
        
        Serial.print("Sensitivity set to: ");
        Serial.println(newSensitivity);
      }
    }
  }
}

// ========== Publish Motion Status ==========
void publishMotionStatus() {
  StaticJsonDocument<200> doc;
  doc["motion"] = 1;
  doc["sensorid"] = SENSORID;
  doc["time"] = millis();
  doc["core"] = xPortGetCoreID();  // Show which core is publishing
  doc["sensitivity"] = motionSensitivity;
  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer);

  if (client.publish(MQTT_PUBLISH_TOPIC, jsonBuffer)) {
    Serial.println("Publish successful.");
  } else {
    Serial.println("Publish failed.");
  }
}

// ========== MQTT Task (runs on Core 0) ==========
void mqttTask(void *pvParameters) {
  const TickType_t xDelay = 100 / portTICK_PERIOD_MS;  // 100ms delay
  unsigned long lastWiFiCheck = 0;
  const unsigned long WIFI_CHECK_INTERVAL = 10000;  // Check WiFi every 10 seconds
  
  // Add this task to watchdog
  esp_task_wdt_add(NULL);
  
  while (true) {
    // Reset watchdog timer
    esp_task_wdt_reset();
    // Check WiFi connection periodically
    unsigned long currentTime = millis();
    if (currentTime - lastWiFiCheck >= WIFI_CHECK_INTERVAL) {
      lastWiFiCheck = currentTime;
      if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi disconnected! Reconnecting...");
        WiFi.disconnect();
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        
        int retries = 0;
        while (WiFi.status() != WL_CONNECTED && retries < 20) {
          Serial.print(".");
          vTaskDelay(500 / portTICK_PERIOD_MS);
          retries++;
        }
        
        if (WiFi.status() == WL_CONNECTED) {
          Serial.println("\nWiFi reconnected!");
          Serial.print("IP address: ");
          Serial.println(WiFi.localIP());
        } else {
          Serial.println("\nWiFi reconnection failed!");
        }
      }
    }
    
    // Only attempt MQTT if WiFi is connected
    if (WiFi.status() == WL_CONNECTED) {
      // Maintain MQTT connection
      if (!client.connected()) {
        Serial.println("Reconnecting to MQTT...");
        if (client.connect(THINGNAME)) {
          Serial.println("MQTT connected!");
          client.subscribe("esp32/sub");
          
          xSemaphoreTake(xMutex, portMAX_DELAY);
          mqttConnected = true;
          xSemaphoreGive(xMutex);
        } else {
          Serial.println("MQTT connection failed.");
          xSemaphoreTake(xMutex, portMAX_DELAY);
          mqttConnected = false;
          xSemaphoreGive(xMutex);
          vTaskDelay(5000 / portTICK_PERIOD_MS);  // Wait 5s before retry
        }
      }
      
      // Process MQTT messages
      if (client.connected()) {
        client.loop();
        
        // Check for motion to publish
        bool shouldPublish = false;
        xSemaphoreTake(xMutex, portMAX_DELAY);
        if (motionDetected) {
          shouldPublish = true;
          motionDetected = false;
        }
        xSemaphoreGive(xMutex);
        
        if (shouldPublish) {
          publishMotionStatus();
        }
      }
    } else {
      // WiFi not connected, mark MQTT as disconnected
      xSemaphoreTake(xMutex, portMAX_DELAY);
      mqttConnected = false;
      xSemaphoreGive(xMutex);
    }
    
    vTaskDelay(xDelay);
  }
}

// ========== Sensor Task (runs on Core 1) ==========
void sensorTask(void *pvParameters) {
  const TickType_t xDelay = 50 / portTICK_PERIOD_MS;  // 50ms delay
  int lastPirState = LOW;
  
  // Add this task to watchdog
  esp_task_wdt_add(NULL);
  
  while (true) {
    // Reset watchdog timer
    esp_task_wdt_reset();
    
    int currentPirState = digitalRead(PIR_PIN);
    unsigned long currentTime = millis();
    
    if (currentPirState == HIGH && lastPirState == LOW) {
      xSemaphoreTake(xMutex, portMAX_DELAY);
      unsigned long timeSinceLastMotion = currentTime - lastMotionTime;
      unsigned long currentDebounceTime = motionDebounceTime;
      xSemaphoreGive(xMutex);
      
      // Check if enough time has passed since last motion
      if (timeSinceLastMotion >= currentDebounceTime) {
        Serial.println("Motion detected!");
        
        xSemaphoreTake(xMutex, portMAX_DELAY);
        motionDetected = true;
        lastMotionTime = currentTime;
        xSemaphoreGive(xMutex);
      }
    }
    
    lastPirState = currentPirState;
    vTaskDelay(xDelay);
  }
}

// ========== Setup ==========
void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
  
  // Initialize watchdog timer with new API
  esp_task_wdt_config_t twdt_config = {
    .timeout_ms = WDT_TIMEOUT * 1000,  // Convert to milliseconds
    .idle_core_mask = 0,  // No idle task monitoring
    .trigger_panic = true
  };
  esp_task_wdt_init(&twdt_config);
  esp_task_wdt_add(NULL);  // Add current task to WDT
  Serial.println("Watchdog timer initialized (10s timeout)");
  
  // Create mutex
  xMutex = xSemaphoreCreateMutex();
  
  connectWiFi();
  setupMQTTClient();
  
  // Create tasks on different cores
  xTaskCreatePinnedToCore(
    mqttTask,         // Task function
    "MQTT_Task",      // Task name
    4096,             // Stack size
    NULL,             // Parameters
    1,                // Priority
    &mqttTaskHandle,  // Task handle
    0                 // Core 0
  );
  
  xTaskCreatePinnedToCore(
    sensorTask,       // Task function
    "Sensor_Task",    // Task name
    2048,             // Stack size
    NULL,             // Parameters
    2,                // Priority (higher than MQTT)
    &sensorTaskHandle,// Task handle
    1                 // Core 1
  );
  
  Serial.println("Multi-threaded tasks started!");
}

// ========== Main Loop ==========
void loop() {
  // Main loop is empty as all work is done in tasks
  esp_task_wdt_reset();  // Keep main task alive
  vTaskDelay(1000 / portTICK_PERIOD_MS);
}