# GroupBy Mixin

Enhance your block to support grouping incoming signal lists.

It is often desirable to have a block perform the same operation independently on groups of signals. For example, a counter block could simply count the number of signals it receives. A better counter block could count groups of signals in the incoming lists. This opens up the possibility to many options such as counting posts per user, counting rain events per zip code, counting log messages by severity, etc.

The GroupBy mixin adds this ability to your blocks by adding a `Group By` parameter to the block's configuration.

## Quick Usage

Include the `GroupBy` mixin in your block's inheritance and implement `process_group_signals` instead of `process_signals`. 

```python
from nio import Block, Signal
from nio.block.mixins import GroupBy

class Counter(GroupBy, Block):
    
    def process_group_signals(self, signals, group, input_id=None):
        return Signal({
            "count": len(signals),
            "group": group
        })
```

This block will notify the count of every group of signals defined by the `Group By` parameter of the block.

## Parameters

* Group By - The value to group signals by. A hard-coded value essentially means the block will only operate on one group. It is better to set this to the value of a nio expression. See examples below.

## Reference

### process_group_signals

The easiest way to operate on a group of signals rather than the full list of incoming signals is to simply return results from the `process_group_signals` method. If you use this approach, do not define `process_signals`.

```python
def process_group_signals(self, signals, group, input_id=None)
```

* signals - The list of Signal objects that belong to this group
* group - The group that is currently being processed, i.e., the result of `self.group_by()`
* input_id - The ID the signals were processed on

Override this method and return an individual signal or a list of signals to return. The mixin will take care of concatenating the list of all signals from all groups for you.

### for_each_group

Sometimes a block's group by functionality is more complicated than can be wrapped in a single `process_group_signals` method. In these cases, it is better to have your block code call the `for_each_group` method to execute a function on every group of signals.

```python
def for_each_group(self, target, signals=None, *args, **kwargs)
```

* target - The target method to call. This method must have one of the following signatures, depending on how `for_each_group` was called
  * If signals were provided to `for_each_group` - the target method must have the list of signals be the first argument and the group name be the second argument. The target method will be called for every group that exists in the list of signals.
  * If no signals were provided to `for_each_group` or if signals is `None` - the target method must have the first argument be the group name. The target method will be called for every group that has ever been processed on the block.
  * Additional arguments and keyword arguments on methods are fine, and will be passed `*args` and `**kwargs` from the call of `for_each_group`
* signals - An optional list of signals to pass to each execution of the target method. If provided, the group name will be determined from the signals and the value of the group by block property
* *args/**kwargs - Additional arguments to pass to the target method

**Example:**

```python
from collections import defaultdict
from nio import Block, Signal
from nio.block.mixins import GroupBy

class BetterCounter(GroupBy, Block):
    
    def __init__(self):
        super().__init__()
        self._totals = defaultdict(int)
    
    def add_count(self, signals, group, extra_name=""):
        """ Add the current count of signals per group to the total """
        self._totals[group] += multiplier * len(signals)
        return Signal({
            "total": self._totals[group],
            "name": extra_name,
        })
        
    def process_signals(self, signals):
        """ Increment our totals when signals are processed """
        # We will call add_count on every group of incoming signals
        out_sigs = self.for_each_group(self.add_count, signals, extra_name="example")
        # Then notify the results
        self.notify_signals(out_sigs)
        
	def get_group_total(self, group):
        """ Get the current total for a group"""
        return self._totals[group]
    
    def get_current_totals(self):
        """ A method that can be called to retrieve all totals"""
        # totals would be a list of integer totals that we have
        # effectively the same as:  list(self._totals.values())
        totals = self.for_each_group(self.get_group_total)
```

### groups

A helper method to get the set of current groups that this block has processed

```python
def groups(self)
```

Returns: A set of all groups that this block has processed