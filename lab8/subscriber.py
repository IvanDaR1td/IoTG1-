from machine import Pin
from network import WLAN
import time
import umqtt.robust as umqtt

HOSTNAME = '10.46.41.91'
PORT = 1883
TOPIC = b'temp/pico'

# LED setup
led = Pin("LED", Pin.OUT)
led.value(0)

# MQTT setup
mqtt = umqtt.MQTTClient(
    client_id = b'subscribe',
    server = HOSTNAME.encode(),
    port = PORT,
    keepalive = 7000
)

# WiFi setup
wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

ssid = "ssid"
password = "Password"

def connect(wifi_obj, ssid, password, timeout=10):
    print("Trying to connect to WiFi")
    wifi_obj.connect(ssid, password)

    while timeout > 0:
        if wifi_obj.isconnected():
            print("Connected successfully")
            return True

        time.sleep(1)
        timeout -= 1

    return False


# MQTT callback
def callback(topic, message):
    if topic != TOPIC:
        return

    print(f'Received message "{message}" for topic "{topic}"')

    temp = float(message.decode())

    if temp >= 25:
        led.value(1)
        print("Temperature >= 25: LED ON")
    else:
        led.value(0)
        print("Temperature < 25: LED OFF")


# Connect and subscribe
is_connected = connect(wifi, ssid, password)

if is_connected:
    print("WiFi connection made")

    mqtt.set_callback(callback)
    mqtt.connect()
    mqtt.subscribe(TOPIC)

    print("Subscribed to", TOPIC)

    while True:
        mqtt.wait_msg()

else:
    print("WiFi connection failed")

from machine import Pin
from network import WLAN
import time
import umqtt.robust as umqtt

HOSTNAME = '10.46.41.91'
PORT = 1883
TOPIC = b'temp/pico'

# LED setup
led = Pin("LED", Pin.OUT)
led.value(0)

# MQTT setup
mqtt = umqtt.MQTTClient(
    client_id = b'subscribe',
    server = HOSTNAME.encode(),
    port = PORT,
    keepalive = 7000
)

# WiFi setup
wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

ssid = "Fork"
password = "Password123!"

def connect(wifi_obj, ssid, password, timeout=10):
    print("Trying to connect to WiFi")
    wifi_obj.connect(ssid, password)

    while timeout > 0:
        if wifi_obj.isconnected():
            print("Connected successfully")
            return True

        time.sleep(1)
        timeout -= 1

    return False


# MQTT callback
def callback(topic, message):
    if topic != TOPIC:
        return

    print(f'Received message "{message}" for topic "{topic}"')

    temp = float(message.decode())

    if temp >= 25:
        led.value(1)
        print("Temperature >= 25: LED ON")
    else:
        led.value(0)
        print("Temperature < 25: LED OFF")


# Connect and subscribe
is_connected = connect(wifi, ssid, password)

if is_connected:
    print("WiFi connection made")

    mqtt.set_callback(callback)
    mqtt.connect()
    mqtt.subscribe(TOPIC)

    print("Subscribed to", TOPIC)

    while True:
        mqtt.wait_msg()

else:
    print("WiFi connection failed")

