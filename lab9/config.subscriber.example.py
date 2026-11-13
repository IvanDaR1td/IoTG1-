# Copy to config.subscriber.py on your computer; upload.py saves it as config.py.
# Keep the real Wi-Fi password in the ignored local copy, not this example.
ROLE = "subscriber"
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
MQTT_HOST = "YOUR_PI_IP"
MQTT_PORT = 1883  # Example: confirm today's broker port; Lab 8 used 8080.
TOPIC = b"temp/pico/protobuf"
PUBLISHER_ID = ""  # Unused in subscriber mode.
PUBLISH_INTERVAL_MS = 500
TIME_SOURCE = "ntp"  # Subscribers display the publisher's time; no NTP needed.
NTP_HOST = "pool.ntp.org"
