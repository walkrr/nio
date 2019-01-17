# Retry Mixin

Retry failed operations using different backoff strategies

If your block performs an operation that has a chance of failure like an HTTP API call or a database query, it is often more resilient to retry those operations. The Retry mixin allows you to define retry options as block parameters.

## Quick Example

Include the mixin in your block's inheritance and call the `execute_with_retry` method around the code which has a chance of failing.

```python
from nio import Block
from nio.block.mixins import Retry

class HTTPCall(Retry, Block):
    
	def make_http_call(self, url):
        # Make http request here, raise on failure
        
    def process_signal(self, signal):
        self.execute_with_retry(self.make_http_call, url="http://url.com")
```

This example will make an HTTP call when incoming signals are processed. If that HTTP call fails it will retry based on the retry parameters configured on the block.

## Parameters

* strategy (select): A choice of pre-configured backoff strategies
* max_retry (int): The maximum number of retries to attempt. 
  * Note that this is based on retry number, not retry duration. 
  * Setting it to 0 means that no retries will be attempted. 
  * Setting it to a negative number means that there is no maximum. 
  * Also note that this property works in concert with the indefinite flag. If that flag is set to True, then the retry duration for the retry number specified in `max_retry` will be retried indefinitely.
* multiplier (float): This property has slightly different meanings based on what strategy is being used, but for the most part, it allows you to control how much time will elapse between retries. The higher the number, the longer amount of time that will elapse between each retry attempt.
* indefinite (bool): Set to True if you wish for the `max_retry` retry attempt to be continued indefinitely. For example, if this is `true` and `max_retry` is 5, then the 5th retry will continue to be retried until the retry is successful or the block is stopped. If this flag is set to `false`, the retry mixin will stop retrying once the `max_retry` retry attempt is reached.

## Reference

### execute_with_retry

The main method of this mixin is the `execute_with_retry` method, which should be called when performing an operation that could fail.

```python
def execute_with_retry(self, execute_method, *args, stop_retry_event=None, **kwargs)
```

* execute_method - The method to call and retry if it fails. If this method raises an exception it is considered to have failed
* stop_retry_event - An optional `Event` to include that will be `set()` when the mixin has stopped retrying. Useful for logging messages or taking action when the block knows that the request will never succeed
* *args/**kwargs - Additional arguments to pass to `execute_method`
* Returns: The `execute_with_retry` method returns the results of the `execute_method` once it succeeds, or raises the exception the `execute_method` raises if it gives up retrying.

### before_retry

The block developer can also implement some custom behavior in their block that will happen before the next retry. This can be done by overriding the `before_retry` method. This is a useful place to do things like close and reopen connections or take other actions that can sometimes remedy the reason the failures occur.

```python
def before_retry(self, *args, **kwargs)
```

* *args/**kwargs - The arguments from the original `execute_method` being called in `execute_with_retry`.

### Backoff Strategies

Block developers can implement their own backoff strategies and employ those instead by overriding the setup_backoff_strategy method.