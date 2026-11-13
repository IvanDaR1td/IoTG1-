# IoT MQTT Lab — Pico W Temperature Monitoring

A MicroPython lab demonstrating MQTT communication between two Raspberry Pi Pico W boards through a Mosquitto broker running on a Raspberry Pi. The publisher reads its onboard temperature sensor and sends readings to `temp/pico`. The subscriber receives those readings and switches its onboard LED **on at 25°C or above** and **off below 25°C**.

## Group members

| Name | Student ID |
| --- | --- |
| Iulian Ursu | C23531183 |
| Xingyi Chen | D22126393 |
| Mohamed Elrayah | C23458442 |

## Project status and files

This README documents the supplied `publisher.py` and `subscriber.py`. The subscriber needs cleanup before committing. **`mosquitto.conf` is pending and will be copied from the lab Raspberry Pi once it is available.** Its contents and the broker's access settings have not been verified.

Expected repository layout, with the pending file explicitly marked:

```text
.
├── README.md          # Project documentation
├── publisher.py       # Pico W temperature publisher
├── subscriber.py      # Pico W LED subscriber; duplicate code needs cleanup
└── mosquitto.conf     # PENDING — not yet included
```

No placeholder broker configuration is supplied. When the Raspberry Pi is available, copy the actual configuration used for the lab, review it for secrets, and document any included configuration files it depends on.

### Source review before committing

- **Duplicated subscriber:** the supplied `subscriber.py` contains two identical 78-line blocks. Lines 79–156 repeat lines 1–78. Keep one complete copy of the program.
- **Check `else` indentation:** the supplied file passes a Python syntax check, so an indentation error is **not confirmed**. In the received file, the callback's `else` lines (56 and 134) correctly align with `if temp >= 25`, and the connection-failure `else` lines (76 and 154) correctly align with `if is_connected`. Preserve these relationships when removing the duplicate or copying the code into an editor.
- **Remove credentials:** both scripts currently contain a hardcoded Wi-Fi password. Replace real credentials with placeholders before committing, or change the scripts to import credentials from an untracked local file. This README does not reproduce the password. External credential loading is a suggested change, not an existing feature.

A successful syntax check does not verify MicroPython imports, hardware behaviour, Wi-Fi connectivity, or the broker configuration. The hardware tests below remain to be run against the final cleaned scripts.

## How it works

```text
Publisher Pico W                    Raspberry Pi                 Subscriber Pico W
ADC(4) → temperature in °C  ──────→  Mosquitto broker  ─────────→  onboard LED
publish to temp/pico                TCP port 1883                 ON:  temperature ≥ 25°C
                                                                 OFF: temperature < 25°C
```

### Publisher

`publisher.py` activates the Wi-Fi station interface and checks for a connection for up to approximately 10 seconds. If connected, it connects to the broker and repeatedly:

1. Reads the RP2040's internal temperature sensor using `ADC(4)` and `read_u16()`.
2. Converts the reading to voltage and then degrees Celsius:

   ```python
   voltage = value * (3.3 / 65535)
   temperature = 27 - (voltage - 0.706) / 0.001721
   ```

3. Publishes `str(temp).encode()` to `b'temp/pico'`.
4. Waits `0.5` seconds before repeating, giving approximately two readings per second when communication is working normally.

The payload is a numeric text value, such as `24.8`, without a unit suffix or JSON wrapper. The onboard sensor measures chip temperature; it is not a calibrated room-temperature sensor. MicroPython documents the internal sensor and ADC scaling in its [RP2 ADC reference](https://docs.micropython.org/en/latest/rp2/quickref.html#adc-analog-to-digital-conversion).

### Subscriber

`subscriber.py` initialises `Pin("LED", Pin.OUT)` and turns the LED off. It connects to Wi-Fi and MQTT, registers its callback, subscribes to `b'temp/pico'`, and waits for messages with `mqtt.wait_msg()`.

The callback ignores other topics, decodes the payload, converts it with `float()`, and applies:

| Received temperature | LED state |
| --- | --- |
| Below 25°C | OFF (`led.value(0)`) |
| Exactly 25°C | ON (`led.value(1)`) |
| Above 25°C | ON (`led.value(1)`) |

## Hardware and software

| Item | Purpose |
| --- | --- |
| Two Raspberry Pi Pico W boards | One publisher and one subscriber for the complete demonstration |
| Raspberry Pi with Raspberry Pi OS, storage and power supply | Mosquitto broker host |
| USB data cables and a development computer | Program and monitor the Pico W boards |
| Wi-Fi network accessible to both Pico W boards | Reach the broker over the local network |
| MicroPython firmware for Pico W | Runs the two scripts |
| `umqtt.robust` and `umqtt.simple` on each Pico W | MQTT client libraries |
| `mpremote` on the development computer | Install libraries and run scripts over USB |
| Mosquitto and its command-line clients | Broker and message testing |

No external temperature sensor, external LED, breadboard, or GPIO wiring is required. Both scripts run on Pico W boards; the Raspberry Pi runs the broker.

## Configuration

Review these values in both scripts before running:

| Setting | Supplied value | Notes |
| --- | --- | --- |
| `HOSTNAME` | `10.46.41.91` | Lab broker address in the source; replace with the Raspberry Pi's current reachable LAN address |
| `PORT` | `1883` | MQTT TCP port used by both scripts |
| `TOPIC` | `b'temp/pico'` | Must match in both scripts |
| Publisher client ID | `b'publish'` | Use a unique ID for each simultaneously connected client |
| Subscriber client ID | `b'subscribe'` | Use a unique ID for each simultaneously connected client |
| `keepalive` | `7000` seconds | Value passed to the MQTT client in both scripts |
| `ssid` | Set locally | Wi-Fi network name |
| `password` | Set locally; intentionally omitted here | Do not commit the real password |
| Publisher delay | `0.5` seconds | Delay after each publication |
| LED threshold | `25` °C | The callback uses `temp >= 25` |

The scripts do not supply MQTT authentication credentials or enable TLS. Whether the broker accepts those connections must be checked against the real `mosquitto.conf`. Do not assume the Wi-Fi password is also an MQTT password.

## Setup

### 1. Prepare the broker

When the Raspberry Pi is available, install the broker and client utilities on Raspberry Pi OS if needed:

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto
systemctl status mosquitto --no-pager
hostname -I
```

Mosquitto is available through the Raspberry Pi package repository. See the [official installation page](https://mosquitto.org/download/).

Use the Pi's appropriate LAN address for `HOSTNAME` in both scripts. Confirm that the actual lab configuration allows the Pico W boards to connect on TCP port `1883` and use `temp/pico`. A running service alone does not prove that remote clients can connect: listener and authentication settings must match the clients. See the [Mosquitto configuration reference](https://mosquitto.org/man/mosquitto-conf-5.html).

**Pending:** retrieve the working `mosquitto.conf` from the Raspberry Pi before claiming the broker setup is reproducible. Do not replace the Pi's existing configuration with an invented example.

### 2. Prepare each Pico W

Install a stable [MicroPython firmware build for Raspberry Pi Pico W](https://micropython.org/download/RPI_PICO_W/). To flash it, hold BOOTSEL while connecting USB, then copy the downloaded UF2 file onto the drive that appears.

On the development computer, install `mpremote` and list the connected boards:

```bash
python3 -m pip install --user mpremote
mpremote connect list
```

Replace `PUBLISHER_PORT` and `SUBSCRIBER_PORT` below with the respective device paths or port names from that list. Close other serial monitors before using a board with `mpremote`.

```bash
mpremote connect PUBLISHER_PORT mip install umqtt.simple umqtt.robust
mpremote connect SUBSCRIBER_PORT mip install umqtt.simple umqtt.robust
```

These commands use MicroPython's package installation workflow. See the [mpremote documentation](https://docs.micropython.org/en/latest/reference/mpremote.html). Both packages are listed explicitly because [`umqtt.robust` imports `umqtt.simple`](https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.robust/umqtt/robust.py).

### 3. Configure and run

Remove the duplicated subscriber block, review its indentation, and set the Wi-Fi credentials locally. Update both broker addresses and keep the topic and port consistent.

From the repository directory, start the subscriber in one terminal:

```bash
mpremote connect SUBSCRIBER_PORT run subscriber.py
```

Then start the publisher in a second terminal:

```bash
mpremote connect PUBLISHER_PORT run publisher.py
```

Watch both terminals for connection messages and temperature output. `mpremote run` executes the local script on the board without saving it there permanently. After testing, an optional standalone deployment is to copy each board's corresponding script to its filesystem as `main.py`, keeping the descriptive filenames in the repository. See [mpremote run and file-copy behaviour](https://docs.micropython.org/en/latest/reference/mpremote.html).

## Testing

These are test instructions and expected outcomes, not a claim that the hardware tests have already passed. Run the commands on the Raspberry Pi or another machine with Mosquitto clients installed. Replace `BROKER_IP` with the same address configured in the scripts. The commands assume broker access compatible with the supplied unauthenticated clients.

### Observe published readings

With both Pico W programs running:

```bash
mosquitto_sub -h BROKER_IP -p 1883 -t temp/pico -v
```

Expect lines containing `temp/pico` followed by a numeric temperature, approximately twice per second. The exact values depend on the board and conditions. The subscriber LED should follow the threshold table. The [Mosquitto client examples](https://mosquitto.org/documentation/using-the-snap/) explain the subscribe/publish command options.

### Check the threshold precisely

Stop or disconnect the **publisher only**, leaving the broker and subscriber running. Otherwise, live readings can immediately overwrite the LED state caused by a test message.

Run each command separately and inspect the LED before sending the next:

| Test command | Expected LED |
| --- | --- |
| `mosquitto_pub -h BROKER_IP -p 1883 -t temp/pico -m '24.9'` | OFF |
| `mosquitto_pub -h BROKER_IP -p 1883 -t temp/pico -m '25.0'` | ON |
| `mosquitto_pub -h BROKER_IP -p 1883 -t temp/pico -m '25.1'` | ON |
| `mosquitto_pub -h BROKER_IP -p 1883 -t temp/pico -m '20.0'` | OFF |

Restart the publisher and confirm that live readings resume. Record the results, firmware/library versions, and broker configuration when the Raspberry Pi is available.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Wi-Fi connection fails | Local SSID/password, signal, and network compatibility; the script checks for about 10 seconds before reporting failure |
| MQTT connection fails | Broker address, service status, listener, authentication, and network rules for TCP port 1883 |
| `ImportError` for `umqtt` | Install both MQTT packages on the affected Pico W |
| `IndentationError` after editing | Keep one subscriber block; align each `else` with its corresponding `if` and use consistent spaces |
| LED stays off | Confirm a numeric reading of at least 25°C reaches `temp/pico` and the subscriber callback runs |
| Manual LED test changes back immediately | Stop the live publisher before injecting test temperatures |
| Clients repeatedly disconnect | Check that every connected MQTT client has a unique client ID |
| No messages after a broker restart | Restart the subscriber to establish a fresh connection and subscription, then investigate reconnect handling |

## Limitations

- **Temperature accuracy:** readings estimate the chip's temperature using a fixed conversion formula and assumed 3.3 V reference. Calibration, supply variation and self-heating affect their relationship to ambient temperature.
- **Payload validation:** `float(message.decode())` has no exception handling. An invalid numeric payload can terminate the subscriber, leaving the LED in its previous state.
- **Threshold behaviour:** there is no hysteresis or smoothing, so readings near 25°C can repeatedly switch the LED.
- **Connection recovery:** Wi-Fi startup has a short checking period, and initial MQTT connection failures are not handled explicitly. `umqtt.robust` retries some MQTT operations, but the application has no explicit Wi-Fi recovery or resubscription logic. Recovery after outages or a broker restart needs testing. See the [library implementation](https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.robust/umqtt/robust.py).
- **Keepalive and stale state:** the scripts do not explicitly schedule MQTT pings, report device availability, or turn the LED off when readings stop. The LED can remain in its last state after the publisher disconnects.
- **Delivery and history:** publish/subscribe calls use the library's default QoS 0; published readings are not retained. There is no application-level acknowledgement or stored measurement history. These defaults are defined in [`umqtt.simple`](https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.simple/umqtt/simple.py).
- **Security:** the current clients use plaintext MQTT and no MQTT authentication. Keep this setup within the intended lab environment; authentication and TLS would require coordinated broker and client changes. Real Wi-Fi credentials must be removed from files intended for GitHub.
- **Reproducibility:** the actual `mosquitto.conf`, software versions and hardware test results are still to be documented.
