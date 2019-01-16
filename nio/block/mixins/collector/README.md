# Collector Mixin

Collect or buffer output signals in your block.

If you have a block that can potentially emit high-volume signal streams, it may be desirable to collect or buffer the output streams into lists rather than bombarding subsequent blocks. Including this mixin allows a block developer to add a configurable collection window to their block.

The mixin adds a `collect` property to the block that determines how long to collect signals for before notifying.

## Quick Usage

Include the `Collector` mixin in your block and notify signals like normal:

```python
from nio import Block, Signal
from nio.block.mixins import Collector

class MyBlock(Collector, Block):

    def start(self):
        super().start()
        self._job = Job(self._notify, timedelta(seconds=0.1, repeatable=True)

    def _notify(self):
        self.notify_signals([Signal()])

    def stop(self):
        self._job.cancel()
        super().stop()
```

## Parameters

 * Collect Timeout - How long to group signals. If set to 0 then no collection will occur, effectively disabling the mixin

## Timing

Imagine a block that is designed to notify 1 signal every second. Without this mixin, the notify timing would look like this, where `*` indicates a signal:
```
       [*]     [*]     [*]     [*]     [*]     [*]
|-------|-------|-------|-------|-------|-------|---
t=0     1       2       3       4       5       6
```

If we wanted to "slow the block down" without losing signals, we could add the `Collector` mixin and configure a collect timeout of 2 seconds. This would collect signals every 2 seconds and then notify. The block's timing would now start to look like this:

```
              [*,*]           [*,*]           [*,*]
|-------|-------|-------|-------|-------|-------|---
t=0     1       2       3       4       5       6
```

Notice that no signals got lost, they were just grouped together at a slower interval. 

It is also important to note that the collection timeout sets the notification timing of the block. This means that even though we are calling `notify_signals` every second in the block, the mixin is changing the notification timing to happen every time a collect window ends.

Imagine the same block that notified every second, but now with a collect timeout of 1.5 seconds. The block's timing now looks like this:
```
           [1]        [2,3]        [4]        [5,6]
|-------|-------|-------|-------|-------|-------|---
t=0     1       2       3       4       5       6
```

The signals have been numbered now to show the time that the notify was called from the block. Notice that the signal notified at the 1 second mark wasn't actually emitted from the block until the 1.5 second mark, when the collect window expired.
