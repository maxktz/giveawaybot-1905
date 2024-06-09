# ruff: noqa: S301
import pickle
from abc import ABC, abstractmethod
from typing import Any

import orjson


class AbstractSerializer(ABC):
    @abstractmethod
    def serialize(self, obj: Any) -> Any:
        "Support for serializing objects stored in Redis."

    @abstractmethod
    def deserialize(self, obj: Any) -> Any:
        "Support for deserializing objects stored in Redis."


class PickleSerializer(AbstractSerializer):
    "Serialize values using pickle."

    @staticmethod
    def serialize(obj: Any) -> bytes:
        return pickle.dumps(obj)

    @staticmethod
    def deserialize(obj: bytes) -> Any:
        "Deserialize values using pickle."
        return pickle.loads(obj)


class JSONSerializer(AbstractSerializer):
    "Serialize values using JSON."

    @staticmethod
    def serialize(obj: Any) -> bytes:
        return orjson.dumps(obj)

    @staticmethod
    def deserialize(obj: str) -> Any:
        "Deserialize values using JSON."
        return orjson.loads(obj)
