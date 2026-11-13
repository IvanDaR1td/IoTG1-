# Third party code

## uprotobuf

Source: [T0ha/uprotobuf](https://github.com/T0ha/uprotobuf/tree/d5a4c6d3679d4c564baf9db71024f3555dfe8f1d), commit `d5a4c6d3679d4c564baf9db71024f3555dfe8f1d`.

The included `tools/uprotobuf_plugin.py` is the upstream compiler plugin, unchanged. Generated modules import `protobuf.uprotobuf`, so this project preserves that package layout. The runtime's `decode()` is a class method returning a new message; the application uses `TemperatureReading.decode(payload)`.

`protobuf/uprotobuf.py` includes three small local corrections:

1. Encode required fields even when their value equals the default. This preserves required zero temperatures and the zero components of `00:00:00` for Google Protobuf interoperability.
2. Reject missing required fields while decoding, including inside nested messages.
3. Reject length-delimited fields whose declared length exceeds the available bytes.

No claim is made that this adds full Protobuf conformance. In particular, this runtime rejects unknown fields rather than skipping them; both boards should use the same schema. The original MIT notice is in `licenses/uprotobuf-LICENSE.txt`.

## MicroPython libraries

Source: [micropython/micropython-lib](https://github.com/micropython/micropython-lib/tree/92ee97d94c4b558cf4e6d27a4534401f1e9b9f50), commit `92ee97d94c4b558cf4e6d27a4534401f1e9b9f50`.

- `umqtt/simple.py`: copied unchanged from `micropython/umqtt.simple/umqtt/simple.py`.
- `ntptime.py`: copied unchanged from `micropython/net/ntptime/ntptime.py`.
- Empty `__init__.py` files are provided for package imports.

The upstream license collection is retained in `licenses/micropython-lib-LICENSE.txt`. MQTT reconnects are handled explicitly by this project's main loop, which recreates the connection and subscription after an error.
