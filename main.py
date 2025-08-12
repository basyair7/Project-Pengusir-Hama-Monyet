import asyncio
import os
import threading
import time
import pygame
import json
import paho.mqtt.client as mqtt
from bot.telegram import TelegramBot
from utility.sound_control import sound_control

# Mosquitto MQTT Config
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
CLIENT_ID = "raspberry_monyet"
TOPIC = "esp8266/pub"

# Try to initialize pygame.mixer with retries
def init_audio_with_retry(retries=5, delay=5):
    for i in range(retries):
        try:
            pygame.mixer.init()
            print("🔊 Audio initialized successfully")
            return True
        except pygame.error as e:
            print(f"⚠️ Audio init failed (attempt {i+1}/{retries}): {e}")
            time.sleep(delay)
    print("❌ Audio init failed after all retries")
    return False

audio_ready = init_audio_with_retry()

# Telegram Bot
bot = TelegramBot()

# Sound control instance
sound_ctrl = sound_control()

# Play sound one time
def play_sound_once():
    # Check if audio is ready
    if not audio_ready:
        print("🔇 Skipping sound playback, audio device not ready")
        return
    
    # Check if sound is enabled
    if not sound_ctrl.is_sound_enabled():
        print("🔇 Sound is disabled, skipping playback")
        return

    try:
        # Check for various alarm file formats
        alarm_files = ["alarm/alarm.wav", "alarm/alarm.mp3", "alarm/alarm.ogg", "alarm/alarm.flac"]
        sound_file = "example.mp3"  # Default fallback
        
        # Find the first existing sound file
        for file in alarm_files:
            if os.path.exists(file):
                sound_file = file
                break
        
        # Load and play the sound
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play() # Play once
        print("🔊 Alarm playing once")
        # Wait for the sound to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        print("🔇 Alarm finished")
    except Exception as e:
        print(f"⚠️ Error playing sound: {e}")

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker!")
        client.subscribe(TOPIC)
        print(f"📡 Subscribed to topic '{TOPIC}'")
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"📩 Received MQTT message from '{msg.topic}': {message}")

    # threading.Thread(target=play_sound_once, daemon=True).start()
    # asyncio.run(bot.send_message("🐒 MQTT message received", sensor_active=True))
    
    try:
        data = json.loads(message)
        motion = data.get("motion")
        sensor_id = data.get("sensorid")
        timestamp = data.get("time")
        core = data.get("core")
        sensitivity = data.get("sensitivity")
        
        print(f"📊 Parsed data - Motion: {motion}, Sensor ID: {sensor_id}, Time: {timestamp}, Core: {core}, Sensitivity: {sensitivity}")
        
        if (motion):
            play_sound_once()
            asyncio.run(bot.send_message(f"🐒 Motion detected by sensor {sensor_id} at {timestamp}", sensor_active=sensor_id))
        
    except json.JSONDecodeError:
        print("⚠️ Invalid JSON received, ignoring message")

# MQTT Client Setup
client = mqtt.Client(CLIENT_ID)
client.on_connect = on_connect # Set connect callback
client.on_message = on_message # Set message callback

# Async main
async def main():
    print(f"🔌 Connecting to Mosquitto broker at {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("🔌 Disconnecting...")
        client.loop_stop() # Stop the MQTT loop
        client.disconnect() # Disconnect from the broker
        print("🚫 Disconnected.")

if __name__ == "__main__":
    # Run MQTT client in a separate thread
    mqtt_thread = threading.Thread(target=lambda: asyncio.run(main()), daemon=True) 
    mqtt_thread.start()  # Start MQTT client in a background thread
    print("🐒 MQTT client started in background thread")
    
    bot.run()  # Start Telegram bot in the main thread
