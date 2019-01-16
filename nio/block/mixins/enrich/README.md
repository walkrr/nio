# EnrichSignals Mixin

Enrich incoming signals with new attributes.

When a block creates some new data based on an incoming signal there are a few different ways to emit that data in an outgoing signal. The data can be its own signal, it can be merged with the incoming signal, or it can be added to the incoming signal as an attribute. The EnrichSignals mixin takes away this complexity for the block developer and instead lets the service designer make the decision on how the data should be produced.

## Quick Usage

Include the `EnrichSignals` mixin in your block inheritance and then notify the results of `get_output_signal()`. 

```python
from nio import Block
from nio.block.mixins import EnrichSignals 

class MyBlock(EnrichSignals, Block):
    
    def process_signal(self, signal):
        outgoing_data = {"key": "value"}
        return self.get_output_signal(outgoing_data, signal)
```

This example will allow the service designer to decide how to best represent the data from the block (`{"key": "value"}`) in the outgoing signals from the block.

## Properties

All properties will be nested in an advanced property on the block called "Signal Enrichment"

* Exclude existing? - boolean - whether to exclude the incoming data on outgoing signals
* Results field - string - The name of the signal attribute to put the new data on

## Modes of Use

### Signal Data Replacement

Discard all incoming signal data and only notify the new data from the block. This is the default behavior of the mixin.

* Exclude existing? - `true`
* Results field - any/ignored

### Signal Data Merge

Merge the new data into the incoming signal data.

* Exclude existing? - `false`
* Results field - empty string (`""`)

### New Signal Attribute

Place the new data onto the incoming signal with on a given attribute

* Exclude existing? - `false`
* Results field - the name of the attribute

### Examples

For all of these examples, assume the block code is notifying a signal returned by `self.get_output_signal({"new key": "new val"}, incoming_signal)`

| Block Config                                                 | Incoming Signal                                              | Outgoing Signal                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| exclude existing: `true`<br />results field: `""`            | {"old_key": "old val"}                                       | {<br />"new key", "new val"<br />}                           |
| exclude existing: `false`<br />results field: `""`           | {"old_key": "old val"}                                       | {<br />"old_key": "old val",<br />"new key", "new val"<br />} |
| exclude existing: `false`<br />results field: `"attr"`       | {"old_key": "old val"}                                       | {<br />"old_key": "old val",<br />"attr": {"new key", "new val"}<br />} |
| exclude existing: `false`<br />results field: `""`<br />_(merge overwrite)_ | {<br />"old_key": "old val",<br />"new_key": "other val"<br />} | {<br />"old_key": "old val",<br />"new key", "new val"<br />} |

## Reference

The mixin exposes two methods to use in your block

### get_output_signal

Get an output signal based on the block's configuration of how to merge in some data

```python
def get_output_signal(self, signal_data, incoming_signal copy=True)
```

* signal_data (dict) - This is a required dictionary of the new data to merge on the signal
* incoming_signal (Signal) - The original incoming signal
* copy (bool) - defaults to `True` - whether to make a copy of the incoming signal. This will normally be true unless you want to overwrite references to the actual incoming signal when performing the merge.
* _returns:_ Signal - An outgoing signal with the `signal_data` merged in per the block's configuration

### notify_output_signals

A helper method to notify a list of signals after properly enriching them

```python
def notify_output_signals(self, signals_data, incoming_signal, copy=True, output_id=None)
```

* signals_data (dict/list) - Data about the output signals. If this is a list, it will be assumed to be a list of dictionaries whose corresponding Signals will be notified in a batch. Otherwise, it should be a single dict containing the signal data to notify.
* incoming_signal (Signal) - The original incoming signal
* copy (bool) - defaults to `True` - whether to make a copy of the incoming signal. This will normally be true unless you want to overwrite references to the actual incoming signal when performing the merge.
* output_id (str) - The output ID of the block to notify on. If not included then the default output ID will be used.
* _returns:_ None - it just notifies the signals