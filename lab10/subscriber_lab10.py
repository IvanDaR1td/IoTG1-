
from machine import Pin, I2C
from network import WLAN
import time
import sys
import umqtt.robust as umqtt

sys.path.append("/lab10")
from lcd1602 import LCD1602



# MQTT setup

HOSTNAME = '172.20.10.2'
PORT = 8080
TOPIC = b'temp/pico'


# =====================================
# LCD scrolling settings
# =====================================

LCD_WIDTH = 16

# 350ms per character
# Approximately 5.6 seconds per 16 characters
SCROLL_STEP_MS = 350

# Extra time to read first and last screens
FIRST_HOLD_MS = 1000
LAST_HOLD_MS = 1000

POLL_MS = 20


# LED and LCD setup

led = Pin("LED", Pin.OUT)
led.value(0)

# Physical Pin 6 = GP4 (SDA)
# Physical Pin 7 = GP5 (SCL)
i2c = I2C(
    0,
    sda=Pin(4),
    scl=Pin(5),
    freq=100000
)

lcd = LCD1602(i2c, 2, 0)
lcd.clear()


# MQTT client

mqtt = umqtt.MQTTClient(
    client_id=b'subscribe',
    server=HOSTNAME.encode(),
    port=PORT,
    keepalive=7000
)


# WiFi setup

wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

ssid = b"NOT Ivan\xe2\x80\x99s iPhone\x20".decode("utf-8")
password = "A4351966"



# Global state

scrolling = False
pending_temp = None
ignored_count = 0


# WiFi connection

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


# LCD helper

def lcd_line(row, text):
    # Limit output to 16 characters
    text = str(text)[:LCD_WIDTH]

    # Clear unused characters from previous text
    text = text + " " * (LCD_WIDTH - len(text))

    lcd.setCursor(0, row)
    lcd.print(text)


# Temperature classification

def classify_temp(temp):
    if temp < 16:
        return "too cold"

    elif temp > 25:
        return "too hot"

    else:
        return "just right"


# MQTT callback

def callback(topic, message):
    global pending_temp, ignored_count

    if topic != TOPIC:
        return

    # Lab 10: ignore messages during scrolling
    if scrolling:
        ignored_count += 1
        return

    try:
        temp = float(message.decode())
        pending_temp = temp

        print("Received temperature:", temp)

    except ValueError:
        print("Invalid temperature message")


# Wait while processing MQTT messages

def scroll_wait(duration_ms):

    deadline = time.ticks_add(
        time.ticks_ms(), duration_ms
    )

    while time.ticks_diff(
        deadline, time.ticks_ms()
    ) > 0:

        # Process MQTT packets during scrolling.
        # Callback will discard temperature messages.
        mqtt.check_msg()

        time.sleep_ms(POLL_MS)


# LCD temperature display

def display_temp(temp):
    global scrolling, ignored_count

    status = classify_temp(temp)

    message = (
        "The temperature is {:.1f} degrees. "
        "This is {}."
    ).format(temp, status)

    print("Displaying:", message)

    # Preserve original Lab 8 LED behaviour
    if temp >= 25:
        led.value(1)
        print("LED ON")
    else:
        led.value(0)
        print("LED OFF")

    # Begin scrolling
    scrolling = True
    ignored_count = 0

    try:
        # LCD second row: temperature and status
        lcd_line(
            1,
            "{:.1f}C {}".format(temp, status)
        )

        # LCD first row: scrolling sentence
        steps = max(
            1,
            len(message) - LCD_WIDTH + 1
        )

        for i in range(steps):

            # Display a 16-character window
            window = message[i:i + LCD_WIDTH]
            lcd_line(0, window)

            # Longer pause at beginning and end
            if i == 0:
                delay = FIRST_HOLD_MS

            elif i == steps - 1:
                delay = LAST_HOLD_MS

            else:
                delay = SCROLL_STEP_MS

            # Continue checking MQTT during delay
            scroll_wait(delay)

        # Drain packets already queued at the end.
        # Keep scrolling=True while discarding.
        for _ in range(100):
            result = mqtt.check_msg()

            if result is None:
                break

    finally:
        scrolling = False

    print("Scrolling finished")
    print("Ignored messages:", ignored_count)
    print("------------------------------")


# Main program

lcd_line(0, "IoT Lab 10")
lcd_line(1, "Connecting WiFi")

is_connected = connect(wifi, ssid, password)

if is_connected:

    print("WiFi connection made")

    lcd_line(0, "Connecting MQTT")
    lcd_line(1, "Please wait")

    mqtt.set_callback(callback)
    mqtt.connect()
    mqtt.subscribe(TOPIC)

    print("Subscribed to", TOPIC)

    lcd_line(0, "MQTT connected")
    lcd_line(1, "Waiting for temp")

    while True:

        # Listen for MQTT messages
        mqtt.check_msg()

        # Only display a new temperature
        # after the previous scroll has finished
        if pending_temp is not None:

            temp = pending_temp
            pending_temp = None

            display_temp(temp)

        time.sleep_ms(20)

else:

    print("WiFi connection failed")

    lcd_line(0, "WiFi failed")
    lcd_line(1, "Check connection")

