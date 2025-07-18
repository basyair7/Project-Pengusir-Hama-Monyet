import sys
import threading
import time
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder

# Device credentials
ENDPOINT = "a3rc34zf1lqqgc-ats.iot.ap-southeast-1.amazonaws.com"  # e.g. abcd1234-ats.iot.us-east-1.amazonaws.com
CLIENT_ID = "raspberry_monyet"
PATH_TO_CERT = "certs/3a05842fb863cc101019a2e3e2ab19a61aa8b7b37084bcd4f9c14de886473e6c-certificate.pem.crt"
PATH_TO_KEY = "certs/3a05842fb863cc101019a2e3e2ab19a61aa8b7b37084bcd4f9c14de886473e6c-private.pem.key"
PATH_TO_ROOT_CA = "certs/AmazonRootCA1.pem"
TOPIC = "esp8266/pub"

# Callback for received messages
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print(f"Received message from topic '{topic}': {payload.decode()}")

# Set up the MQTT connection
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

# Connect
print("Connecting to AWS IoT Core...")
connect_future = mqtt_connection.connect()
connect_future.result()
print("Connected!")

# Subscribe
print(f"Subscribing to topic '{TOPIC}'...")
subscribe_future, packet_id = mqtt_connection.subscribe(
    topic=TOPIC,
    qos=mqtt.QoS.AT_LEAST_ONCE,
    callback=on_message_received
)
subscribe_result = subscribe_future.result()
print("Subscribed!")

# Keep the script running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")
