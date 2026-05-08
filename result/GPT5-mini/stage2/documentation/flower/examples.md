# `examples`

## Tree:
examples/
└── tasks.py

## Role:
Provide a tiny set of single-purpose example helpers intended for documentation, tests, or simple demo code. Each exported function demonstrates a minimal behavior (pure computation, passthrough, deterministic failure, or blocking wait) so callers can use, mock, or replace them in examples and tests.

## Description:
Where and when this module is used:
- Imported by documentation examples, demo scripts, or tests that need trivial, deterministic task-like functions.
- Useful as stubs/mocks for background-task wiring or as minimal examples when demonstrating serialization, error handling, and blocking behavior.

Why these components are grouped:
- Cohesion: every exported function represents a minimal "task" concept — a single responsibility with no external dependencies outside the standard library.
- Layering: this module lives at the example/demo layer, intentionally lightweight so it can be used in many contexts (docs, tests, CI) without introducing third-party dependencies.

## Components:
- add(x: object, y: object) -> object
  - Compute and return the result of applying Python's binary + operator to two operands.
  - Component-level documentation: examples.tasks.add (detailed component doc available)
- echo(msg: Any) -> Any
  - Return the provided argument unchanged (simple passthrough).
  - Component-level documentation: MISSING (no stored component doc found); see "Implementation note" in Public API below.
- error(msg: Any) -> None (raises Exception)
  - Immediately raise Exception(msg); does not return normally.
  - Component-level documentation: examples.tasks.error (detailed component doc available)
- sleep(seconds: int | float) -> None
  - Block the calling thread for the given duration by delegating to time.sleep(seconds).
  - Component-level documentation: examples.tasks.sleep (detailed component doc available)

Mermaid dependency graph (internal relationships):
graph LR
    tasks_py[examples/tasks.py] --> add
    tasks_py --> echo
    tasks_py --> error
    tasks_py --> sleep
    %% Functions are independent; no internal call edges

## Public API:
- add(x: object, y: object) -> object
  - Summary: Compute and return x + y.
  - Behavior and constraints (from component doc):
    * x (object): left-hand operand. Any Python object for which x + y is valid at runtime.
    * y (object): right-hand operand. Any Python object compatible with x for the + operator.
    * Returns: object — the direct result of evaluating x + y (concrete type depends on operands).
    * Raises: TypeError if the operands are incompatible for addition; any exception raised by operand __add__ propagates unchanged.
  - Usage note: The function performs no validation or coercion; provide operands that make x + y valid.

- echo(msg: Any) -> Any
  - Summary: Identity/pass-through operation returning msg unchanged.
  - Implementation note (provisional — component-level doc missing):
    * Canonical implementation: def echo(msg): return msg
    * Accepts any object (None, primitives, containers, custom objects).
    * No side effects, no copying; returns the same object reference/value passed in.
    * Edge cases: If callers require a copy of a mutable input, they must copy before or after calling echo (echo does not copy).
  - Action item: Add a component-level documentation file for examples.tasks.echo to record exact signature and behavior; the above is an inferred, conventional implementation.

- error(msg: Any) -> None (raises Exception)
  - Summary: Unconditionally raise an Exception created with msg.
  - Behavior and constraints (from component doc):
    * msg (Any): message (typically a str) or object passed into Exception(msg).
    * Returns: None — the function does not return normally.
    * Raises: Exception(msg) always; callers must handle this exception if they expect to continue execution.
  - Usage note: Use to demonstrate failing tasks or to abort execution in examples.

- sleep(seconds: int | float) -> None
  - Summary: Block the current thread for the requested duration.
  - Behavior and constraints (from component doc):
    * seconds (int | float): duration in seconds. Accepts ints and floats (or objects convertible to float).
    * Returns: None after time.sleep completes.
    * Raises: Propagates exceptions from time.sleep (e.g., ValueError for negative values, TypeError for invalid types, KeyboardInterrupt if interrupted).
  - Usage note: This is synchronous and blocking; in tests, patch time.sleep to avoid delays.

## Dependencies:
Internal (other repo modules):
- None required; functions are standalone within examples/tasks.py.

External (standard library):
- time
  - Purpose: used by sleep(seconds) to call time.sleep(seconds).

## Constraints:
- Thread-safety:
  - add and echo are pure/stateless and safe to call concurrently from multiple threads.
  - error raises immediately and has no shared mutable state.
  - sleep blocks the calling thread — avoid using it on event-loop threads or where responsiveness is required.

- Ordering / initialization:
  - No initialization required; functions are ready to call after import.

- Caller responsibilities:
  - For add: provide operands compatible with Python's +; the function performs no type conversion.
  - For sleep: pass a numeric seconds value; negative values typically raise ValueError at time.sleep.
  - For echo: do not assume it returns a deep copy of mutable inputs.
  - For error: be prepared to catch Exception if continued execution is desired.

## Public usage examples:
- Importing:
    from examples.tasks import add, echo, error, sleep

- add:
    result = add(2, 3)  # -> 5

- echo:
    value = echo({"k": "v"})  # returns the same dict object

- error:
    try:
        error("failure")
    except Exception as e:
        # e.args[0] == "failure"
        pass

- sleep:
    sleep(0.5)  # blocks current thread for ~0.5 seconds

## Maintenance notes:
- Maintain component-level documentation for echo to match the level of detail present for add, error, and sleep.
- Tests should patch time.sleep when exercising sleep to avoid slow tests.
- Keep these helpers minimal and side-effect-free; prefer adding wrappers for logging/metrics instead of changing these functions directly.

---

## Files

- [`tasks.py`](examples/tasks.md)

