# `collection_utils.py`

## `trailscraper.collection_utils.consume` · *function*

## Summary:
Consumes an iterator by exhausting it without storing any elements.

## Description:
This function takes any iterable object and fully consumes it, discarding all elements. It uses the collections.deque constructor with maxlen=0 as an efficient way to iterate through the entire iterator without storing any values in memory. This pattern is commonly used when you need to process an iterator for its side effects but don't need to retain the results.

## Args:
    iterator: Any iterable object that can be consumed (list, generator, iterator, etc.)

## Returns:
    None: This function doesn't return anything meaningful, as its sole purpose is to consume the iterator.

## Raises:
    No exceptions are explicitly raised by this function. However, if the iterator raises an exception during iteration, it will propagate up normally.

## Constraints:
    Preconditions:
    - The input must be an iterable object
    - The iterator should be consumable (not infinite in a way that causes resource exhaustion)
    
    Postconditions:
    - The iterator is fully exhausted
    - No elements from the iterator are retained in memory

## Side Effects:
    None: This function has no side effects beyond consuming the input iterator.

## Control Flow:
```mermaid
flowchart TD
    A[consume(iterator)] --> B{Create deque with maxlen=0}
    B --> C{Iterate through iterator}
    C --> D{Discard all elements}
    D --> E[Iterator exhausted]
```

## Examples:
```python
# Basic usage with a list
numbers = [1, 2, 3, 4, 5]
consume(numbers)  # Consumes the list, no return value

# Usage with a generator
def number_generator():
    for i in range(3):
        yield i * 2

consume(number_generator())  # Consumes the generator

# Usage with a file iterator
with open('file.txt') as f:
    consume(f)  # Consumes all lines from the file
```

