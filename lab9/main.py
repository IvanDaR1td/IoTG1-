"""Lab 9: one MicroPython program, selected by config.ROLE on each Pico W."""

import math
import time
from binascii import hexlify

import machine
import network
import ntptime
from umqtt.simple import MQTTClient, MQTTException
from telemetry_upb2 import TemperatureReading


def validate_config(cfg):
    if cfg.ROLE not in ("publisher", "subscriber"):
        raise ValueError("ROLE must be publisher or subscriber")
    if not cfg.WIFI_SSID or cfg.WIFI_SSID == "YOUR_WIFI_SSID":
        raise ValueError("Fill in WIFI_SSID in the local configuration file")
    if cfg.WIFI_PASSWORD == "YOUR_WIFI_PASSWORD":
        raise ValueError("Fill in WIFI_PASSWORD in the local configuration file")
    if not cfg.MQTT_HOST or cfg.MQTT_HOST == "YOUR_PI_IP":
        raise ValueError("Set MQTT_HOST to the Raspberry Pi's current LAN IP")
    if not isinstance(cfg.TOPIC, bytes) or not cfg.TOPIC:
        raise ValueError("TOPIC must be a non-empty bytes value")
    if cfg.PUBLISH_INTERVAL_MS < 100:
        raise ValueError("PUBLISH_INTERVAL_MS must be at least 100")
    if cfg.TIME_SOURCE not in ("ntp", "rtc"):
        raise ValueError("TIME_SOURCE must be ntp or rtc")


def connect_wifi(wlan, cfg):
    if wlan.isconnected():
        return
    wlan.active(True)
    wlan.connect(cfg.WIFI_SSID, cfg.WIFI_PASSWORD)
    started = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), started) >= 20000:
            wlan.disconnect()
            raise OSError("Wi-Fi connection timed out; check local settings")
        time.sleep_ms(250)
    print("Wi-Fi connected")


def prepare_clock(cfg):
    """Do not publish made-up time after a cold boot."""
    if cfg.TIME_SOURCE == "ntp":
        ntptime.host = cfg.NTP_HOST
        ntptime.timeout = 3
        for attempt in range(3):
            try:
                ntptime.settime()
                print("Clock synchronised to UTC")
                return
            except OSError:
                print("NTP attempt %d/3 failed" % (attempt + 1))
                time.sleep(1)
        raise OSError("NTP unavailable: use TIME_SOURCE='rtc' and upload.py --run")
    if time.gmtime()[0] < 2024:
        raise OSError("RTC is unset: set current UTC with upload.py --run")
    print("Using RTC in UTC; ensure it was set from the computer this session")


def read_temperature(sensor):
    voltage = sensor.read_u16() * (3.3 / 65535)
    return 27 - (voltage - 0.706) / 0.001721


def validate_reading(reading):
    if not math.isfinite(reading.temperature_c):
        raise ValueError("Temperature is not finite")
    if not reading.publisher_id.strip() or len(reading.publisher_id.encode()) > 64:
        raise ValueError("Publisher ID must contain 1-64 UTF-8 bytes")
    clock = reading.time
    if not (0 <= clock.hour <= 23 and 0 <= clock.minute <= 59
            and 0 <= clock.second <= 59):
        raise ValueError("Invalid time of day")
    return reading


def make_reading(temperature, publisher_id, utc):
    reading = TemperatureReading()
    reading.temperature_c = temperature
    reading.publisher_id = publisher_id
    reading.time.hour = utc[3]
    reading.time.minute = utc[4]
    reading.time.second = utc[5]
    return validate_reading(reading)


def decode_reading(payload):
    if not payload or len(payload) > 256:
        raise ValueError("Empty or oversized Protobuf payload")
    # T0ha/uprotobuf.decode is a class method returning a new message.
    return validate_reading(TemperatureReading.decode(payload))


def show_reading(prefix, reading, size):
    clock = reading.time
    print("%s id=%s temp=%.2f C time=%02d:%02d:%02d UTC bytes=%d" % (
        prefix, reading.publisher_id, reading.temperature_c,
        clock.hour, clock.minute, clock.second, size))


def make_callback(expected_topic):
    def on_message(topic, payload):
        if topic != expected_topic:
            return
        try:
            reading = decode_reading(payload)
        except Exception as error:
            # Invalid or old Lab 8 text messages must not stop the subscriber.
            print("Ignored invalid Protobuf message:", type(error).__name__)
            return
        show_reading("RX", reading, len(payload))
    return on_message


def serve(client, wlan, sensor, publisher_id, cfg):
    last_publish = time.ticks_ms()
    last_ping = last_publish
    first_reading = True
    while True:
        if not wlan.isconnected():
            raise OSError("Wi-Fi disconnected")
        client.check_msg()  # Also consumes MQTT PINGRESP packets.
        now = time.ticks_ms()
        if cfg.ROLE == "publisher" and (first_reading or
                time.ticks_diff(now, last_publish) >= cfg.PUBLISH_INTERVAL_MS):
            reading = make_reading(read_temperature(sensor), publisher_id, time.gmtime())
            payload = reading.encode()
            client.publish(cfg.TOPIC, payload, retain=False, qos=0)
            show_reading("TX", reading, len(payload))
            first_reading = False
            last_publish = now
        if time.ticks_diff(now, last_ping) >= 20000:
            client.ping()
            last_ping = now
        time.sleep_ms(50)


def run(cfg=None):
    if cfg is None:
        try:
            import config as cfg
        except ImportError:
            print("Missing config.py: copy and edit the appropriate config example")
            return
    validate_config(cfg)
    # Support both older and newer MicroPython station-interface constants.
    station = getattr(network.WLAN, "IF_STA", None)
    if station is None:
        station = network.STA_IF
    wlan = network.WLAN(station)
    device_id = hexlify(machine.unique_id()).decode()
    publisher_id = cfg.PUBLISHER_ID or ("pico-" + device_id)
    client_id = ("lab9-" + cfg.ROLE + "-" + device_id).encode()
    sensor = machine.ADC(4) if cfg.ROLE == "publisher" else None
    clock_ready = False
    print("Lab 9 role=%s topic=%s" % (cfg.ROLE, cfg.TOPIC.decode()))

    while True:
        client = None
        try:
            connect_wifi(wlan, cfg)
            if cfg.ROLE == "publisher" and not clock_ready:
                prepare_clock(cfg)
                clock_ready = True
            client = MQTTClient(client_id, cfg.MQTT_HOST, port=cfg.MQTT_PORT,
                                keepalive=60)
            client.set_callback(make_callback(cfg.TOPIC))
            client.connect(clean_session=True, timeout=8)
            if cfg.ROLE == "subscriber":
                # Resubscribe after EVERY reconnect, including a broker restart.
                client.subscribe(cfg.TOPIC, qos=0)
            print("MQTT connected to %s:%d" % (cfg.MQTT_HOST, cfg.MQTT_PORT))
            serve(client, wlan, sensor, publisher_id, cfg)
        except KeyboardInterrupt:
            print("Stopped")
            return
        except (OSError, MQTTException) as error:
            print("Connection problem:", error)
            print("Retrying in 3 seconds")
        finally:
            if client is not None and client.sock is not None:
                try:
                    client.sock.close()
                except OSError:
                    pass
        time.sleep(3)


if __name__ == "__main__":
    run()
