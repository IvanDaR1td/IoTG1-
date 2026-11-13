# Copy to config.publisher.py on your computer; upload.py saves it as config.py.
# Keep the real Wi-Fi password in the ignored local copy, not this example.
ROLE = "publisher"
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
MQTT_HOST = "YOUR_PI_IP"  # Check current address; last week's was 10.46.41.91.
MQTT_PORT = 1883  # Example: confirm today's broker port; Lab 8 used 8080.
TOPIC = b"temp/pico/protobuf"  # Both boards must use this same topic.
PUBLISHER_ID = "pico-1"  # Give each publisher a different, recognisable ID.
PUBLISH_INTERVAL_MS = 500
TIME_SOURCE = "ntp"  # Use "rtc" with upload.py --run if NTP is blocked.
NTP_HOST = "pool.ntp.org"
