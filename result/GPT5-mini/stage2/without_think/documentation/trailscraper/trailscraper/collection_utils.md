# `collection_utils.py`

## `trailscraper.collection_utils.consume` · *function*

## Summary:
Exhausts (fully iterates through) the provided iterable/iterator without retaining any of its items, causing any iteration-side effects to occur while using no additional memory to store elements.

## Description:
This utility drains an iterable or iterator by passing it to a zero-length collections.deque, which iterates through all items and immediately discards them. Common usage is to ensure any generator or iterator completes (thereby executing its side effects) when the caller does not need the yielded values.

Known callers within the codebase:
    - No internal callers were provided with the source for this task. Typical callers are pipeline or streaming cleanup code that needs to advance a generator to completion (for example, flushing remaining events, ensuring finalization code in a generator runs, or discarding remaining results stored in an iterator).

Why this logic is extracted:
    - The draining behavior is a single responsibility (exhaust an iterator for its side effects) that is useful at multiple call sites and benefits from a small, well-documented helper instead of repeating the deque idiom each time.
    - It emphasizes the intent ("consume the iterator") and hides the implementation detail (using collections.deque with maxlen=0) so callers don't need to remember the optimal memory-safe way to drain iterators.

## Args:
    iterator (iterable or iterator): Any object that supports iteration (an iterator, generator, or other iterable). The routine will obtain an iterator from this object (if it is not already an iterator) and iterate it to exhaustion.

    Notes on allowed values and interdependencies:
    - The argument may be any iterable; it need not already be an iterator. If it is an iterator, it will be advanced to its terminal state.
    - The function does not accept None; passing None will cause a TypeError when the function attempts to iterate.
    - Passing an infinite iterator will cause the call to never return (it will loop indefinitely).

## Returns:
    None

    Explanation:
    - The function does not return any value. Its purpose is side-effectful: to advance the given iterator to completion.
    - No sentinel or status is returned to indicate how many items were consumed.

## Raises:
    - TypeError: If the provided argument is not iterable (the underlying call to collections.deque will attempt to iterate and Python will raise TypeError).
    - Any exception raised while iterating the provided iterator (for example, user code inside a generator may raise ValueError, IOError, etc.) is propagated unchanged.

    Exact conditions:
    - If iterator does not implement the iterable protocol, the error originates from the attempt to get an iterator or iterate over it.
    - If the iterator's iteration logic raises an exception at any point, that exception propagates out of consume.

## Constraints:
    Preconditions:
    - The caller should ensure that draining the iterator is safe and desired (i.e., the iterator is finite or the caller is prepared to block indefinitely).
    - If the iterator performs I/O or expensive work on iteration, the caller must accept those side effects and costs.

    Postconditions:
    - If the function returns normally, the provided iterator (if it was an iterator object) is exhausted — subsequent attempts to iterate it yield no further items.
    - Any side effects performed by iteration have run to completion (assuming no exceptions occurred).

## Side Effects:
    - Iteration may trigger arbitrary side effects implemented by the iterator/generator (I/O, state mutation, logging, network calls, DB writes, etc.). Those side effects will be executed as the iterator is traversed.
    - No I/O or network calls are made by this function itself (it only causes the iterator to run).
    - No return value or global state is modified by this function directly; external state changes are only those performed by the iterator's own code.

## Control Flow:
flowchart TD
    Start --> CallDeque[Call collections.deque(iterator, maxlen=0)]
    CallDeque --> Iteration["deque consumes items by iterating\nloop: get next item -> discard"]
    Iteration -->|Iterator exhausted| End[Return None]
    Iteration -->|Iterator raises exception| Propagate[Propagate exception]
    Iteration -->|Infinite iterator| Hang[Loop forever (no return)]

## Examples:
    Example 1 — draining a finite generator for its side effects:
        def logger_generator():
            for i in range(3):
                print("side-effect", i)
                yield i

        # We only need the printing side-effects, not the values
        consume(logger_generator())
        # Prints:
        # side-effect 0
        # side-effect 1
        # side-effect 2

    Example 2 — handling exceptions raised during iteration:
        def faulty_gen():
            yield 1
            raise RuntimeError("failure during iteration")

        try:
            consume(faulty_gen())
        except RuntimeError as e:
            print("Iteration failed:", e)
        # Output: Iteration failed: failure during iteration

    Example 3 — caution with infinite iterators:
        import itertools
        # This will not return; it consumes items forever
        # consume(itertools.count())

