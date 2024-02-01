# Flakely

Allows for the generation and validation of SHA256 signed snowflakes.

## Installation

```shell
pip install flakely
```

## Usage

The `flakely.Flakely` class handles generation and validation of the signed snowflakes. It accepts the following arguemnts:

- `device: int` a device ID that is encoded into each snowflake
- `process: int` a process ID that is encoded into each snowflake
- `secret: str | bytes` used to generate unpredictable signature hashes

`Flakely.generate() -> int`

Generates a new signed snowflake and returns it as an `int`.

`Flakely.generate_bytes() -> bytes`

Generates a new signed snowflake and returns it as a `bytes` object.

`Flakely.validate(snowflake: int | bytes) -> bool`

Checks that a snowflake's signature is valid for the payload.

`Flakely.get_signature(flake: bytes) -> bytes`

Generates a signature for the snowflake payload as SHA256 digest.

`Flakely.get_tick() -> int`

Returns an integer to use as the timestamp.
