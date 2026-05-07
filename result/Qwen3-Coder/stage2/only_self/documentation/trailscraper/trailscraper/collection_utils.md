# `collection_utils.py`

## `trailscraper.collection_utils.consume` · *function*

## Summary:
Consumes an iterator by fully exhausting it without retaining any elements.

## Description:
This function efficiently drains an iterator by converting it into a collections.deque with maxlen=0. This is a well-established Python idiom for consuming iterators when the actual values are not needed. The function is commonly used when you want to process an iterator for its side effects (such as triggering lazy evaluations, consuming generators, or processing items for their side effects) but don't care about the returned values.

## Args:
    iterator: Any iterable object that can be consumed (list, generator, etc.)

## Returns:
    None: This function returns None as it's designed purely for its side effect of consuming the iterator.

## Raises:
    TypeError: If the argument is not iterable.

## Constraints:
    Preconditions: The argument must be an iterable object.
    Postconditions: All elements from the iterator have been consumed and discarded.

## Side Effects:
    None: This function has no side effects beyond consuming the iterator.

## Control Flow:
```mermaid
flowchart TD
    A[consume(iterator)] --> B{Create deque with maxlen=0}
    B --> C[Iterator elements consumed]
    C --> D[Elements discarded due to maxlen=0]
    D --> E[Return None]
```

## Examples:
```python
# Example 1: Consuming a generator to trigger side effects
def process_items():
    for i in range(3):
        print(f"Processing item {i}")
        yield i

# Consume the generator to trigger printing but discard results
consume(process_items())

# Example 2: Consuming a list to avoid keeping references
my_list = [1, 2, 3, 4]
consume(my_list)  # Efficiently consume without storing values

# Example 3: Consuming a range for side effects
def side_effect_func(x):
    print(f"Side effect with {x}")
    return x * 2

# Process range items for side effects only
consume(side_effect_func(x) for x in range(3))
```

