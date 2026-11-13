# Lab 9 Protocol Buffers over MQTT

Two Pico W boards run the same `main.py`. The publisher reads the RP2040 temperature sensor using `ADC(4)`, encodes a Protobuf reading and publishes it to Mosquitto. The subscriber decodes the payload and prints the publisher ID, temperature and UTC time.

## Team

| Name | Student ID |
| --- | --- |
| Iulian Ursu | C23531183 |
| Xingyi Chen | D22126393 |
| Mohamed Elrayah | C23458442 |

## Generate the Protobuf modules

`telemetry.proto` defines a proto2 `TemperatureReading` with a Celsius temperature, a publisher ID and a nested UTC time of day. In the repository directory on a computer with Python 3.10 or later, create a virtual environment, activate it and run the following commands.

```bash
python -m pip install -r requirements-dev.txt
python tools/generate.py
```

The generator compiles `telemetry.proto` and invokes the bundled uprotobuf plugin. It creates `telemetry_upb2.py` for the Pico and a CPython module under `tests/generated/`. Both outputs are generated locally and ignored by Git.

## Install and run

1. On each Pico W running MicroPython, use Thonny to copy `main.py`, `telemetry_upb2.py`, `ntptime.py` and the complete `protobuf/` and `umqtt/` directories into `/lab9`.
2. On the publisher, save an edited copy of `config.publisher.example.py` as `/config.py`. On the subscriber, use `config.subscriber.example.py`. Fill in the local Wi-Fi credentials, broker address and port in each copy. Keep these copies private.
3. Use the same topic on both boards. Our hardware run used `temp/pico/protobuf` on `172.20.10.2:8080`. Set both `MQTT_PORT` values to `8080` for that setup.
4. In each board's Thonny Shell, run the commands below. Start the subscriber first, then the publisher. The publisher synchronises its clock over NTP before sending data.

```python
import os, sys
os.chdir("/")
sys.path.insert(0, "/")
sys.path.insert(0, "/lab9")
import config, main
main.run(config)
```

## Hardware results

On 13 November 2026, the publisher sent readings via the Raspberry Pi Mosquitto broker and the subscriber decoded them continuously. The lines below are from different moments in the same run.

```text
TX id=pico-1 temp=24.70 C time=14:59:34 UTC bytes=21
RX id=pico-1 temp=25.17 C time=15:00:04 UTC bytes=21
```

See [third-party sources and modifications](THIRD_PARTY.md) and the notices in `licenses/`.
