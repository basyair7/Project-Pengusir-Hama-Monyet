# ESP8266 vs ESP32 Implementation Differences

## Why Different Implementations?

While both boards run similar code, there are architectural differences that require platform-specific implementations:

### 1. Watchdog Timer Implementation

**ESP8266:**
```cpp
// Simple hardware watchdog
ESP.wdtEnable(8000);  // 8 second timeout
ESP.wdtFeed();        // Feed the watchdog
```

**ESP32:**
```cpp
// Task-based watchdog with per-task monitoring
esp_task_wdt_init(WDT_TIMEOUT, true);
esp_task_wdt_add(NULL);    // Add task to watchdog
esp_task_wdt_reset();      // Reset watchdog for this task
```

**Reason**: ESP32's watchdog is more sophisticated, allowing individual task monitoring. ESP8266 has a simpler global watchdog.

### 2. Task Creation

**ESP8266:**
```cpp
// Single core - tasks share CPU time
xTaskCreate(mqttTask, "MQTT_Task", 2048, NULL, 1, &mqttTaskHandle);
```

**ESP32:**
```cpp
// Dual core - tasks can run on specific cores
xTaskCreatePinnedToCore(mqttTask, "MQTT_Task", 4096, NULL, 1, &mqttTaskHandle, 0);
```

**Reason**: ESP32 has 2 cores, allowing true parallel execution. ESP8266 has 1 core with time-slicing.

### 3. Memory Allocation

**ESP8266:**
- Smaller stack sizes (1024-2048 bytes)
- Limited RAM (~80KB usable)

**ESP32:**
- Larger stack sizes (2048-4096 bytes)
- More RAM (~320KB usable)

**Reason**: ESP32 has significantly more memory available.

### 4. WiFi Library Differences

**ESP8266:**
```cpp
#include <ESP8266WiFi.h>
WiFi.mode(WIFI_STA);
yield();  // Needed for background tasks
```

**ESP32:**
```cpp
#include <WiFi.h>
WiFi.mode(WIFI_STA);
// No yield() needed
```

**Reason**: Different WiFi stack implementations. ESP8266 requires explicit yielding.

### 5. GPIO Pin Naming

**ESP8266:**
```cpp
#define PIR_PIN D7  // NodeMCU pin naming
```

**ESP32:**
```cpp
#define PIR_PIN 27  // Direct GPIO number
```

**Reason**: ESP8266 boards often use D-prefixed pin names, ESP32 uses GPIO numbers directly.

## Similarities Maintained

Despite hardware differences, we maintain consistency in:

1. **FreeRTOS Usage**: Both use FreeRTOS for multitasking
2. **MQTT Protocol**: Same message format and topics
3. **Motion Detection Logic**: Identical sensitivity and debounce algorithms
4. **WiFi Reconnection**: Same 10-second check interval
5. **Thread Synchronization**: Both use mutex for shared data protection
6. **Configuration Protocol**: Same JSON command structure

## Performance Characteristics

### ESP8266
- **Pros**: Lower power consumption, cheaper
- **Cons**: Single core limits true parallelism
- **Best for**: Simple deployments, battery-powered devices

### ESP32
- **Pros**: Dual-core performance, more memory, better peripherals
- **Cons**: Higher power consumption, more expensive
- **Best for**: Complex applications, multiple sensors

## Compilation Notes

### ESP8266
- Board: NodeMCU 1.0 (ESP-12E Module)
- CPU Frequency: 80 MHz or 160 MHz
- Flash Size: 4MB (FS:2MB OTA:~1019KB)

### ESP32
- Board: ESP32 Dev Module
- CPU Frequency: 240 MHz (WiFi/BT)
- Flash Size: 4MB
- Partition Scheme: Default 4MB with spiffs

## Future Convergence Opportunities

1. **Unified Watchdog Wrapper**: Create abstraction layer for watchdog functions
2. **Conditional Compilation**: Use #ifdef to handle platform differences
3. **Common Configuration**: Shared header file for both platforms
4. **OTA Updates**: Implement unified OTA system for both boards