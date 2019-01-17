# Persistence Mixin

Use this mixin in your blocks to save internal block state across service and instance restarts.

## Quick Example

The following block will have it's value of `self._counter` saved and re-loaded when the service or instance gets restarted.

```python
from nio import Block
from nio.block.mixins import Persistence

class Counter(Persistence, Block):

    def __init__(self):
        self._counter = 0
        
    def persisted_values(self):
        return ["_counter"]
        
    def process_signals(self, signals):
        self._counter += len(signals)
```

## Mixin Behavior

The Persistence mixin is designed to periodically persist important block data while a service is running and also when the service is stopped.

The mixin will add an advanced block property called `backup_interval` that defines how often while a service is running the data should be saved.

The mixin will also add an advanced checkbox property called `load_from_persistence`. When checked, this means the block will load values from persistence when a service starts. Note that even when the box is unchecked, the block will still save to persistence when the service is stopped and according to the backup interval. This setting only affects loading from persistence.

## Simple Override

The easiest way to make use of this mixin is to override the `persisted_values` method in your block. This method should return a list of the attributes of your block that you would like saved. Data from the block will be serialized and saved using the [`safepickle`](https://github.com/niolabs/safepickle) library. This library works well for simple data types. For more complex data saving see the [Custom Serialization section](#custom-serialization-override) below.

## Custom Serialization Override

If your block requires the persistence of more complex data you can define custom serialization and deserialization techniques by overriding the `persistence_serialize` and `persistence_deserialize` methods in your block.

Note that overriding either `persistence_serialize` or `persistence_deserialize` will take precedence over anything included in an overridden `persisted_values` method.

The `persistence_serialize` method will be called before saving data to persistence. It is expected to take any important data that the block needs saved and return a data structure that is able to be serialized.

The `persistence_deserialize` method will be called when the block configures (if configured to load from persistence). It will be passed the data from the persistence file. It is then expected to repopulate the block's state as needed.

### Example

```python
class Person():

    def __init__(self, name, age):
        self.name = name
        self.age = age
   
   
class PersistingBlock(Persistence, Block):

    def __init__(self):
        self._people = []
        
    def process_signals(self, signals):
        for signal in signals:
            self._people.append(Person(signal.name, signal.age))
        
    def persistence_serialize(self):
        return [{"name": p.name, "age": p.age} for p in self._people]
        
    def persistence_deserialize(self, data):
        for person in data:
            self._people.append(Person(person['name'], person['age']))
```
