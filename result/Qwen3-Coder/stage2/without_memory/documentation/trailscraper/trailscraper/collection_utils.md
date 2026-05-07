# `collection_utils.py`

## `trailscraper.collection_utils.consume` · *function*

## Summary:
Consumes an iterator by exhausting it completely without storing any elements.

## Description:
This function takes any iterable object and fully consumes it by converting it into a collections.deque with maxlen=0. This pattern efficiently drains the iterator while discarding all elements, making it useful for side-effect operations or when you need to ensure an iterator is fully processed without retaining any data.

## Args:
    iterator: Any iterable object that can be consumed (list, generator, iterator, etc.)

## Returns:
    None: This function does not return any meaningful value.

## Raises:
    TypeError: If the argument is not iterable.

## Constraints:
    Preconditions: The argument must be an iterable object.
    Postconditions: The iterator is fully exhausted and no elements are retained.

## Side Effects:
    None: This function has no side effects beyond consuming the input iterator.

## Control Flow:
```mermaid
flowchart TD
    A[consume(iterator)] --> B{iterator is iterable?}
    B -->|Yes| C[collections.deque(iterator, maxlen=0)]
    C --> D[Iterator exhausted]
    B -->|No| E[TypeError raised]
```

## Examples:
```python
# Consuming a generator
def my_generator():
    for i in range(3):
        yield i

gen = my_generator()
consume(gen)  # Generator is fully consumed

# Consuming a list
my_list = [1, 2, 3]
consume(my_list)  # List is consumed, but no return value

# Using with side-effect operations
def side_effect_func():
    print("Processing item")
    yield 1

consume(side_effect_func())  # Prints "Processing item" once
```

