import pickle
from typing import Any
from abc import ABC, abstractmethod

import orjson


class AbstractSerializer(ABC):
    @abstractmethod
    def serialize(self, obj: Any) -> Any:
        """Support for serializing objects stored in Redis."""

    @abstractmethod
    def deserialize(self, obj: Any) -> Any:
        """Support for deserializing objects stored in Redis."""


class PickleSerializer(AbstractSerializer):

    def serialize(self, obj: Any) -> bytes:
        return pickle.dumps(obj)

    def deserialize(self, obj: bytes) -> Any:
        return pickle.loads(obj)


class JSONSerializer(AbstractSerializer):

    def serialize(self, obj: Any) -> bytes:
        return orjson.dumps(obj)

    def deserialize(self, obj: str) -> Any:
        return orjson.loads(obj)