import json
from functools import wraps
from typing import Any

from pydantic import BaseModel


# Mock a Redis client (You'd replace this with a real Redis client)
class FakeRedis:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value

    def delete(self, key):
        del self.data[key]


# Usage
redis = FakeRedis()


def subscribable(property_func):
    key_name = property_func.__name__

    @wraps(property_func)
    def wrapper(self: "Data"):
        return self._event_keys.get(key_name)

    def setter(self: "Data", value):
        self._event_keys[key_name] = value

    return property(wrapper).setter(setter)


class Data(BaseModel):
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

        for key, value in self._event_keys.items():
            field_key = f"data:{self.type}:{self.uid}:event:{key}"
            redis_data = redis.get(field_key)
            if redis_data != value:
                redis.set(field_key, value)

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
                redis.delete(f"data:{self.type}:{self.uid}:event:{key}")


class Special(Data):
    other_value: str

    @subscribable
    def magic(self):
        pass

    @subscribable
    def magic2(self):
        pass


model = Special(uid="1010101", other_value="cool", magic2="hmm")
model.magic = "uwot"
model.save()
print(model.magic, model.magic2)
print(redis.data)
print(model.model_dump_json())

print(Special.load(uid="1010101").model_dump_json())

model.delete()
print(redis.data)
