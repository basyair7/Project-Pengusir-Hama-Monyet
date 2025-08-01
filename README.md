# ESP8266/ESP32 Motion Detection System with MQTT

## Overview

This project implements a sophisticated motion detection system using ESP8266 and ESP32 microcontrollers with PIR sensors. The system features real-time motion detection, MQTT communication, multi-threading capabilities, automatic recovery mechanisms, and remote configuration options.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Features](#features)
3. [Hardware Requirements](#hardware-requirements)
4. [Software Components](#software-components)
5. [Multi-Threading Implementation](#multi-threading-implementation)
6. [MQTT Communication](#mqtt-communication)
7. [Motion Detection System](#motion-detection-system)
8. [Reliability Features](#reliability-features)
9. [Configuration and Usage](#configuration-and-usage)
10. [Performance Optimizations](#performance-optimizations)

## System Architecture

The system consists of two main implementations:
- **ESP8266**: Single-core microcontroller using Ticker library for cooperative multitasking
- **ESP32**: Dual-core microcontroller utilizing FreeRTOS and both cores for parallel processing

### Platform Differences

| Feature | ESP8266 | ESP32 |
|---------|---------|-------|
| Architecture | Single-core (80/160MHz) | Dual-core (240MHz) |
| Multitasking | Ticker-based cooperative | FreeRTOS preemptive |
| RAM | 80KB | 320KB |
| Flash | 512KB-16MB | 4MB-16MB |
| Threading | Cooperative functions | True multithreading |
| Watchdog | Hardware WDT | Task-based WDT |
| Task Sync | Global variables | Mutex/semaphores |

### Core Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   PIR Sensor    │────▶│  Microcontroller│────▶│  MQTT Broker    │
│                 │     │  (ESP8266/32)   │     │  (Mosquitto)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   WiFi Network  │
                        └─────────────────┘
```

## Features

### 1. Real-Time Motion Detection
- **Response Time**: 50ms sensor polling interval
- **Debounce Logic**: Prevents false triggers
- **Adjustable Sensitivity**: 3 levels (Low/Medium/High)

### 2. Multi-Threading Support
- **Concurrent Tasks**: MQTT and sensor monitoring run independently
- **Priority-Based Scheduling**: Sensor task has higher priority
- **Non-Blocking Operation**: No delays in main processing

### 3. Network Resilience
- **Auto WiFi Reconnection**: Checks every 10 seconds
- **MQTT Auto-Recovery**: Maintains persistent connection
- **Offline Buffering**: Queues events during disconnection

### 4. System Reliability
- **Watchdog Timer**: 10-second timeout prevents freezes
- **Automatic Restart**: Recovery from system failures
- **Thread-Safe Operations**: Mutex/semaphore protection

### 5. Remote Configuration
- **MQTT Commands**: Adjust settings via JSON messages
- **Real-Time Updates**: Immediate response to configuration changes
- **Status Reporting**: Current settings included in motion events

## Hardware Requirements

### ESP8266 Setup
```
ESP8266 Pin     Component
-----------     ---------
D7              PIR Sensor Signal
3.3V            PIR Sensor VCC
GND             PIR Sensor GND
```

### ESP32 Setup
```
ESP32 Pin       Component
---------       ---------
GPIO 27         PIR Sensor Signal
3.3V            PIR Sensor VCC
GND             PIR Sensor GND
```

## Software Components

### 1. secrets.h Configuration
Create a `secrets.h` file with your network credentials:
```cpp
#define WIFI_SSID "your_wifi_ssid"
#define WIFI_PASSWORD "your_wifi_password"
#define MQTT_HOST "your_mqtt_broker_ip"
#define THINGNAME "your_device_name"
```

### 2. Library Dependencies

**Common Libraries**:
- PubSubClient (MQTT communication)
- ArduinoJson (JSON parsing/serialization)

**ESP8266 Specific**:
- ESP8266WiFi (WiFi connectivity)
- Ticker (cooperative multitasking)

**ESP32 Specific**:
- WiFi (WiFi connectivity)
- esp_task_wdt (watchdog timer)
- FreeRTOS (built-in multitasking)

## Multi-Threading Implementation

### ESP8266 (Ticker-based Cooperative)
```cpp
// Ticker objects for periodic function calls
Ticker mqttTicker;
Ticker sensorTicker;
Ticker wifiCheckTicker;

// Setup periodic tasks
mqttTicker.attach(0.1, mqttTask);        // 100ms intervals
sensorTicker.attach(0.05, sensorTask);   // 50ms intervals
wifiCheckTicker.attach(10.0, checkWiFi); // 10 second intervals
```

**Cooperative Scheduling**:
- Functions called periodically by hardware timers
- Non-blocking execution with yield() calls
- Shared variables without mutex (single-threaded)
- Main loop handles background WiFi tasks

### ESP32 (Dual Core)
```cpp
// Tasks pinned to specific cores
xTaskCreatePinnedToCore(mqttTask, "MQTT_Task", 4096, NULL, 1, &mqttTaskHandle, 0);
xTaskCreatePinnedToCore(sensorTask, "Sensor_Task", 2048, NULL, 2, &sensorTaskHandle, 1);
```

**Core Assignment**:
- Core 0: MQTT communication and WiFi management
- Core 1: Sensor monitoring and motion detection
- True parallel execution

## MQTT Communication

### Published Topics
- **Motion Events**: `esp8266/pub`
  ```json
  {
    "motion": 1,
    "time": 1234567890,
    "sensitivity": 2,
    "core": 0  // ESP32 only
  }
  ```

### Subscribed Topics
- **Configuration**: `esp8266/sub` or `esp32/sub`
  ```json
  {
    "sensitivity": 3  // 1=Low, 2=Medium, 3=High
  }
  ```

### Connection Management
1. **Initial Connection**: Attempts connection on startup
2. **Keep-Alive**: Maintains persistent connection
3. **Auto-Reconnect**: Retries every 5 seconds on failure
4. **Message Queue**: Processes incoming messages in callback

## Motion Detection System

### Sensitivity Levels

| Level | Value | Debounce Time | Use Case |
|-------|-------|---------------|----------|
| Low | 1 | 5000ms | Minimize false triggers |
| Medium | 2 | 2000ms | Balanced detection |
| High | 3 | 500ms | Maximum responsiveness |

### Detection Algorithm
```cpp
1. Read PIR sensor state every 50ms
2. Check for LOW → HIGH transition
3. Verify debounce time has elapsed
4. Set motion flag for MQTT task
5. Publish motion event
```

### Thread Synchronization

**ESP8266 (Cooperative)**:
- **Shared Variables**: Direct access (single-threaded)
- **Motion Flag**: Set by sensor function, cleared by MQTT function
- **No Race Conditions**: Sequential execution guaranteed

**ESP32 (Preemptive)**:
- **Shared Variables**: Protected by semaphores/mutex
- **Motion Flag**: Set by sensor task, cleared by MQTT task
- **Atomic Operations**: Prevents race conditions

## Reliability Features

### 1. Watchdog Timer

**ESP8266 Implementation**:
```cpp
// Hardware watchdog (simpler)
ESP.wdtEnable(8000);  // 8 second timeout
ESP.wdtFeed();        // Feed in loop and functions
```

**ESP32 Implementation**:
```cpp
// Task watchdog (more sophisticated)
esp_task_wdt_config_t twdt_config = {
  .timeout_ms = WDT_TIMEOUT * 1000,
  .idle_core_mask = 0,
  .trigger_panic = true
};
esp_task_wdt_init(&twdt_config);
esp_task_wdt_add(NULL);
```

**Operation**:

**ESP8266**:
- Hardware watchdog must be fed in main loop
- Simple timeout-based restart mechanism
- Less granular than ESP32 implementation

**ESP32**:
- Each task must feed the watchdog regularly
- Task-specific monitoring capabilities
- More sophisticated failure detection

### 2. WiFi Recovery
```cpp
if (WiFi.status() != WL_CONNECTED) {
    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    // Retry logic with timeout
}
```

**Features**:
- Periodic connection checks (10s intervals)
- Automatic reconnection attempts
- MQTT operations suspended during disconnection

### 3. Error Handling
- Connection failure logging
- Graceful degradation
- State preservation across restarts

## Configuration and Usage

### 1. Initial Setup
1. Flash the appropriate code to your device
2. Configure WiFi and MQTT credentials in `secrets.h`
3. Connect PIR sensor to designated pins
4. Power on the device

### 2. MQTT Broker Setup
```bash
# Install Mosquitto
sudo apt install mosquitto mosquitto-clients

# Test subscription
mosquitto_sub -t "esp8266/pub" -v

# Send configuration
mosquitto_pub -t "esp8266/sub" -m '{"sensitivity":3}'
```

### 3. Remote Control
```python
# Python example for sensitivity adjustment
import paho.mqtt.client as mqtt
import json

client = mqtt.Client()
client.connect("mqtt_broker_ip", 1883)

# Set high sensitivity
config = {"sensitivity": 3}
client.publish("esp8266/sub", json.dumps(config))
```

## Performance Optimizations

### 1. Task Timing

**ESP8266 (Ticker-based)**:
- **MQTT Function**: 100ms (10Hz) - Balances responsiveness and CPU usage
- **Sensor Function**: 50ms (20Hz) - Fast motion detection
- **WiFi Check**: 10s - Reduces overhead
- **Main Loop**: 10ms delay with yield() calls

**ESP32 (FreeRTOS)**:
- **MQTT Task**: 100ms intervals with vTaskDelay()
- **Sensor Task**: 50ms intervals with vTaskDelay()
- **WiFi Check**: Integrated into MQTT task
- **Main Loop**: 1s delay (tasks handle everything)

### 2. Memory Management

**ESP8266**:
- **No Task Stacks**: Functions called from main context
- **Global Variables**: Shared between Ticker functions
- **Heap Usage**: Lower overhead without FreeRTOS
- **JSON Buffers**: 512 bytes fixed size

**ESP32**:
- **Task Stacks**: 2-4KB per task
- **Mutex Objects**: Additional memory for synchronization
- **Heap Usage**: Higher overhead with FreeRTOS
- **JSON Buffers**: 512 bytes fixed size

### 3. Power Efficiency
- **Task Delays**: Allow CPU idle time
- **WiFi Sleep**: Possible between checks
- **Sensor Power**: Can be controlled via GPIO

### 4. Network Optimization
- **Persistent MQTT**: Reduces connection overhead
- **Local Broker**: Minimizes latency
- **Compact JSON**: Reduces bandwidth usage

## Troubleshooting

### Common Issues

1. **Watchdog Resets**
   
   **ESP8266**:
   - Ensure ESP.wdtFeed() is called in main loop
   - Add yield() calls in long-running functions
   - Check for blocking operations in Ticker functions
   
   **ESP32**:
   - Check task delays are present (vTaskDelay)
   - Verify esp_task_wdt_reset() is called regularly
   - Monitor serial output for freeze location

2. **WiFi Connection Failures**
   - Verify credentials in secrets.h
   - Check router settings (2.4GHz for ESP8266)
   - Monitor signal strength

3. **MQTT Connection Issues**
   - Verify broker is running
   - Check firewall settings
   - Ensure unique client names

4. **False Motion Triggers**
   - Adjust sensitivity level
   - Check PIR sensor placement
   - Verify power supply stability

### Debug Output
Monitor serial output (115200 baud) for:
- Connection status
- Motion events
- Configuration changes
- Error messages

## Future Enhancements

1. **Additional Sensors**: Temperature, humidity, light
2. **Data Logging**: SD card or cloud storage
3. **Web Interface**: Configuration dashboard
4. **OTA Updates**: Remote firmware updates
5. **Battery Operation**: Deep sleep modes
6. **Multiple Zones**: Array of PIR sensors
7. **AI Integration**: Pattern recognition
8. **Encryption**: Secure MQTT with TLS/SSL

## Conclusion

This motion detection system provides a robust, scalable solution for IoT applications. The multi-threaded architecture ensures responsive performance, while the reliability features guarantee continuous operation. The flexible configuration options make it suitable for various deployment scenarios, from home security to industrial monitoring.