import json
from functools import wraps
from typing import Any

from pydantic import BaseModel
from vidi18n.common.redis import get_redis

redis = get_redis()


def subscribable(property_func):
    """
    A subscribable property will publish a message to Redis when it is updated.
    """
    key_name = property_func.__name__

    @wraps(property_func)
    def wrapper(self: "Data"):
        return self._event_keys.get(key_name, property_func(self))

    def setter(self: "Data", value):
        self._event_keys[key_name] = value

    return property(wrapper).setter(setter)


class Data(BaseModel):
    """
    Base model for data.
    * `uid` is the unique identifier for the data type
    * load it from Redis using ClassName.load(uid)
    * save it back again with instance.save()
    * remove it with instance.delete()
    * Use @subscribable as a decorator
    """

    uid: str
    _event_keys: dict[str, Any] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            field = self.__class__.__dict__.get(key)
            is_prop = type(field) == property
            if is_prop and hasattr(field, "setter"):
                setattr(self, key, value)

    @classmethod
    @property
    def type(cls):
        return cls.__name__.lower()

    def save(self, redis=redis):
        json_key = f"data:{self.type}:{self.uid}"
        my_data = self.model_dump_json()
        redis_data = redis.get(json_key)

        if redis_data != my_data:
            redis.set(f"data:{self.type}:{self.uid}", my_data)

        # save data and publish events
        for key, value in self._event_keys.items():
            field_key = self.field_key(key, self.uid)
            redis_data = redis.get(field_key)
            if redis_data != value:
                pubsub_key = self.field_key(key)
                redis.set(field_key, value)
                redis.publish(pubsub_key, field_key)

    @classmethod
    def load(cls, uid, redis=redis) -> "Data":
        data = redis.get(f"data:{cls.type}:{uid}")
        if data:
            data_dict = json.loads(data)
            data_dict["uid"] = uid
            return cls(**data_dict)

    def delete(self, redis=redis):
        item = self.__class__.load(self.uid)
        if item:
            redis.delete(f"data:{self.type}:{self.uid}")
            for key in self._event_keys.keys():
                redis.delete(f"data:{self.type}:event:{key}:{self.uid}")

    @classmethod
    def field_key(cls, key, uid="*"):
        return f"data:{cls.type}:event:{key}:{uid}"

    @classmethod
    def key_to_uid(cls, key: str) -> str:
        return key.split(":")[-1]
