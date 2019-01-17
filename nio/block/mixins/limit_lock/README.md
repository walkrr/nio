# LimitLock Mixin

Safely lock certain resources on incoming signals without blowing up memory.

If a block has a non-thread safe operation like opening a connection to a port, it is useful to place a Python `Lock` object in your block to make sure that two, asynchronous signals do not trigger the operation at the same time. 

However, sometimes this can cause blocking and memory to fill up the call stack queue if an operation will never complete or is taking longer than the incoming signal rate. The LimitLock mixin provides a method, `execute_with_lock` that locks a method call across threads but only allows a certain number of callers to wait for the lock to free.

## Quick Example

Include the mixin in your block's inheritance and call the `execute_with_lock` method around the code you wish to lock

```python
from nio import Block
from nio.block.mixins import LimitLock

class MyBlock(LimitLock, Block):
    
    def listen_on_port(self, port_no):
        # do something here like open a port
        
    def process_signal(self, signal):
        self.execute_with_lock(self.listen_on_port, 5, 5000)
```

This example has a method that opens a port, something only one thread can do at a time. If more than 5 threads try to grab the lock then a warning will be logged and an exception will be thrown.

## Reference

### execute_with_lock

Call a method once a lock frees but don't allow more than a certain number of threads to try to grab the lock. This method will block until the lock is acquired.

```python
def execute_with_lock(self, execute_method, max_locks, *args, **kwargs)
```

* execute_method - The method to execute once the lock has been acquired
* max_locks - int - The maximum number of threads allowed to wait for a lock at a time
* *args/**kwargs - additional arguments that will get passed to the execute method

Returns: The result of execute_method once it has run

Raises: `LockQueueFull` if there are too many threads trying to acquire the lock