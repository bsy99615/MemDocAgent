# `progress_bar.py`

## `src.ydata_profiling.utils.progress_bar.progress` · *function*

## Summary:
Wraps a callable to update a tqdm progress bar: sets the bar's postfix message before calling the callable, then advances the bar by one step after the callable returns, returning the callable's result.

## Description:
This function returns a wrapper around an existing callable that integrates simple progress reporting using a tqdm progress bar. The wrapper performs three responsibilities in order:
1. Set the progress bar's postfix to the provided message (bar.set_postfix_str).
2. Invoke the underlying callable with the original positional and keyword arguments.
3. Advance the progress bar by one step (bar.update) if the callable completes successfully.

Known callers within the codebase:
- No direct call sites were discovered in the scanned context for this documentation generation. Typical callers are functions that process items in a loop (e.g., per-row/column processing during profiling, or per-task workers) and wish to update a shared tqdm progress bar after each processed item.

Why this is extracted into a separate utility:
- Responsibility boundary: encapsulates the common pattern "show a message and increment a shared progress bar around the execution of a work function". Extracting it avoids repeating progress bar bookkeeping at every call site, preserves the wrapped function's signature (via functools.wraps), and centralizes behavior such as when the bar is updated relative to the wrapped function's execution.

## Args:
    fn (Callable): The function or callable to wrap. It will be called with the same positional and keyword arguments that the wrapper receives.
    bar (tqdm): A tqdm progress bar instance that supports set_postfix_str(str) and update(n: int = 1). The function assumes bar is already constructed (for example, tqdm(total=N)).
    message (str): Text displayed as the bar's postfix for this invocation. This is set on the bar immediately before calling `fn`.

Notes on interdependencies:
- The wrapper assumes `bar` exposes the methods set_postfix_str and update. If `bar` does not provide these methods, an AttributeError will result at runtime.
- `message` is used only to set the bar postfix and has no effect on the wrapped callable's inputs or outputs.

## Returns:
    Callable: A callable (the wrapper) that accepts any positional and keyword arguments and:
      - Calls `fn(*args, **kwargs)`.
      - If `fn` returns normally, increments `bar` by one (calls bar.update()) and returns the original return value from `fn`.
      - If `fn` raises, the exception propagates to the caller and the bar is not advanced by this wrapper.

All possible return behaviors:
- Normal return: the wrapper returns whatever `fn` returns.
- Exceptional return: if `fn` raises any exception, it is propagated unchanged (no suppression) and bar.update() is not called by this wrapper.

## Raises:
    AttributeError: If `bar` does not implement set_postfix_str or update and those attribute lookups are attempted.
    Any exception raised by `fn`: propagated unchanged. The wrapper does not catch or translate exceptions from `fn`.

## Constraints:
Preconditions:
- `fn` must be a callable.
- `bar` must be a valid tqdm-like progress bar object with the methods:
    - set_postfix_str(message: str)
    - update(n: int = 1)
- `message` must be a string (or convertible to string) appropriate for display in the bar postfix.

Postconditions (guarantees after a successful call of the wrapper):
- The bar's postfix has been set to `message` at the time `fn` was executing.
- If `fn` completed successfully, the bar's progress has been incremented by one (bar.update called once).
- The wrapper returns the exact value returned by `fn`.

What is NOT guaranteed:
- If `fn` raises an exception, the bar will not be advanced by this wrapper.
- The wrapper does not restore a previous postfix value after completion; the bar's postfix remains set to `message`.

## Side Effects:
- Mutates state of the provided `bar` by:
    - Calling bar.set_postfix_str(message) (mutates bar's displayed postfix).
    - Calling bar.update() upon normal completion (increments progress).
- No file, network, database, or global-variable side effects are performed by this utility itself beyond the bar mutation.
- No additional logging or I/O is performed by this function.

## Control Flow:
flowchart TD
    Start --> SetPostfix[Set bar.postfix = message]
    SetPostfix --> CallFn[Call fn(*args, **kwargs)]
    CallFn --> FnSuccess{fn returned or raised?}
    FnSuccess -->|returned| UpdateBar[bar.update()]
    UpdateBar --> ReturnResult[Return fn result]
    CallFn -->|raised| PropagateError[Propagate exception to caller]
    PropagateError --> End

(Interpretation: the postfix is set before calling fn. If fn returns normally, the bar is updated and the wrapper returns fn's result. If fn raises, the exception propagates and the wrapper does not call update.)

## Examples (described usage; not raw code):
1. Simple per-item processing
   - Create a tqdm progress bar with a known total equal to the number of items to process.
   - Define a function that processes a single item and returns a result.
   - Wrap that function with this utility, passing the shared bar and a short message like "Processing item".
   - For each item in the input iterable, call the wrapped function. After each successful call, the bar will display the message and advance by one.
   - If a processing call raises an exception, that exception will propagate and the bar will not advance for that item.

2. Error handling considerations
   - If you need the progress bar to advance even when the work function raises, handle exceptions inside the work function or use a wrapper that updates the bar in a finally block (i.e., ensure update happens regardless of exceptions). This utility intentionally updates only after successful completion so it reflects completed work accurately.

3. Decorating vs. manual wrapping
   - This utility returns a callable that preserves the wrapped function's metadata. It can be used either as an explicit wrapper factory (pass the function to `progress` and call the returned wrapper) or applied programmatically where functions are created/registered. It is not implemented as a decorator factory that returns a decorator with parameters — instead it takes the target function, the bar, and the message directly and returns the instrumented callable.

Implementation notes for reimplementation:
- Use functools.wraps(fn) to preserve function metadata (name, docstring).
- Call bar.set_postfix_str(message) before invoking fn.
- Call bar.update() only after fn returns successfully.
- Do not catch exceptions from fn; let them propagate.

