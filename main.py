import asyncio
import threading
import time
import pygame

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
from bot.telegram import TelegramBot

# AWS IoT Config
ENDPOINT = "a3rc34zf1lqqgc-ats.iot.ap-southeast-1.amazonaws.com"
CLIENT_ID = "raspberry_monyet"
PATH_TO_CERT = "/home/pi/Desktop/raspberry_pi_code/certs/3a05842fb863cc101019a2e3e2ab19a61aa8b7b37084bcd4f9c14de886473e6c-certificate.pem.crt"
PATH_TO_KEY = "/home/pi/Desktop/raspberry_pi_code/certs/3a05842fb863cc101019a2e3e2ab19a61aa8b7b37084bcd4f9c14de886473e6c-private.pem.key"
PATH_TO_ROOT_CA = "/home/pi/Desktop/raspberry_pi_code/certs/AmazonRootCA1.pem"
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

# Play sound one time
def play_sound_once():
    if not audio_ready:
        print("🔇 Skipping sound playback, audio device not ready")
        return

    try:
        pygame.mixer.music.load("/home/pi/Desktop/raspberry_pi_code/example.mp3")
        pygame.mixer.music.play()
        print("🔊 Alarm playing once")
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        print("🔇 Alarm finished")
    except Exception as e:
        print(f"⚠️ Error playing sound: {e}")

# MQTT callback
def on_message_received(topic, payload, **kwargs):
    message = payload.decode()
    print(f"📩 Received MQTT message from '{topic}': {message}")

    threading.Thread(target=play_sound_once, daemon=True).start()
    asyncio.run(bot.send_message("🐒 MQTT message received", sensor_active=True))

# MQTT Connection Setup
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=PATH_TO_CERT,
    pri_key_filepath=PATH_TO_KEY,
    client_bootstrap=client_bootstrap,
    ca_filepath=PATH_TO_ROOT_CA,
    client_id=CLIENT_ID,
    clean_session=False,
    keep_alive_secs=30,
)

# Async main
async def main():
    print("🔌 Connecting to AWS IoT Core...")
    connect_future = mqtt_connection.connect()
    connect_future.result()
    print("✅ Connected!")

    print(f"📡 Subscribing to topic '{TOPIC}'...")
    subscribe_future, _ = mqtt_connection.subscribe(
        topic=TOPIC,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received
    )
    subscribe_future.result()
    print("✅ Subscribed!")

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔌 Disconnecting...")
        mqtt_connection.disconnect().result()
        print("🚫 Disconnected.")
