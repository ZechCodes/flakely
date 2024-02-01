import time
from typing import Callable, Literal, TypeVar

import os
import secrets
import hashlib


T = TypeVar("T")


def _use_if_set_else(value: T, default: Callable[[], T]) -> T:
    if value is None:
        return default()

    return value


class Flakely:
    COUNTER_SIZE = 2
    DEVICE_ID_SIZE = 4
    IDENTIFIER_SIZE = 4
    PROCESS_ID_SIZE = 4
    SIGNATURE_SIZE = 32
    TICK_SIZE = 4
    BYTE_ORDER: Literal["big", "little"] = "little"

    def __init__(
        self,
        device: int | None = None,
        process: int | None = None,
        secret: str | bytes | bytearray = b"",
    ):
        self.device = _use_if_set_else(device, lambda: secrets.randbelow(2**32))
        self.process = _use_if_set_else(process, lambda: os.P_PID)
        self.secret = secret.encode() if isinstance(secret, str) else secret

        self._last_generated = 0
        self._generation_counter = 0

    def generate(self, identifier: int) -> int:
        return int.from_bytes(self.generate_bytes(identifier), byteorder=self.BYTE_ORDER)

    def generate_bytes(self, identifier: int) -> bytes | bytearray:
        tick = self.get_tick()
        self.update_counter(tick)

        flake = bytearray()
        flake.extend(identifier.to_bytes(self.IDENTIFIER_SIZE, self.BYTE_ORDER))
        flake.extend(self._generation_counter.to_bytes(self.COUNTER_SIZE, self.BYTE_ORDER))
        flake.extend(self.process.to_bytes(self.PROCESS_ID_SIZE, self.BYTE_ORDER))
        flake.extend(self.device.to_bytes(self.DEVICE_ID_SIZE, self.BYTE_ORDER))
        flake.extend(tick.to_bytes(self.TICK_SIZE, self.BYTE_ORDER))
        flake.extend(self.get_signature(flake))
        return flake

    def get_signature(self, flake: bytes | bytearray) -> bytes | bytearray:
        return hashlib.sha256(bytes((*flake, *self.secret))).digest()

    def get_tick(self) -> int:
        return int(time.time())

    def update_counter(self, tick: int):
        if tick == self._last_generated:
            self._generation_counter += 1

        else:
            self._last_generated = tick
            self._generation_counter = 0

    def validate(self, flake: int) -> bool:
        payload_size = self.COUNTER_SIZE + self.DEVICE_ID_SIZE + self.IDENTIFIER_SIZE + self.PROCESS_ID_SIZE + self.TICK_SIZE
        _flake = flake.to_bytes(payload_size + self.SIGNATURE_SIZE, self.BYTE_ORDER)
        payload = _flake[:payload_size]
        signature = _flake[payload_size:]
        return signature == self.get_signature(payload)
