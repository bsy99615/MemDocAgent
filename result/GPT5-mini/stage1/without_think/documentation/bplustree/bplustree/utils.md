# `utils.py`

## `bplustree.utils.pairwise` · *function*

## Summary:
Produces a lazy iterator of consecutive element pairs from the input iterable (first paired with second, second with third, etc.), yielding no pair if the input has fewer than two elements.

## Description:
This utility creates two independent iterators from the provided iterable, advances the second one by a single step, and returns a zip of the two so that iteration produces consecutive pairs (overlapping).

Known callers within the provided codebase snapshot:
- No direct callers were identified in the provided file-level context. Typical usage is from higher-level components that need to process or compare adjacent items in a sequence (for example, scanning a sorted list to find boundaries or detecting adjacent duplicates).

Why this is extracted into a separate function:
- The logic of producing overlapping consecutive pairs is a small, reusable primitive used by many algorithms. Extracting it keeps callers concise and avoids repeatedly implementing the tee/advance/zip pattern. It also centralizes any behavior-related notes (lazy evaluation, buffering) so callers can reason about performance and memory.

## Args:
    iterable (Iterable):
        Any Python iterable (e.g., list, tuple, generator, iterator, map object).
        - If a non-iterable is provided, underlying calls (itertools.tee) will raise a TypeError.
        - The function accepts both re-iterable sequences and one-shot iterators/generators. Behavior differs: for one-shot iterators, tee will internally buffer values as they are consumed by the returned iterator(s).

## Returns:
    An iterator (zip object) that yields 2-tuples (first, second), each containing two consecutive elements taken from the input iterable.
    - Type: Iterator[tuple[Any, Any]]
    - Examples of returned behavior:
        - For iterable = [] -> returns an iterator that yields nothing.
        - For iterable = [x] -> yields nothing (single-element).
        - For iterable = [x, y, z] -> yields (x, y), (y, z).
    - The returned object is lazy: pairs are produced as the consumer iterates. No full list of pairs is built in advance by this function.

## Raises:
    - TypeError: If the provided argument is not iterable, itertools.tee will raise a TypeError when attempting to create iterators.
    - Any exception raised during iteration of the input (for example, exceptions from a generator's body) will propagate to the consumer when the returned iterator is iterated.

## Constraints:
Preconditions:
    - The caller must provide an iterable object. Passing None or a non-iterable will lead to TypeError.
    - If the caller relies on low memory usage, they should ensure that the underlying iterable is not both very large and produced by a single-pass iterator that causes tee to buffer many items.

Postconditions:
    - The returned iterator will yield consecutive overlapping pairs until the shorter of the two tee'ed iterators is exhausted (i.e., until the original iterable has no further elements for the advanced iterator).
    - The original iterable object is not consumed at call time by this function beyond what itertools.tee performs; actual consumption occurs when the returned iterator is iterated.

## Side Effects:
    - No I/O (no file, network, or stdout operations) are performed.
    - No global mutable state is modified.
    - Resource side-effects:
        - itertools.tee may allocate internal buffers (in memory) to hold values from the underlying iterable. For single-pass iterators or generators, buffering can grow proportional to the maximum lag between the two tee'd iterators (here effectively the number of items retained until the trailing iterator catches up). For very large or infinite iterators, this can cause high memory usage if the consumer pattern causes buffering.

## Control Flow:
flowchart TD
    Start([Start]) --> CreateTees[/"call itertools.tee(iterable) -> (a,b)"/]
    CreateTees --> AdvanceB{"call next(b, None)"}
    AdvanceB --> ReturnZip[/return zip(a, b)/]
    ReturnZip --> Consumer[/"When consumer iterates:"/]
    Consumer --> GetPair{Are there >=2 remaining items?}
    GetPair -->|Yes| YieldPair[(yield (item_i, item_i+1))]
    YieldPair --> GetPair
    GetPair -->|No| End([End])

## Examples:
- Basic usage with a list:
    - Input: [1, 2, 3]
    - Result: iterator that yields (1, 2), (2, 3)
    - Illustration: converting to list => [(1, 2), (2, 3)]

- Using with a generator:
    - If you have a generator that yields values lazily, pairwise(generator) returns a lazy iterator over consecutive pairs. Beware: buffering can grow if the generator is single-pass and the consumer accesses pairs in a way that keeps the earlier tee reference behind the advanced one.

- Edge cases:
    - Empty iterable: yields nothing.
    - Single-element iterable: yields nothing.

- Example error handling when a non-iterable is passed:
    - If somebody calls pairwise(123) (an int), a TypeError will be raised; callers can catch it:
        try:
            pairs = pairwise(123)
            next(pairs)
        except TypeError:
            # handle incorrect-argument-type
            pass

Notes and performance tips:
    - For sequences that support random access (like lists or tuples) and small sizes, creating explicit pairs via indexing or slicing may be simpler and avoids tee buffering.
    - For very large or infinite iterables, prefer streaming consumers that iterate pairs as they are produced and avoid holding references that prevent tee's buffer from being released.

## `bplustree.utils.iter_slice` · *function*

## Summary:
Yields consecutive fixed-size slices from a bytes sequence along with a boolean that signals whether each yielded slice is the final chunk.

## Description:
This helper extracts successive contiguous byte slices of length n from a bytes object and yields each slice together with a flag that is True when that slice is the final slice (i.e., when there are no remaining bytes after it). It advances by n bytes between yielded slices and always returns slices using Python slicing semantics (which may be shorter than n for the last chunk).

Known callers within the provided context:
- No direct callers were present in the provided file context. Typical callers in this codebase are higher-level I/O or serialization routines that must process or persist a large bytes buffer in fixed-size pages/blocks (for example, B+ tree node serialization, page writers, or network/message chunkers).

Why this logic is extracted:
- It encapsulates the iteration semantics for chunking a bytes buffer and the "is-last-chunk" determination in one place so callers receive both the slice and an explicit end-of-data signal. Extracting this avoids duplicating the index arithmetic and last-chunk logic wherever fixed-size chunking is needed.

## Args:
    iterable (bytes): The byte sequence to slice into chunks. The function uses len(iterable) and iterable[start:stop], so the argument must support these operations. Although typed as bytes, any sequence supporting len() and slicing will behave the same.
    n (int): Positive integer chunk size. Each yielded slice will be taken from current start to start + n (Python slicing). Must be > 0 (see Constraints); non-positive values lead to undefined or infinite behavior.

Interdependencies:
    - Both parameters are required. The correctness of iteration depends on n being a positive integer and iterable providing length and slicing.

## Returns:
Yields tuples of (chunk, is_last) where:
    chunk (bytes): A contiguous slice of the original iterable, produced by iterable[start:stop]. All yielded chunks except possibly the last will have length == n. The final chunk may have length in the range [1, n] (or 0 if the iterable is empty).
    is_last (bool): True when the yielded chunk is the final one (i.e., there are no remaining bytes after this chunk). Internally this value is computed as the updated start index (after advancing by n) being >= len(iterable). That makes is_last True for the last yielded slice and False otherwise.

Edge-case returns:
    - If iterable is empty, the generator yields nothing.
    - If len(iterable) is an exact multiple of n, the last yielded chunk will have length n and is_last will be True for that chunk.
    - If iterable length < n, a single chunk of length < n is yielded with is_last == True.

## Raises:
    - No exceptions are explicitly raised by this function.
    - Built-in operations used by the function may raise exceptions:
        * TypeError if the provided iterable does not support len() or slicing with integer indices.
        * Any exception that slicing or len() on the supplied object would normally raise will propagate to the caller.

## Constraints:
Preconditions:
    - n must be a positive integer (n > 0). If n <= 0, the loop's start/stop arithmetic will not progress correctly and may cause an infinite loop or repeated empty slices.
    - iterable must support len(iterable) and slicing with integer indices (iterable[start:stop]).

Postconditions:
    - After iteration completes, the concatenation of yielded chunks equals the original iterable (i.e., no bytes are dropped or repeated).
    - Each yielded chunk corresponds to a non-overlapping span of the original iterable and spans progress from index 0 in steps of n.
    - The final yielded chunk is marked with is_last == True.

## Side Effects:
    - This function has no I/O side effects.
    - It does not mutate the provided iterable or any external/global state.
    - It performs only pure computation and yields values to the caller.

## Control Flow:
flowchart TD
    Start --> Init[set start=0, stop=n, final_offset=len(iterable)]
    Init --> CheckStart{start >= final_offset?}
    CheckStart -- Yes --> End[break -> generator completes]
    CheckStart -- No --> Slice[rv = iterable[start:stop]]
    Slice --> Advance[set start = stop; set stop = start + n]
    Advance --> Yield[yield (rv, start >= final_offset)]
    Yield --> CheckStart

## Examples:
Example 1 — iterate over bytes in 4-byte chunks and handle last chunk:
    data = b"HelloWorld"  # length 10
    for chunk, is_last in iter_slice(data, 4):
        # chunk values: b'Hell', b'oWor', b'ld'
        # is_last values: False, False, True
        process(chunk)
        if is_last:
            finalize()

Example 2 — single short chunk when data shorter than n:
    data = b"abc"
    for chunk, is_last in iter_slice(data, 10):
        # yields one chunk b'abc' with is_last == True
        send(chunk)

Example 3 — error handling for invalid arguments:
    try:
        for chunk, is_last in iter_slice(None, 4):
            pass
    except TypeError:
        handle_invalid_input()

