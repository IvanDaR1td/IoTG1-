from machine import ADC
from network import WLAN
import time
import umqtt.robust as umqtt

HOSTNAME = '10.46.41.91'
PORT = 1883
TOPIC = b'temp/pico'

mqtt = umqtt.MQTTClient(
    client_id = b'publish',
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


# Temperature setup
temp_sensor = ADC(4)

def read_temp():
    value = temp_sensor.read_u16()
    voltage = value * (3.3 / 65535)
    temperature = 27 - (voltage - 0.706) / 0.001721
    return temperature


# MQTT publish
def mosquitto():
    temp = read_temp()
    print(temp, TOPIC)
    mqtt.publish(TOPIC, str(temp).encode())


is_connected = connect(wifi, ssid, password)

if is_connected:
    print("Connection made")

    mqtt.connect()
    print("MQTT connected")

    while True:
        mosquitto()
        time.sleep(0.5)

else:
    print("WiFi connection failed")

