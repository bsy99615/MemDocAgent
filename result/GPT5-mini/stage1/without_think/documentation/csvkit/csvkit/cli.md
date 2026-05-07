# `cli.py`

## `csvkit.cli.LazyFile` · *class*

## Summary:
A lightweight wrapper that defers opening/initialization of a file-like or iterator-producing resource until the first time it is used, delegating attribute access and iteration to the underlying resource.

## Description:
LazyFile is intended for scenarios where opening a file or creating a large/expensive resource should be delayed until actually needed (for example, when constructing CLI objects but not reading until processing starts). The class stores a callable (init) plus arguments and keyword arguments, and only calls init(*args, **kwargs) when a consumer requests an attribute or an item from the iterator.

Typical callers:
- CLI utilities that accept a filename or file factory but should avoid opening files during option parsing.
- Any code that wants to pass a file-like object into downstream code while deferring actual open/creation cost until use.

Motivation and responsibility:
- Encapsulates the "lazy open" behavior so callers do not need to manage the open-on-demand pattern themselves.
- Responsibility is limited to: storing the init callable and args, invoking init on first use, delegating attribute access and iteration to the opened resource, and providing a close() to release the resource. It does not implement context manager protocols.

## State:
Attributes (public and internal):
- init (callable)
  - Type: callable
  - Description: The function or callable to produce the underlying resource (e.g., builtins.open, a factory function).
  - Constraint: Should be callable; if not callable, calls to open will raise TypeError when init is invoked.
- f (file-like object or iterator or None)
  - Type: object | None
  - Description: The live underlying resource returned by init; typically a file object or iterator. None until the resource is opened.
  - Valid values: None or the object returned by init.
- _is_lazy_opened (bool)
  - Type: bool
  - Description: Tracks whether init has been invoked and f is populated.
  - Invariant: _is_lazy_opened is True if and only if f is not None (after successful open). After close() both f is None and _is_lazy_opened is False.
- _lazy_args (tuple)
  - Type: tuple
  - Description: Positional arguments saved for calling init.
  - Immutable once assigned in __init__.
- _lazy_kwargs (dict)
  - Type: dict
  - Description: Keyword arguments saved for calling init.
  - Immutable reference: the dict object is stored; callers should not rely on external mutation.

Class invariants:
- If _is_lazy_opened is True then f must be the object returned by calling init with the stored args/kwargs.
- If _is_lazy_opened is False then f must be None.
- After close(), the class must revert to an unopened state (f is None, _is_lazy_opened is False).

## Lifecycle:
Creation:
- Call signature: LazyFile(init, *args, **kwargs)
- Required: init (callable). *args and **kwargs are optional and will be passed to init when opening.
- No implicit opening occurs during construction; no file descriptors are opened at __init__ time.

Usage:
- Attribute access: Any attribute lookup not defined on LazyFile triggers __getattr__. This will call _open() and then forward the attribute access to the underlying f (e.g., read, readline, fileno, seek).
- Iteration: LazyFile is an iterator: __iter__ returns self, and __next__ triggers _open() and returns next(f) with null character removal (see below).
- Typical sequence:
  1. Instantiate LazyFile.
  2. Either call a method or access an attribute (e.g., .read(), .readline()) or iterate (for line in lazy_file: ...).
  3. The first access calls init(*_lazy_args, **_lazy_kwargs) and sets f.
  4. Use delegated methods/iteration on f.
  5. When finished, call close() to close the underlying resource (if opened).

Destruction / cleanup:
- Manual: call close() to close and release the underlying resource. close() checks whether the resource has been opened; if so it calls f.close(), sets f to None, and clears _is_lazy_opened.
- There is no __enter__/__exit__; LazyFile is NOT a context manager. To use in a with block, wrap the underlying resource directly or add your own context manager.

Important behavioral detail:
- __next__ returns next(self.f).replace('\0', ''), i.e., it removes any embedded null characters from the string returned by the underlying iterator. This assumes that next(self.f) returns a str (text). If the underlying iterator yields bytes, the .replace call will raise AttributeError/TypeError; callers should ensure init returns an iterator producing str when iteration is intended.

## Method Map:
Graph of key methods and their relationships (call flow):

mermaid
flowchart LR
    A[LazyFile.__init__] --> B{object created, unopened}
    B --> |attribute access| C[LazyFile.__getattr__]
    B --> |iteration starts| D[LazyFile.__next__]
    C --> E[LazyFile._open]
    D --> E
    E --> |if not opened| F[call init(*args,**kwargs) -> f]
    E --> |if already opened| G[no-op]
    F --> H[set _is_lazy_opened=True; assign f]
    C --> I[delegate attribute access to f]
    D --> J[next(f) and replace('\\0','')]
    K[close()] --> L[if opened -> f.close(); set f=None; _is_lazy_opened=False]

## Method behavior details:
- __init__(init, *args, **kwargs)
  - Stores init and arguments; does not call init.
  - No I/O side effects.

- __getattr__(name)
  - Calls _open() (which will call init if not already opened).
  - Returns getattr(self.f, name), i.e., delegates attribute access to the underlying resource.
  - Edge cases:
    - If init raises an exception (e.g., FileNotFoundError, OSError, or any user-defined exception), that exception propagates to the caller.
    - If the attribute does not exist on the underlying resource, AttributeError is raised by getattr(f, name).

- __iter__()
  - Returns self (iterator protocol). No side effects.

- __next__()
  - Calls _open(), then obtains next(self.f).
  - After retrieving the next item it returns item.replace('\0', '').
  - Typical use: iterating over a text file where each next(f) yields a str line.
  - Edge cases:
    - If f's iterator is exhausted, underlying StopIteration propagates normally.
    - If next(f) returns a non-str type (e.g., bytes), calling .replace('\0', '') may raise AttributeError/TypeError.

- _open()
  - If not already opened, calls f = init(*_lazy_args, **_lazy_kwargs) and sets _is_lazy_opened True.
  - If init returns None or an unexpected type, f will be set to that return value and subsequent calls will behave accordingly (possibly raising errors).
  - Exceptions from the init callable are propagated directly; _is_lazy_opened remains False in that case.

- close()
  - If _is_lazy_opened is True: calls f.close(), sets f to None, sets _is_lazy_opened to False.
  - If not opened, close() is a no-op.
  - Note: If f does not have a close() method, close() will raise AttributeError coming from f.close().

## Raises:
- __init__
  - Does not explicitly raise, but if the caller passes a non-callable as init, no error is raised until the first use. At that point, calling init(...) will raise TypeError.

- _open / __getattr__ / __next__
  - Any exception raised by the init callable (e.g., FileNotFoundError, PermissionError, OSError) will propagate to the caller.
  - AttributeError if delegating an attribute that doesn't exist on the underlying resource.
  - StopIteration from __next__ when the underlying iterator is exhausted (normal iterator termination).
  - TypeError/AttributeError in __next__ if the item returned by next(f) is not a str and thus has no .replace method.

- close()
  - If f does not provide close(), an AttributeError will be raised when trying to call f.close().

## Example:
- Creation:
    - Use a standard open function:
      lazy = LazyFile(open, 'data.csv', 'r', encoding='utf-8')
    - Creation does not open the file.

- First use (opens lazily):
    - Read a line:
      first_line = lazy.readline()  # triggers open -> delegates to file.readline()

    - Iterate:
      for line in lazy:
          # on first iteration init() is called, subsequent iterations use the opened file
          process(line)

- Cleanup:
    - Always close when finished:
      lazy.close()

- Notes:
    - Because LazyFile is not a context manager, do not use "with LazyFile(...)" unless you wrap it. For guaranteed cleanup, call close() in a finally block.
    - Ensure the init callable produces str lines (text mode) if you plan to iterate; otherwise __next__ may error.

### `csvkit.cli.LazyFile.__init__` · *method*

## Summary:
Stores a callable and its arguments on the instance so that the actual file-like object is created later; initializes internal flags and placeholders used by the lazy-open mechanism.

## Description:
This initializer makes the construction of the LazyFile instance side-effect free by recording only the factory (init) and the arguments required to create the underlying file-like resource. It does not open or allocate the resource. The actual opening is performed later by the instance method _open, which is invoked by __getattr__ and __next__ when the wrapper is first accessed or iterated.

Lifecycle and trigger points:
- The instance is created with the factory and arguments and may be held or passed around without performing I/O.
- The underlying resource is created when one of the following occurs:
    * attribute access on the LazyFile instance (triggers __getattr__ -> _open)
    * iteration/consumption via next() on the instance (triggers __next__ -> _open)
- There is no separate public "open" call implemented; opening is performed lazily on first use.

Why this exists as a separate initializer:
- Ensures initialization performs no I/O or heavy work.
- Centralizes and documents the lazy-open state setup so other methods (_open, __getattr__, __next__, close) can rely on consistent attributes.

## Args:
    init (callable): A callable to be invoked later to produce the underlying file-like object. The callable will be invoked as init(*self._lazy_args, **self._lazy_kwargs). The callable is expected to return an object supporting the operations the wrapper uses (attribute access, iteration/next, close), but no explicit interface check is performed here.
    *args (tuple): Positional arguments captured to forward to init when opening.
    **kwargs (dict): Keyword arguments captured to forward to init when opening.

## Returns:
    None

## Raises:
    None directly from __init__.
    - Errors related to the validity of `init` (for example, TypeError if `init` is not callable) or errors from creating the resource are raised later when _open is invoked, not during initialization.

## State Changes:
Attributes READ:
    - None

Attributes WRITTEN:
    - self.init: set to the provided init callable
    - self.f: set to None (placeholder for the lazily-created file-like object)
    - self._is_lazy_opened: set to False (flag indicating whether _open has been called successfully)
    - self._lazy_args: set to the tuple of provided positional arguments
    - self._lazy_kwargs: set to the dict of provided keyword arguments

## Constraints:
Preconditions:
    - No preconditions are enforced here; callers should ensure that `init` is a callable that accepts the provided arguments and returns a file-like object compatible with the wrapper's uses.

Postconditions:
    - After __init__ returns:
        * The instance holds references to the factory and its captured arguments.
        * No I/O has been performed and the flag `_is_lazy_opened` is False.
        * The instance is ready to lazily open the resource on first access.

## Side Effects:
    - None at initialization time. No file descriptors are opened, no external services are contacted, and no global state is modified by __init__.
    - Later side effects (opening files, allocating resources) occur only when _open is invoked by the wrapper's accessors.

### `csvkit.cli.LazyFile.__getattr__` · *method*

## Summary:
Delegates attribute access to the lazily-opened underlying file-like object, ensuring the file is opened first and returning the requested attribute from that underlying object.

## Description:
This method is invoked by Python's attribute lookup machinery when an attribute is not found on the LazyFile instance itself. On first such access it ensures the underlying resource is opened (by calling the instance's _open method) and then forwards the attribute lookup to the underlying object stored in self.f.

Known callers and context:
- Invoked implicitly by Python whenever code attempts to access an attribute that does not exist on the LazyFile instance (e.g., treating the LazyFile as a file-like object and calling read, readline, fileno, etc.).
- Used during the object's normal lifecycle when external code treats LazyFile as a proxy for the real file-like object; this supports lazy resource acquisition (opening only when actually needed).
- Not called for attributes defined directly on LazyFile (those are handled by normal attribute resolution).

Why this is a separate method:
- Centralizes the lazy-opening and delegation behavior in one place so that any attribute-based use of the proxy triggers opening exactly once and consistently forwards behavior to the underlying object. Inlining this logic everywhere callers might access attributes would be error-prone and duplicative.

## Args:
    name (str): The attribute name being accessed. Must be a valid Python attribute identifier.

## Returns:
    Any: The attribute value retrieved from the underlying object self.f. This may be:
        - a bound method (callable) if the underlying object exposes a method with that name,
        - a data attribute value,
        - a descriptor result as per Python's getattr semantics.
    Edge cases:
        - If init returns None (so self.f is None), getattr(None, name) will raise AttributeError.
        - If the underlying attribute exists but retrieving it triggers side effects (e.g., properties), those side effects occur as usual.

## Raises:
    AttributeError: If, after opening, the underlying object does not have the requested attribute (this is raised by getattr(self.f, name)).
    Any exception raised by the initializer (self.init) or by code executed during opening: propagated unchanged. For example, if self.init opens a file and that operation raises OSError, that exception propagates out of __getattr__.

## State Changes:
    Attributes READ:
        - self.init (used by _open to create the underlying object)
        - self._lazy_args (used by _open when calling init)
        - self._lazy_kwargs (used by _open when calling init)
        - self._is_lazy_opened (checked inside _open)
    Attributes WRITTEN:
        - self.f (set to the result of self.init(...) inside _open if not already opened)
        - self._is_lazy_opened (set to True inside _open when initialization occurs)

## Constraints:
    Preconditions:
        - The LazyFile instance must have been constructed such that self.init is a callable and self._lazy_args / self._lazy_kwargs contain the intended arguments for that callable.
        - __getattr__ is only invoked for attribute names not present on the LazyFile instance or its class.

    Postconditions:
        - After returning normally, if the underlying object had not been opened previously, self.f is set to the result of self.init(*self._lazy_args, **self._lazy_kwargs) and self._is_lazy_opened is True.
        - The returned value is equal to getattr(self.f, name) at the time of the call.

## Side Effects:
    - May perform I/O or other resource allocation because it calls self._open(), which invokes self.init(...) (for example, opening a file descriptor).
    - May raise and propagate any exceptions from self.init or from getattr on the underlying object.
    - Does not close or modify external objects beyond assigning self.f and flipping the _is_lazy_opened flag; however, the init callable itself may have arbitrary side effects.

### `csvkit.cli.LazyFile.__iter__` · *method*

## Summary:
Returns the same LazyFile instance so the object can act as its own iterator without opening the underlying file or changing internal state.

## Description:
Known callers and contexts:
- Python's iteration protocol (builtins.iter()), implicit calls from for-loops (for ... in ...), and any API that requests an iterator from an iterable (e.g., list(), tuple(), itertools functions). __iter__ is invoked at the start of an iteration lifecycle to obtain an iterator object; subsequent element retrieval is driven by __next__.
- This method is invoked when an external consumer requests an iterator; it does not initiate file access. Actual opening and reading of the underlying file are deferred to __next__ (which calls _open()).

Why separate:
- Keeping __iter__ trivial (returning self) preserves LazyFile's lazy-open semantics: the underlying file is not opened just by beginning iteration. Centralizing opening logic in _open()/__next__ avoids prematurely performing I/O and keeps iteration-start and first-element retrieval semantics distinct.

## Args:
None.

## Returns:
LazyFile
- Returns self (the same instance) so the object is its own iterator.
- Possible values: always returns the same LazyFile instance; it does not return a new iterator wrapper.

## Raises:
None directly.
- This method performs no operations that raise. Errors related to opening or reading the underlying file will occur later during __next__ when _open is called or when the underlying iterator yields/raises.

## State Changes:
Attributes READ:
- None. The implementation does not access any attributes or call other methods.

Attributes WRITTEN:
- None. The implementation does not modify any attributes.

## Constraints:
Preconditions:
- The LazyFile object must be a correctly constructed instance (its __init__ has executed). No other special preconditions are required to call __iter__.

Postconditions:
- The method returns self without side effects: _is_lazy_opened, f, _lazy_args, _lazy_kwargs, and init remain unchanged.
- Iteration state is not reset by this call. If the underlying file has been opened and partially/fully consumed, that position remains unchanged after __iter__ returns.

## Side Effects:
- None performed directly by this method: no I/O, no external calls, and no mutation of objects outside self.
- Indirect side effects can occur later during iteration because __next__ calls _open(), which performs I/O and mutates self.f and self._is_lazy_opened.

## Usage notes and edge cases:
- Because the object is its own iterator, calling iter(lazy_file) repeatedly returns the same object and does not create a fresh iterator. This means repeated for-loops over the same LazyFile instance will continue from the current position of the underlying file rather than restarting from the beginning.
- To re-read from the beginning, call close() on the LazyFile instance before iterating again; close() resets self._is_lazy_opened to False and self.f to None so the next __next__ will call _open() and obtain a fresh underlying file object from init.
- Example lifecycle (conceptual, not code): create LazyFile -> call iter() (returns self) -> first next() triggers _open() and begins I/O -> continue iterating until StopIteration -> optionally call close() to allow a fresh open for a new iteration.

### `csvkit.cli.LazyFile.close` · *method*

## Summary:
Closes the underlying lazily-opened file resource if it is currently open, and updates the object's state to reflect that no file is open.

## Description:
This method centralizes the logic required to tear down a lazily-opened file handle held by the LazyFile instance. It performs a guarded close: only when the internal flag indicates the file was opened lazily does it call close on the file object, clear the file reference, and mark the instance as no longer lazily opened.

Known callers and typical call context:
- Any code that manages LazyFile instances and is responsible for releasing file resources should call this method during cleanup (for example, at the end of a file-processing pipeline or when a command completes).
- It is also suitable to be invoked by resource-management wrappers (explicit cleanup blocks) that use LazyFile, ensuring a single place for the close logic.
- The method is designed to be called when the caller determines the file is no longer needed; it is not responsible for deciding that lifecycle—it only performs the safe close-and-reset operation.

Why this is a separate method:
- Centralizing close semantics avoids duplicating the guarded-close pattern (checking _is_lazy_opened, calling close, clearing state) throughout the codebase.
- Encapsulates the side effects (I/O close) and state mutations so callers need only call one method to release resources safely.

## Args:
    None

## Returns:
    None

## Raises:
    Propagates any exception raised by the underlying file object's close() call.
    - Typical exceptions that may surface include OSError (I/O errors) or AttributeError if the file-like object lacks a close attribute, but no exception is explicitly raised by this method itself; it simply forwards exceptions from the underlying call.

## State Changes:
Attributes READ:
    - self._is_lazy_opened
    - self.f

Attributes WRITTEN:
    - self.f (set to None when a close occurs)
    - self._is_lazy_opened (set to False when a close occurs)

## Constraints:
Preconditions:
    - The method may be called at any time; callers should expect it to be idempotent (calling it when no lazy-opened file exists has no effect).
    - If self._is_lazy_opened is True, then self.f is expected to be a file-like object with a close() method. If that is not the case, calling close may raise an exception from the underlying object.

Postconditions:
    - If self._is_lazy_opened was True at entry:
        * The underlying file object's close() will have been invoked (subject to any exceptions raised by that call).
        * self.f will be set to None.
        * self._is_lazy_opened will be set to False.
    - If self._is_lazy_opened was False at entry:
        * No changes are made (self.f and self._is_lazy_opened remain as they were).

## Side Effects:
    - Performs I/O by calling close() on the underlying file-like object (this typically releases file descriptors and flushes OS buffers).
    - May trigger exceptions coming from the underlying file close operation; such exceptions are propagated to the caller.
    - Mutates the LazyFile instance by clearing the file reference and updating the opened flag.

### `csvkit.cli.LazyFile.__next__` · *method*

## Summary:
Returns the next line from the lazily-created underlying file-like iterator, ensuring the file is opened before first use and removing any embedded NUL characters from the returned text. This advances the underlying iterator and may transition the LazyFile from unopened to opened state.

## Description:
Known callers and context:
- The Python iteration protocol: builtins.next(lazy_file) and for-loops (for line in lazy_file) call this method to retrieve successive items.
- Higher-level CSV reading or streaming pipelines that accept an iterator over text lines will indirectly call __next__ when consuming a LazyFile instance.
- Lifecycle stage: invoked during normal iteration over a LazyFile to fetch successive rows/lines. The first call triggers the lazy-opening of the underlying resource via _open().

Why this is a separate method:
- Encapsulates the iteration step and ensures the lazy-open semantics are preserved: the underlying resource is only created on first access. Keeping opening logic in _open and calling it from __next__ prevents premature I/O and centralizes resource creation and state toggling.

## Args:
None.

## Returns:
str
- A text string representing the next line/item yielded by the underlying iterator, with all NUL characters ('\0') removed.
- Normal (happy-path) return requires that the underlying iterator yields str objects; otherwise a TypeError or AttributeError may be raised when attempting to call .replace on the returned value.
- Edge-case: When the underlying iterator yields an empty string (''), this method returns '' (unchanged aside from NUL removal).

## Raises:
- StopIteration
    - Propagated when the underlying iterator self.f is exhausted (i.e., next(self.f) raises StopIteration). This signals end-of-iteration to the caller.
- Any exception raised by opening the resource:
    - Any exception raised by self.init(*self._lazy_args, **self._lazy_kwargs) (for example, FileNotFoundError, PermissionError, TypeError if init is not callable) will propagate. These occur during the call to _open().
- Any exception raised by the underlying iterator when producing the next item:
    - For example, IOError/OSError arising from reading the file, decoding errors if the iterator performs decoding, or other iterator-specific exceptions will propagate unchanged.
- AttributeError or TypeError
    - If next(self.f) returns a non-text object that does not support str.replace (for example, bytes or an object without replace), calling .replace('\0', '') will raise an AttributeError or TypeError; this will propagate to the caller.

## State Changes:
Attributes READ:
- self._is_lazy_opened (read indirectly by calling _open())
- self.init (read indirectly by calling _open() if a lazy open is needed)
- self._lazy_args (read indirectly by _open() when constructing the underlying resource)
- self._lazy_kwargs (read indirectly by _open())
- self.f (read by next(self.f))

Attributes WRITTEN:
- self.f (may be assigned by _open() to the newly-created underlying iterator/file object)
- self._is_lazy_opened (may be set to True by _open() when the resource is created)

Note: The reads/writes above include attributes accessed or modified by the delegated call to _open().

## Constraints:
Preconditions:
- The LazyFile instance must have been initialized so that:
    - self.init is a callable that accepts self._lazy_args and self._lazy_kwargs and returns an iterator or file-like object.
    - self._lazy_args and self._lazy_kwargs contain the arguments required by init.
- The underlying iterator that init returns is expected to yield text strings (str). If it yields bytes or other types, the call to .replace may fail.
- No prior call to close() is required; __next__ will open as needed.

Postconditions:
- If __next__ returns a string successfully:
    - self._is_lazy_opened is True (the underlying resource has been opened, either previously or during this call).
    - self.f references an open iterator/file-like object positioned immediately after the returned item.
    - The returned string contains no NUL characters (they have been replaced/removed).
- If __next__ raises an exception:
    - If the exception occurs during _open(), the object's lazy-open state will reflect whatever _open() did before the exception (commonly, _is_lazy_opened remains False if init failed before assignment, or True if assignment succeeded and a later operation failed).
    - If StopIteration is raised, the underlying iterator is at end-of-file; self.f remains whatever object _open() produced (if it produced one).

## Side Effects:
- I/O: May cause file I/O when _open() is invoked (init is executed), including opening file descriptors and performing initial read(s).
- Mutations outside self:
    - Consumes/advances the underlying iterator self.f by one item (this mutates f's internal position/state).
    - If the underlying iterator is a file or stream, its read pointer advances.
- No other global state (e.g., process-level settings) is modified by this method.

### `csvkit.cli.LazyFile._open` · *method*

## Summary:
Lazily initializes the underlying file-like object by calling the stored factory and marks the LazyFile as opened. If already opened, this method is a no-op.

## Description:
This method is invoked to perform the deferred (lazy) construction of the underlying file-like object. Known callers:
- __getattr__: triggered when an attribute not found on LazyFile is accessed; ensures the underlying file object exists before delegating attribute access.
- __next__: triggered when iteration requests the next item; ensures the underlying file object exists before reading from it.

Lifecycle/context:
- The LazyFile object is constructed with a factory callable (init) plus arguments. The actual file-like resource is created only when first needed (attribute access or iteration). _open encapsulates that creation step so the same logic is reused by multiple callers.

Why this method exists:
- To centralize and encapsulate the lazy-initialization behavior (call the factory with the stored args/kwargs and flip the opened flag). Placing this in a single method prevents duplicate initialization code in multiple places and makes the lazy-open semantics explicit and testable.

## Args:
    None

## Returns:
    None
    - Effect: After a successful call when the object was not previously opened, self.f is set to the value returned by the factory (self.init(...)) and self._is_lazy_opened is set to True.
    - Edge case: If the factory returns None, self.f will be None and the object is considered opened; subsequent operations will likely raise AttributeError or TypeError when attempting to use self.f.

## Raises:
    Any exception raised by the factory callable (self.init) or by argument evaluation when calling it.
    - Typical exceptions: OSError, FileNotFoundError, PermissionError, or other exceptions produced by the underlying open/read operations — these are propagated unchanged because _open does not catch them.
    - Condition: raised when the factory invocation fails (e.g., invalid path, permission denied, invalid arguments).

## State Changes:
    Attributes READ:
        - self._is_lazy_opened: checked to determine whether initialization is required
        - self.init: the factory callable used to construct the underlying object
        - self._lazy_args: positional arguments supplied to the factory
        - self._lazy_kwargs: keyword arguments supplied to the factory

    Attributes WRITTEN:
        - self.f: set to the return value of self.init(*self._lazy_args, **self._lazy_kwargs)
        - self._is_lazy_opened: set to True when initialization succeeds (or when the factory returns without raising)

## Constraints:
    Preconditions:
        - self.init must be a callable set at construction time (LazyFile.__init__ stores it).
        - self._lazy_args and self._lazy_kwargs must contain the intended parameters for the factory.
        - It is valid to call this method multiple times; callers should expect it to be idempotent when the file is already opened.

    Postconditions:
        - If self._is_lazy_opened was False prior to the call and the factory returns successfully, then:
            * self.f references the object returned by the factory.
            * self._is_lazy_opened is True.
        - If self._is_lazy_opened was already True, the method leaves self.f and self._is_lazy_opened unchanged.

## Side Effects:
    - Invokes the factory callable (self.init) which typically performs I/O (e.g., opening a file, creating a network or compressed stream); those external effects occur during this call.
    - May allocate resources (file descriptors, memory) and therefore may need matching cleanup (LazyFile.close should be used to release resources).
    - Exceptions from the factory propagate to the caller; there is no internal retry or fallback logic.

## `csvkit.cli.CSVKitUtility` · *class*

*No documentation generated.*

### `csvkit.cli.CSVKitUtility.__init__` · *method*

## Summary:
Prepare a CSVKitUtility instance for use by building and populating the CLI argument parser, parsing arguments, assigning the output destination, computing CSV reader/writer option dictionaries, and installing process-level handlers for uncaught exceptions and SIGPIPE. After this method returns the instance is configured and ready to run.

## Description:
Called during object construction (instantiation of a CSVKitUtility subclass) to perform initial configuration before any processing or IO occurs. Typical callers are CLI entry points and unit tests that instantiate concrete subclasses (for example, CSVLook, CSVStat, CSVCut). This method centralizes common initialization so subclasses need only supply additional arguments and main logic.

Why a separate initializer:
- Parsing and configuration are shared across many utilities; having this logic in __init__ ensures every subclass starts from the same, consistent state and avoids duplicating parser setup elsewhere.

Lifecycle context:
- Executed immediately when a utility object is created. After __init__ completes, other lifecycle methods such as run(), main(), or helper methods can safely read self.args, self.reader_kwargs, self.writer_kwargs, and self.output_file.

## Args:
    args (list[str] | tuple[str, ...] | None):
        - Command-line arguments to parse. If None (default), argparse will parse the current process arguments (sys.argv[1:]).
        - Must be an iterable of strings acceptable to argparse; otherwise argparse will raise (and may call SystemExit).
    output_file (io.TextIOBase | file-like object | None):
        - A writable text-mode file-like object used to write human-facing output (must implement write()).
        - If None, defaults to sys.stdout.

## Returns:
    None
    - As a constructor, it returns no value. Its effects are observable through instance attributes and global process handlers.

## Raises:
    SystemExit:
        - Raised indirectly by argparse.ArgumentParser.parse_args on parse errors or if a terminating action is triggered (for example, --help or --version).
    NotImplementedError:
        - Raised if the concrete subclass has not implemented add_arguments and the base class add_arguments is invoked.
    Any exception raised by helper methods:
        - Exceptions from _init_common_parser, _extract_csv_reader_kwargs, _extract_csv_writer_kwargs, or _install_exception_handler will propagate. The only exceptions this initializer swallows are ImportError and AttributeError raised while attempting to call signal.signal (these are ignored).

## State Changes:
Attributes READ:
    - self.description (str): used by _init_common_parser to set the ArgumentParser description.
    - self.epilog (str): used by _init_common_parser to set the ArgumentParser epilog.
    - self.override_flags (str or iterable): read by _init_common_parser to determine which common CLI flags to omit.

Attributes WRITTEN:
    - self.argparser (argparse.ArgumentParser): constructed and augmented with common and subclass-specific arguments.
    - self.args (argparse.Namespace): result of parsing the provided args.
    - self.output_file (file-like): assigned to output_file argument or sys.stdout when None.
    - self.reader_kwargs (dict): dictionary of CSV reader options returned by _extract_csv_reader_kwargs.
    - self.writer_kwargs (dict): dictionary of CSV writer options returned by _extract_csv_writer_kwargs.
Global process state modified:
    - sys.excepthook is replaced with the custom handler installed by _install_exception_handler.
    - If supported, the SIGPIPE handler is set to signal.SIG_DFL (default) to avoid noisy Python tracebacks on broken pipes.

## Constraints:
Preconditions:
    - The object is an instance of CSVKitUtility or a subclass.
    - Subclasses MUST override add_arguments (at class definition time) to add any utility-specific arguments; otherwise the base add_arguments will raise NotImplementedError when called during initialization.
    - If args is provided, it must be an iterable of strings acceptable to argparse.

Postconditions:
    - self.argparser exists and contains the common CLI options plus any subclass options added by add_arguments.
    - self.args is an argparse.Namespace populated with parsed values for all configured options.
    - self.output_file is set to a text-capable file-like object (sys.stdout if not provided).
    - self.reader_kwargs is a dict prepared for CSV reading routines. Typical keys (when present) include:
        - 'delimiter' (str)
        - 'quotechar' (str)
        - 'quoting' (int)
        - 'doublequote' (bool)
        - 'escapechar' (str)
        - 'field_size_limit' (int)
        - 'skipinitialspace' (bool)
        - 'header' (bool) — present if --no-header-row was used (header=False)
    - self.writer_kwargs is a dict prepared for CSV writing routines. Typical keys (when present) include:
        - 'line_numbers' (bool)
        - (subclasses such as CSVFormat may add 'delimiter', 'quotechar', 'quoting', 'doublequote', 'escapechar', 'lineterminator')
    - sys.excepthook is configured so uncaught exceptions are printed succinctly unless --verbose was set.

## Side Effects:
    - May trigger SystemExit via argparse when parse_args encounters errors or a terminating action (e.g., --help or --version).
    - Replaces sys.excepthook with a handler that prints short error messages unless --verbose was supplied.
    - Attempts to set the process SIGPIPE handler to the default (signal.SIG_DFL) using signal.signal; ImportError or AttributeError during this attempt are ignored (no signal change).
    - Does not open input files itself; input files are opened later by run()/_open_input_file as needed.

### `csvkit.cli.CSVKitUtility.add_arguments` · *method*

## Summary:
Provide subclass-specific command-line arguments by mutating the already-initialized argument parser; called during object construction to register the utility's CLI flags/options.

## Description:
Known callers and lifecycle stage:
    - Called directly in CSVKitUtility.__init__ immediately after _init_common_parser and before parsing arguments.
    - Lifecycle: during construction of a CSVKitUtility subclass instance, this method is invoked so the subclass can register its custom CLI options with the shared argument parser before parse_args is called.

Why this is a separate method:
    - Each concrete utility exposes distinct CLI flags. Keeping argument registration in an overridable method lets each subclass declare its own options cleanly without modifying the base class.
    - Separating this logic keeps _init_common_parser responsible only for shared/common arguments and centralizes per-command argument declarations in the subclass implementation.

## Args:
    None

## Returns:
    None

## Raises:
    NotImplementedError:
        - Raised unconditionally by the base implementation with the message:
          'add_arguments must be provided by each subclass of CSVKitUtility.'
        - This indicates that subclasses must override this method. If the base implementation is executed (i.e., a subclass does not override it), object construction will fail at __init__.

## State Changes:
    Attributes READ:
        - self.argparser: The method expects an argparse.ArgumentParser instance to already exist (created by _init_common_parser).
    Attributes WRITTEN:
        - self.argparser (mutated): Subclass implementations should call methods like self.argparser.add_argument(...) to register new arguments and may modify parser metadata (e.g., description, epilog) if required.

## Constraints:
    Preconditions:
        - self.argparser must be present and be an instance of argparse.ArgumentParser. The base class ensures this by calling _init_common_parser before add_arguments in __init__, so implementations may assume this precondition when invoked via the normal lifecycle.
        - Do not rely on self.args being populated; parse_args has not yet been called when add_arguments executes.
    Postconditions:
        - After a successful override of add_arguments, self.argparser will include any additional arguments/options required by the subclass. There is no return value; the parser is mutated in-place.
        - No parsing or validation of command-line arguments should occur in this method; parsing happens later in __init__ (self.args = self.argparser.parse_args(args)).

## Side Effects:
    - Mutates the state of self.argparser (registering new CLI options).
    - Should not perform I/O, start background threads, or parse command-line values. Any side effects beyond modifying the parser configuration (for example, creating files or network calls) are discouraged here because this method is invoked during object construction (before argument parsing and run-time behavior).

### `csvkit.cli.CSVKitUtility.run` · *method*

## Summary:
Open the configured input file (unless overridden), run the command's main logic while temporarily suppressing a specific agate warning, and ensure the input file is closed afterwards (unless file handling is overridden).

## Description:
Known callers and context:
- This method is intended to be invoked by the CLI runner after an instance of CSVKitUtility (or a subclass) has been constructed and configured with parsed arguments. Typical usage is the top-level CLI entrypoint which instantiates the utility and calls run() as the lifecycle step that starts command execution.
- It represents the runtime entry point for a csvkit command: set up input resources, execute the command logic, and perform cleanup.

Why this logic is a separate method:
- Encapsulates resource management (open/close of the input file) and warning-suppression concerns so subclasses only need to implement main() with the command-specific behavior.
- Centralizes the common pre/post-execution behavior for all CSVKitUtility-based commands, avoiding duplication across individual commands.

## Args:
    None

## Returns:
    None

## Raises:
    - Any exception raised by self._open_input_file(self.args.input_path) will propagate out of run(). This includes I/O-related exceptions thrown by the underlying file-open logic.
    - Any exception raised by self.main() will propagate out of run().
    - Edge-case: if self._open_input_file raises before assigning self.input_file, the finally block still attempts to close self.input_file (when 'f' not in self.override_flags). If self.input_file was not previously defined on the instance, accessing self.input_file in the finally block can raise AttributeError; this may mask or follow the original exception. Callers should be prepared for propagated exceptions from both the open and the cleanup path.

## State Changes:
Attributes READ:
    - self.override_flags: used to determine whether to open/close the input file ('f' flag suppresses file handling).
    - self.args.input_path: passed to _open_input_file to determine which file/stream to open.
    - getattr(self.args, 'no_header_row', None): checked to decide whether to suppress a specific agate warning.

Attributes WRITTEN:
    - self.input_file: set to the file/stream returned by _open_input_file when 'f' is not in self.override_flags. After run returns normally, the attribute will refer to the closed file object if file handling was performed.

## Constraints:
Preconditions:
    - self.override_flags must be present (typically a set or iterable containing flags).
    - self.args must be present and expected to have an input_path attribute. If a no_header_row flag is used, args may also hold no_header_row.
    - The instance should implement _open_input_file(path) and main().

Postconditions:
    - If run completes without raising and 'f' not in self.override_flags, the opened input file will have been closed before return.
    - If 'f' is in self.override_flags, run will not open or close self.input_file; caller is responsible for input resource management.
    - Any warnings about unspecified column names from agate are suppressed only for the duration of the main() invocation when args.no_header_row is truthy.

## Side Effects:
    - Opens a file or stream via self._open_input_file(self.args.input_path) (unless overridden by override_flags).
    - Temporarily modifies Python's warnings behavior within the with warnings.catch_warnings() context; specifically, it may call warnings.filterwarnings to ignore the "Column names not specified" message from the agate module when args.no_header_row is set.
    - Calls self.main(), which may perform arbitrary I/O or other side effects (not described here).
    - Closes the input file (self.input_file.close()) in the finally block when file handling is not overridden.

### `csvkit.cli.CSVKitUtility.main` · *method*

## Summary:
Defines the abstract CLI entrypoint on the base utility by always raising NotImplementedError so subclasses must provide their own implementation.

## Description:
This base implementation enforces that concrete subclasses of CSVKitUtility provide the command's execution logic. The method body contains a single statement that raises NotImplementedError with the message ' must be provided by each subclass of CSVKitUtility.'.

Why this is a separate method:
- Serves as the required override point for subclasses to implement top-level command behavior (argument handling, orchestration, and exit semantics). The base method intentionally does not attempt to perform or assume any behavior beyond signalling that an override is required.

## Args:
self
    - type: instance of the subclass (CSVKitUtility or derived class)
    - description: the instance on which the method is invoked. No other parameters are accepted.

## Returns:
None — the base implementation does not return because it always raises NotImplementedError. A subclass may define and document its own return behavior (commonly None or an integer exit code).

## Raises:
NotImplementedError
    - Condition: unconditionally raised when this base method is called.
    - Message: ' must be provided by each subclass of CSVKitUtility.' (exact message string raised by the implementation).

## State Changes:
Attributes READ:
    - None. The base implementation performs no reads of self attributes.

Attributes WRITTEN:
    - None. The base implementation performs no writes to self attributes.

## Constraints:
Preconditions:
    - None required by the base implementation. For correct runtime behavior, callers should ensure they invoke an overridden implementation on a concrete subclass rather than calling this base method directly.

Postconditions:
    - The method will always raise NotImplementedError and will not mutate object state.

## Side Effects:
    - The only side effect is raising NotImplementedError. The base implementation performs no I/O, network access, or external service interaction.

### `csvkit.cli.CSVKitUtility._init_common_parser` · *method*

## Summary:
Creates and assigns an argparse.ArgumentParser to the instance and registers the standard, shared command-line options used by csvkit utilities, preparing the object for subsequent argument parsing and subclass-specific argument additions.

## Description:
Known callers and lifecycle stage:
- Invoked by CSVKitUtility.__init__ as part of object construction, before add_arguments() and before parse_args(...) are called.
- Typical lifecycle: instantiate CSVKitUtility subclass -> _init_common_parser (creates parser) -> add_arguments (subclass registers extra options) -> self.args = self.argparser.parse_args(args).

Why this is a separate method:
- Centralizes registration of commonly needed CLI options so many csvkit utilities can share consistent behavior.
- Allows subclasses to selectively disable particular common flags by setting override_flags, preventing duplication or conflicts.
- Keeps __init__ lean and ensures a single place to update shared CLI behavior.

## Args:
    self: CSVKitUtility
        Required instance attributes the method reads:
        - description (str or None): passed to argparse.ArgumentParser(description=...).
        - epilog (str or None): passed to argparse.ArgumentParser(epilog=...).
        - override_flags (iterable supporting membership tests): controls which common options are NOT registered. The class defaults override_flags = '' (empty string), so by default no flags are overridden.

## Returns:
    None
    - Side-effect: assigns a new argparse.ArgumentParser instance to self.argparser.

## Raises:
    None explicitly.
    - Possible runtime outcomes:
        - argparse will handle option conflicts and may raise an argparse.ArgumentError or cause program exit if duplicate/invalid option strings are registered; such errors occur if a subclass or external code registers conflicting flags, not from this method under normal use.
        - When the version option is used at the command line, argparse will print the version and exit the program with a SystemExit.

## State Changes:
    Attributes READ:
        - self.description
        - self.epilog
        - self.override_flags

    Attributes WRITTEN:
        - self.argparser (set to a configured argparse.ArgumentParser)

## Postconditions (what the parser will provide after parse_args):
    - The parser will define the following arguments unless suppressed by membership of the indicated key in self.override_flags. The "dest" names below reflect the attribute names that will appear on the parsed args object (self.args):

    Positional:
        - FILE
            - dest: input_path
            - nargs: '?'
            - type: str or None (None if omitted)
            - behavior: optional path to CSV file; omitted means the program may read from STDIN.

    Options (key listed is the override_flags membership key that disables registering the option):
        - key 'd':
            - flags: -d, --delimiter
            - dest: delimiter
            - type: str
            - default: None
            - help: Delimiting character of the input CSV file.

        - key 't':
            - flags: -t, --tabs
            - dest: tabs
            - action: store_true
            - type: bool
            - default: False (store_true sets False unless provided)
            - help: Specify input is tab-delimited; overrides -d.

        - key 'q':
            - flags: -q, --quotechar
            - dest: quotechar
            - type: str
            - default: None
            - help: Character used to quote strings.

        - key 'u':
            - flags: -u, --quoting
            - dest: quoting
            - type: int
            - choices: [0, 1, 2, 3]
            - default: None
            - help: Quoting style (0=Quote Minimal,1=Quote All,2=Quote Non-numeric,3=Quote None).

        - key 'b':
            - flags: -b, --no-doublequote
            - dest: doublequote
            - action: store_false
            - type: bool
            - default: True (store_false sets True unless the option is provided)
            - help: Whether double quotes are doubled in the input CSV.

        - key 'p':
            - flags: -p, --escapechar
            - dest: escapechar
            - type: str
            - default: None
            - help: Character used to escape delimiter or quotechar when relevant.

        - key 'z':
            - flags: -z, --maxfieldsize
            - dest: field_size_limit
            - type: int
            - default: None
            - help: Maximum length of a single field.

        - key 'e':
            - flags: -e, --encoding
            - dest: encoding
            - type: str
            - default: 'utf-8-sig'
            - help: Encoding of the input CSV.

        - key 'L':
            - flags: -L, --locale
            - dest: locale
            - type: str
            - default: 'en_US'
            - help: Locale for formatted numbers.

        - key 'S':
            - flags: -S, --skipinitialspace
            - dest: skipinitialspace
            - action: store_true
            - type: bool
            - default: False
            - help: Ignore whitespace immediately following the delimiter.

        - key 'blanks':
            - flags: --blanks
            - dest: blanks
            - action: store_true
            - type: bool
            - default: False
            - help: Do not convert common empty/null tokens to NULL.

        - key 'blanks' (same key also controls --null-value):
            - flags: --null-value
            - dest: null_values
            - nargs: '+'
            - type: list[str]
            - default: [] (empty list)
            - behavior note: nargs='+' collects one-or-more values when the option appears. Because action='append' is not used, if --null-value appears multiple times on the command line, the last occurrence's list replaces earlier ones (i.e., last-wins), rather than appending across occurrences.

        - key 'date-format':
            - flags: --date-format
            - dest: date_format
            - type: str
            - default: None
            - help: strptime format for dates (e.g. "%m/%d/%Y").

        - key 'datetime-format':
            - flags: --datetime-format
            - dest: datetime_format
            - type: str
            - default: None
            - help: strptime format for datetimes (e.g. "%m/%d/%Y %I:%M %p").

        - key 'H':
            - flags: -H, --no-header-row
            - dest: no_header_row
            - action: store_true
            - type: bool
            - default: False
            - help: Treat input as having no header row; default headers will be generated.

        - key 'K':
            - flags: -K, --skip-lines
            - dest: skip_lines
            - type: int
            - default: 0
            - help: Number of initial lines to skip before the header row.

        - key 'v':
            - flags: -v, --verbose
            - dest: verbose
            - action: store_true
            - type: bool
            - default: False
            - help: Print detailed tracebacks when errors occur.

        - key 'l':
            - flags: -l, --linenumbers
            - dest: line_numbers
            - action: store_true
            - type: bool
            - default: False
            - help: Insert a leading column of line numbers into output.

        - key 'zero':
            - flags: --zero
            - dest: zero_based
            - action: store_true
            - type: bool
            - default: False
            - help: Use zero-based column numbering.

        - (always registered)
            - flags: -V, --version
            - action: version
            - version string: '%(prog)s 1.3.0'
            - behavior: Prints version and exits (SystemExit).

## Constraints:
    Preconditions:
        - Should be called before self.argparser.parse_args(...) is invoked.
        - override_flags must support membership checks (for example: string, list, set). Class default override_flags = '' is acceptable and means "do not override" by default.
    Postconditions:
        - self.argparser exists and has all documented options registered except those explicitly suppressed by override_flags.
        - Parsing later (self.argparser.parse_args) will populate attributes on the returned args namespace matching the dest names above, with the default values documented.

## Edge cases and implementation notes:
    - Because --null-value uses nargs='+', a single occurrence collects one-or-more values (e.g. "--null-value x y z" yields ['x','y','z']). Repeating --null-value on the command line will not accumulate values; the last occurrence replaces earlier ones.
    - For the --no-doublequote option (action=store_false), the attribute doublequote will be True by default and become False only if the option is provided on the command line.
    - argparse's version action triggers a program exit; callers should expect SystemExit when users request version information.
    - If a subclass registers options that conflict (duplicate option strings or dest names), argparse will raise/emit errors when the parser is constructed or when parse_args is invoked; subclasses should avoid registering flags that collide with the common set unless they intentionally override behavior and also include the corresponding key in override_flags.
    - No I/O, file handles, or external services are used by this method. Its only mutation is assigning self.argparser.

### `csvkit.cli.CSVKitUtility._open_input_file` · *method*

## Summary:
Return a file-like object for the given input path, handling STDIN and common compressed file extensions, and ensuring text encoding is applied; when a filesystem path is provided, return a LazyFile wrapper so the file is opened only when first used.

## Description:
Known callers and usage context:
- CSVKitUtility.run(): called early in the CLI run lifecycle to obtain the input stream before processing; the returned object is typically assigned to self.input_file and later closed in the run() finally block.
- Other CSVKitUtility methods (skip_lines, get_rows_and_column_names_and_column_ids, print_column_names, etc.) consume the returned object as an opened text file or iterator.

Lifecycle stage:
- This method is invoked during command initialization/entry (before main processing) to prepare an input stream that downstream code can iterate over or read from.

Rationale for separate method:
- Centralizes handling of the special '-' (STDIN) convention and selection of open functions for common compression formats (.gz, .bz2, .xz).
- Encapsulates encoding application for STDIN and ensures consistent text mode opening for file paths.
- Returns a LazyFile for filesystem paths so file descriptors are not opened during argument parsing or CLI construction.

## Args:
    path (str | None):
        The input path specified by the user. Allowed values:
        - None or empty string: treated as "no path provided" and interpreted as STDIN.
        - '-' (string): explicitly denotes STDIN.
        - Any other string: treated as a filesystem path; its extension (via os.path.splitext) determines whether a compression-aware opener is used.
    opened (bool, optional, default=False):
        When True and the chosen input is STDIN ('-' or falsy path), do not call sys.stdin.reconfigure(encoding=...). Use this when the caller has already configured or opened stdin.

## Returns:
    sys.stdin (TextIO) or LazyFile:
        - If path is falsy (None, empty string) or equals '-', returns sys.stdin (the global standard input text stream).
          * If opened is False, sys.stdin.reconfigure(encoding=self.args.encoding) is invoked before returning to ensure the desired encoding.
        - Otherwise returns an instance of LazyFile constructed as LazyFile(func, path, mode='rt', encoding=self.args.encoding) where func is:
          * gzip.open for .gz extension
          * bz2.open for .bz2 extension
          * lzma.open for .xz extension
          * builtins open for all other extensions
          The LazyFile defers the actual open() call until the first use; no file descriptor is opened by this method for non-STDIN paths.

Edge-case return notes:
- The returned LazyFile may raise file-related errors (FileNotFoundError, PermissionError, OSError, etc.) when it is first opened by the LazyFile (i.e., at first read/iteration/attribute access), not at the time _open_input_file is called.
- The returned sys.stdin is the current interpreter stdin object; callers should not assume it is a fresh or seekable file.

## Raises:
    AttributeError:
        - If path is falsy or '-' and opened is False, the method calls sys.stdin.reconfigure(...). If sys.stdin does not implement reconfigure (or self.args has no encoding attribute), this will raise AttributeError.
    Any exception raised by splitext or by constructing LazyFile:
        - splitext(path) expects a str-like path; providing an incompatible type may raise a TypeError. Constructing LazyFile itself does not open the file, but passing a non-callable as the init argument would cause an error only later when LazyFile tries to call it.
    Note:
        - This method does not open filesystem files immediately, so FileNotFoundError/PermissionError for filesystem paths are not raised here but will propagate when the LazyFile actually invokes the chosen open function.

## State Changes:
Attributes READ:
    - self.args.encoding: read to determine encoding for STDIN reconfiguration and to pass as encoding to LazyFile.
    - (implicitly) self.args (presence assumed): the method accesses self.args and expects it to exist.
Attributes WRITTEN:
    - None. This method does not modify attributes on self.

## Constraints:
Preconditions:
    - self.args must be an object with an attribute encoding (a text encoding string). Typically provided by the argument parser during CSVKitUtility initialization.
    - path should be a string or None. '-' is a reserved value meaning STDIN.
    - opened must be a boolean.

Postconditions:
    - If path is falsy or '-', the method returns sys.stdin. If opened was False, sys.stdin will have been reconfigured to use self.args.encoding (unless reconfigure is not available, in which case an AttributeError occurs and no return happens).
    - If a filesystem path is provided, the method returns a LazyFile configured to call the appropriate open function in text mode ('rt') with encoding=self.args.encoding; no file descriptor will be opened yet.

## Side Effects:
    - May mutate global interpreter state: calls sys.stdin.reconfigure(encoding=...) when returning STDIN and opened is False. This changes the encoding used by the global stdin stream for the running process.
    - Does not open filesystem files immediately for non-STDIN paths (creates LazyFile), so no immediate I/O such as file descriptor allocation or filesystem access occurs for those paths.
    - Uses os.path.splitext to inspect the path's extension (no I/O).
    - Choosing gzip.open / bz2.open / lzma.open ensures that when the LazyFile later opens the path, the file will be opened in a compression-aware manner and in text mode with the provided encoding.

## Implementation notes / reimplementation guidance:
    - Use os.path.splitext(path)[1] to obtain the extension (including the leading dot).
    - Map '.gz' -> gzip.open, '.bz2' -> bz2.open, '.xz' -> lzma.open; use built-in open otherwise.
    - For filesystem paths, instantiate LazyFile(func, path, mode='rt', encoding=self.args.encoding) and return it.
    - For STDIN (path is falsy or '-'):
        * If opened is False, call sys.stdin.reconfigure(encoding=self.args.encoding) before returning sys.stdin.
        * Return sys.stdin (do not wrap it with LazyFile).
    - Do not attempt to open filesystem files synchronously; rely on LazyFile to defer opening.
    - Keep the method free of side effects on self (do not set self.input_file here — the caller should assign the return value).

### `csvkit.cli.CSVKitUtility._extract_csv_reader_kwargs` · *method*

## Summary:
Constructs and returns a dictionary of CSV reader options derived from parsed CLI arguments; does not mutate object state but is typically used to populate self.reader_kwargs during initialization.

## Description:
This helper centralizes the mapping from parsed command-line options (self.args) to the keyword arguments expected by the CSV/agate CSV reader. It is designed so the parsing-to-reader translation is implemented once and reused across methods that open or read CSV data.

Known callers and lifecycle:
- CSVKitUtility.__init__: calls this method immediately after argument parsing and assigns its return value to self.reader_kwargs.
- CSV-reading code paths then consume the produced dict. Some methods use the stored self.reader_kwargs directly (for example, print_column_names uses agate.csv.reader(..., **self.reader_kwargs)), while others accept an explicit kwargs parameter and are typically invoked with this dict (for example, get_rows_and_column_names_and_column_ids can be called with **self.reader_kwargs). This method therefore sits in the initialization stage of the utility lifecycle, producing configuration used every time the utility reads CSV input.

Why this logic is a separate method:
- Prevents duplication of CLI-to-reader mapping across multiple CSV reading locations.
- Makes it easier to test and override reader option construction independently of other initialization logic.

## Args:
None.

## Returns:
dict
- A mapping of CSV reader option names to values derived from self.args. Typical keys and their value types:
    - 'delimiter' -> str: Either '\t' when tabs mode is enabled, or the value of args.delimiter when provided and truthy. If neither applies, 'delimiter' is omitted and the CSV reader default is used.
    - 'quotechar' -> str: Included only if args.quotechar is not None.
    - 'quoting' -> int (0, 1, 2, 3): Included only if args.quoting is not None.
    - 'doublequote' -> bool: Included only if args.doublequote is not None (note: the CLI defines this with action='store_false', so False can be present).
    - 'escapechar' -> str: Included only if args.escapechar is not None.
    - 'field_size_limit' -> int: Included only if args.field_size_limit is not None.
    - 'skipinitialspace' -> bool: Included only if args.skipinitialspace is not None.
    - 'header' -> bool: Included only when args.no_header_row evaluates truthy; set to not args.no_header_row (so when --no-header-row is specified, header is set to False).
- Behavior for falsy values:
    - The method treats values differently depending on how they are accessed:
        * For 'tabs' and 'delimiter' the code checks truthiness (self.args.tabs and self.args.delimiter); falsy delimiter values (e.g., empty string) will be ignored.
        * For other options, the method uses getattr(...) and includes the key when the value is not None (so False values are included).

Edge-case return values:
- Boolean options created via argparse actions (store_true / store_false) may be present with value False in the returned dict because only None is treated as "absent".
- 'header' appears only when no_header_row is truthy; it will be False in the common case where --no-header-row was specified.

## Raises:
- AttributeError:
    - Attempting to access self.args.tabs or self.args.delimiter via direct attribute access will raise AttributeError if those attributes are not present on self.args. (The method uses direct access for these two.)
    - Other options are accessed via getattr(self.args, name) and therefore will not raise AttributeError; they will return None when the attribute is missing.
- The method does not raise any custom exceptions itself.

## State Changes:
Attributes READ:
- self.args.tabs
- self.args.delimiter
- self.args.quotechar
- self.args.quoting
- self.args.doublequote
- self.args.escapechar
- self.args.field_size_limit
- self.args.skipinitialspace
- self.args.no_header_row

Attributes WRITTEN:
- None (the method returns a new dict and does not modify self or self.args).

## Constraints:
Preconditions:
- self.args must be present and should be an argparse.Namespace (or similar) produced by parse_args(); otherwise direct attribute access may raise AttributeError.
- This method should run after argument parsing (e.g., during __init__), so values reflect the user's CLI input or parser defaults.

Postconditions:
- Returns a dict containing only the reader options that were explicitly provided (or whose values are not None), with the delimiter/header precedence rules applied:
    - Tabs flag, if truthy, takes precedence and sets delimiter to '\t', ignoring args.delimiter.
    - If tabs is falsy and args.delimiter is truthy, delimiter is set to that value.
    - header is set to False and included only when args.no_header_row is truthy.

## Side Effects:
- None: no I/O, no external services called, and no mutation of objects outside the returned dict.

## Implementation notes / mapping rules (sufficient to reimplement):
1. Start with an empty dict kwargs = {}.
2. Determine delimiter:
   - If self.args.tabs is truthy: set kwargs['delimiter'] = '\t'.
   - Else if self.args.delimiter is truthy: set kwargs['delimiter'] = self.args.delimiter.
   - Do not include 'delimiter' if neither condition holds.
3. For each name in ('quotechar', 'quoting', 'doublequote', 'escapechar', 'field_size_limit', 'skipinitialspace'):
   - value = getattr(self.args, name)
   - If value is not None: set kwargs[name] = value
   - Note: this will include False (for store_false) but will exclude missing attributes / None.
4. Header mapping:
   - If getattr(self.args, 'no_header_row', None) is truthy, set kwargs['header'] = not self.args.no_header_row (which will be False when --no-header-row is specified).
5. Return kwargs.

### `csvkit.cli.CSVKitUtility._extract_csv_writer_kwargs` · *method*

## Summary:
Return a small dictionary of CSV writer options derived from the parsed command-line arguments. The dictionary is typically assigned to self.writer_kwargs during initialization and later consumed by output-writing code in subclasses.

## Description:
This method inspects self.args (the argparse.Namespace created during CSVKitUtility initialization) and produces a mapping of keyword arguments intended for CSV writer code. It is invoked from CSVKitUtility.__init__ while building the object's runtime configuration:

- Known callers:
    - CSVKitUtility.__init__: called during object construction; the returned dict is assigned to self.writer_kwargs.
    - Intended consumers (not defined in this file): subclass implementations or helper functions that create CSV writers or otherwise need writer-related flags (for example, code that calls get_rows_and_column_names_and_column_ids or agate/csv writer helpers may accept a 'line_numbers' kwarg).

- Context / lifecycle:
    - Called once during initialization to capture CLI-driven writer options into a reusable structure that other methods can pass to writer functions when producing output.

- Why a separate method:
    - Centralizes the mapping between CLI flags and writer options so adding, testing, or overriding writer-related flags is localized.
    - Keeps argument-parsing and writer-configuration logic separated from higher-level business logic (cleaner subclass implementations and easier unit testing).

## Args:
    None.

## Returns:
    dict: A dictionary mapping writer option names (str) to their values. Currently possible return shapes:
        - {} : when no writer-related flags are active (default).
        - {'line_numbers': True} : when the CLI flag for inserting line numbers is set.
    Edge cases:
        - If self.args has no attribute 'line_numbers' (e.g., modified/constructed Namespace), getattr(self.args, 'line_numbers', None) returns None and the returned dict will be empty.
        - If self.args.line_numbers is present but falsy (False), the key is omitted and an empty dict is returned.

## Raises:
    None raised by this method itself.
    (Implicit assumption: self.args exists. If self.args is missing, AttributeError may occur elsewhere when the caller attempted to construct the object — CSVKitUtility sets self.args in __init__ before calling this method.)

## State Changes:
    Attributes READ:
        - self.args (reads the 'line_numbers' attribute on this Namespace)
    Attributes WRITTEN:
        - None by this method. (However, CSVKitUtility.__init__ assigns the returned dict to self.writer_kwargs immediately after calling this method.)

## Constraints:
    Preconditions:
        - self.args should be an argparse.Namespace (or similar object) created by the parser and available on the instance.
    Postconditions:
        - The returned dict contains only keys for writer options that were explicitly requested via CLI flags; no other defaults are injected.
        - The only key currently emitted is 'line_numbers' with a True value when that CLI flag was set.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects outside self.
    - Purely functional: computes and returns a dict based on current self.args.

### `csvkit.cli.CSVKitUtility._install_exception_handler` · *method*

## Summary:
Installs a global unhandled-exception hook that prints either a concise, user-friendly error message or the full traceback depending on the parsed verbose flag. This modifies global interpreter state (sys.excepthook) for the lifetime of the process.

## Description:
This method is called during object construction (CSVKitUtility.__init__) after command-line arguments are parsed and before the utility begins I/O or main execution. Its purpose is to centralize and standardize how uncaught exceptions are presented to end users:
- When verbose is enabled (self.args.verbose is truthy), it delegates to the interpreter's original excepthook (sys.__excepthook__) to show a full traceback and debugging details.
- When verbose is disabled, it prints a short, user-friendly error message to standard error. If the uncaught exception type exactly equals UnicodeDecodeError, it prints a specific message suggesting that the input file encoding is incorrect and refers the user to the -e flag or PYTHONIOENCODING; otherwise it prints "<ExceptionName>: <exception message>".

This logic is implemented in its own method to keep exception-handling policy isolated from parser/initialization and main processing logic, making it easier to test, modify, or override in subclasses.

Known callers:
- CSVKitUtility.__init__: invoked immediately after parsing args and initializing other instance attributes. This is the primary lifecycle stage where the handler is installed so that any errors during subsequent execution are handled by the installed hook.

## Args:
None.

## Returns:
None. The method's observable effect is the side-effect of assigning sys.excepthook; it does not return a value.

## Raises:
- May raise AttributeError if self.args is not present or does not have the attributes 'verbose' or 'encoding' (these attributes are referenced by the handler closure at runtime). The method itself does not explicitly raise exceptions, but failures accessing those attributes will propagate.
- Assigning to sys.excepthook may raise in extremely unusual or restricted runtime environments, but no such handling is performed here.

## State Changes:
Attributes READ:
- self.args.verbose
- self.args.encoding

Attributes WRITTEN:
- None on self. The method does not modify any self.<attr> fields.

Global state modified:
- sys.excepthook is set to the installed handler function (overwriting any previously set hook). This is a persistent, global change that affects how uncaught exceptions are handled for the entire process.

## Constraints:
Preconditions:
- self.args must exist and be an object with attributes 'verbose' and 'encoding' as expected (typically produced by argparse in CSVKitUtility._init_common_parser and parsed in __init__).
- The runtime must permit assignment to sys.excepthook (standard Python environments do).

Postconditions:
- After calling this method, sys.excepthook points to a handler that:
  - Calls sys.__excepthook__(exc_type, exc_value, exc_tb) if self.args.verbose is truthy.
  - Writes a specific, encoded-related message to sys.stderr if exc_type is exactly UnicodeDecodeError and verbose is falsey (the message includes the value of self.args.encoding).
  - Otherwise writes a one-line error of the form "ExceptionName: <message>" to sys.stderr when verbose is falsey.
- No return value is produced and no self attributes are changed.

## Side Effects:
- Global: Replaces the global exception hook (sys.excepthook) for the entire interpreter process; this affects how any uncaught exception is presented to the user.
- I/O: When an uncaught exception occurs, the handler writes to sys.stderr. The UnicodeDecodeError branch writes a multi-sentence user-facing guidance message; the default branch writes a single-line "<ExceptionName>: <message>".
- The handler delegates to sys.__excepthook__ when verbose is enabled, which may print a full traceback to stderr or perform other interpreter-defined behavior.
- Behavior for exception types that are subclasses of UnicodeDecodeError: the code checks for exact equality (exc_type == UnicodeDecodeError), therefore subclasses will not match the UnicodeDecodeError branch and will follow the generic branch.
- Threading consideration: sys.excepthook affects the main thread's uncaught exception handling; other threading models or frameworks that manage exception hooks may not be impacted or may override this behavior.

### `csvkit.cli.CSVKitUtility.get_column_types` · *method*

## Summary:
Constructs and returns an agate.TypeTester configured according to the current CLI arguments (self.args). It centralizes how null-value handling and the inference type order are derived from CLI options and does not modify object state.

## Description:
This method builds the list of agate data types and returns an agate.TypeTester configured with those types.

Known callers and typical context:
- Invoked by CLI command code paths that perform column type inference or otherwise need an agate.TypeTester to interpret CSV column values (for example, during parsing or when converting CSV columns to agate Table columns).
- Typical lifecycle stage: called after CLI argument parsing and before reading or inferring data types from CSV input, so the returned TypeTester reflects the CLI flags and options supplied by the user.

Why this is a separate method:
- Centralizes all logic that maps CLI options to an agate.TypeTester so different CLI subcommands can reuse the same inference configuration.
- Keeps CLI command logic concise and testable by isolating type-construction rules (null-values, locale, date/time formats, inference toggle, and precedence ordering).

## Args (via self.args):
This method takes no explicit parameters beyond self, but it reads the following attributes from self.args and uses them as inputs. The caller must ensure these attributes exist on self.args before invoking.

- blanks : bool or truthy value
    - If truthy, treat no values as built-in nulls (start with an empty null_values list).
    - If falsy/absent, built-in DEFAULT_NULL_VALUES are used as initial null values.
- null_values : iterable[str] (optional)
    - Additional strings that should be treated as nulls. Each element will be appended to the null_values used when constructing data types.
    - If absent or empty, no additional null values are appended.
- no_inference : bool
    - If True, inference is disabled and the returned TypeTester will contain only Text type (no numeric/date/boolean inference).
- locale : str (optional)
    - Passed to agate.Number as its locale parameter. Typical value is a locale string acceptable to agate.Number; may be None.
- date_format : str or None
    - If provided, passed to agate.Date as date_format and influences the placement of number inference in the type order.
- datetime_format : str or None
    - If provided, passed to agate.DateTime as datetime_format and influences the placement of number inference in the type order.

Notes about types/values:
- The method expects self.args.null_values (if present) to be iterable (e.g., list of strings). If it is present but not iterable, iteration will raise a TypeError at runtime.

## Returns:
- agate.TypeTester
    - The returned object is instantiated as agate.TypeTester(types=types) where types is a list of agate DataType instances constructed according to the rules below.
    - Possible shapes:
        - When no_inference is truthy: types == [agate.Text(**type_kwargs)] (only Text type).
        - Otherwise: types contains agate.Boolean, agate.TimeDelta, agate.Date, agate.DateTime, agate.Text plus an agate.Number inserted either near the front or before Text depending on date/datetime format options.
    - Order semantics:
        - If date_format or datetime_format is provided (truthy), number_type is inserted at index -1, i.e., immediately before the last element (Text). Resulting ordering (conceptually): [Boolean, TimeDelta, Date, DateTime, Number, Text].
        - Otherwise number_type is inserted at index 1 (after Boolean). Resulting ordering (conceptually): [Boolean, Number, TimeDelta, Date, DateTime, Text].
    - The TypeTester uses type_kwargs for each constructed DataType; type_kwargs determines which string values are treated as null.

## Raises:
- No exceptions are explicitly raised by the method body itself.
- The following runtime exceptions may occur depending on state and argument types:
    - AttributeError: If self or self.args is missing or if required attributes accessed directly (self.args.no_inference, self.args.locale, self.args.date_format, self.args.datetime_format) are absent, attribute access will raise AttributeError.
    - TypeError: If self.args.null_values exists but is not iterable, the for-loop will raise TypeError when attempting to iterate.
    - Exceptions raised by agate constructors or agate.TypeTester (e.g., invalid locale or invalid format strings) may propagate; those are thrown by the agate library, not by this method.

## State Changes:
Attributes READ:
- self.args (the method reads the following fields on self.args):
    - self.args.blanks
    - self.args.null_values
    - self.args.no_inference
    - self.args.locale
    - self.args.date_format
    - self.args.datetime_format

Attributes WRITTEN:
- None. This method does not modify self or self.args.

## Constraints:
Preconditions:
- self must have an attribute args (self.args) that is an object exposing the attributes listed above.
- If self.args.null_values is present, it should be an iterable of strings (or values convertible to strings) to represent extra null tokens.
- date_format and datetime_format values (if provided) should be valid for agate.Date and agate.DateTime constructors respectively; locale (if provided) should be acceptable to agate.Number.

Postconditions:
- Returns an agate.TypeTester instance configured to:
    - Treat the configured null token set (built-in DEFAULT_NULL_VALUES unless blanks is truthy, plus any self.args.null_values entries) as nulls for all types constructed.
    - Use only Text type when no_inference is truthy.
    - Include Number with placement dependent on presence of date or datetime formats, affecting inference precedence.
- self and self.args remain unchanged.

## Side Effects:
- No I/O, no logging, and no external service calls occur in this method.
- The only mutations performed are to local variables and to the list object created as type_kwargs['null_values'] while appending additional null values; these are local and do not affect external objects except for potential shared references if self.args.null_values reuses the same list object (the method appends into its own new list or an empty list created in-place; it does not mutate self.args.null_values).

### `csvkit.cli.CSVKitUtility.get_column_offset` · *method*

## Summary:
Return an integer column-index offset (0 or 1) based on the object's parsed arguments flag for zero-based numbering.

## Description:
Directly inspects self.args.zero_based and returns 0 when that attribute is truthy, otherwise returns 1. The method implements a single decision: whether the runtime configuration uses zero-based column numbering (offset 0) or one-based numbering (offset 1). It performs no computation beyond this conditional check and does not modify object state.

Behavior observable from the source:
- If self.args.zero_based is truthy (e.g., True), the method returns 0.
- If self.args.zero_based is falsy (e.g., False, 0, empty), the method returns 1.
- The method uses Python truthiness semantics rather than strict boolean equality.

This method is used to obtain the numeric offset needed when converting user-facing column numbers into internal 0-based indexes.

## Args:
None.

## Returns:
int
    - Possible values: 0 or 1.
    - 0 when self.args.zero_based evaluates to True.
    - 1 when self.args.zero_based evaluates to False.

## Raises:
AttributeError
    - Raised if self has no attribute named args, or if self.args lacks the attribute zero_based, because attribute access is not guarded in the method.
    - No other exceptions are raised by the method itself.

## State Changes:
Attributes READ:
    - self.args
    - self.args.zero_based

Attributes WRITTEN:
    - None. The method does not modify any attributes on self.

## Constraints:
Preconditions:
    - self must be an object with an attribute args.
    - self.args must expose the attribute zero_based (a boolean or boolean-like value).

Postconditions:
    - The method returns an integer (0 or 1) and leaves self unchanged.

## Side Effects:
    - None. The method performs no I/O and does not call external services or mutate objects outside self.

## Usage notes:
    - To convert a user-supplied column number n (using the same numbering scheme as the CLI) to a 0-based index, compute: internal_index = n - offset, where offset is the value returned by this method.
    - Examples:
        - If self.args.zero_based is True, the method returns 0.
        - If self.args.zero_based is False, the method returns 1.

### `csvkit.cli.CSVKitUtility.skip_lines` · *method*

## Summary:
Consumes and discards a number of lines from the object's input_file based on the integer value stored in self.args.skip_lines, advancing the file's read position and returning the same file object.

## Description:
- Known callers and context:
    - No direct callers are present in the provided snippet. Typically, this method is invoked in an input-preparation stage of a CSV command-line utility (for example, before parsing or feeding the file into a CSV reader) to skip metadata, comments, or non-data header lines.
- Why this is a separate method:
    - The logic encapsulates a focused, reusable preprocessing step (consuming leading lines) that is conceptually distinct from parsing or validation. Keeping it separate improves testability and readability of higher-level command flow methods.

## Args:
- None (the method uses attributes on self)
- Implicit inputs:
    - self.args.skip_lines (int): Number of lines to skip. Must be an integer value; negative or zero values are permitted but will not cause line consumption.
    - self.input_file (file-like object): Input stream to read from; must implement a readline() method.

## Returns:
- type: The same file-like object referenced by self.input_file.
- possible values/edge cases:
    - Returns the object even if no lines were skipped (e.g., skip_lines == 0 or negative).
    - If the file reaches EOF while skipping, readline() will return an empty string for those reads; the method does not raise an exception for EOF—skip_lines is still decremented until zero.

## Raises:
- ValueError: Raised when self.args.skip_lines is not an int.
    - Exact raised message in the implementation: 'skip_lines argument must be an int'

## State Changes:
- Attributes READ:
    - self.args.skip_lines (inspected for type and compared to 0)
    - self.input_file (used via its readline() method)
- Attributes WRITTEN:
    - self.args.skip_lines (decremented repeatedly while > 0; if initial value > 0 and an int, it will be driven to 0)

## Constraints:
- Preconditions:
    - self must have an attribute args with an attribute skip_lines.
    - self.args.skip_lines must be an int to avoid a ValueError.
    - self must have an attribute input_file that supports a readline() method.
- Postconditions:
    - If initial self.args.skip_lines was a positive int N, after the call self.args.skip_lines will be 0 and the file read position of self.input_file will have advanced by up to N lines (fewer if EOF was reached).
    - If initial self.args.skip_lines was 0 or negative (but an int), the attribute remains unchanged and no lines are consumed.
    - If initial self.args.skip_lines was not an int, the method raises ValueError and neither attribute nor file position is modified by the method (the check is performed before any readline calls).

## Side Effects:
- Mutates the read position of the file-like object self.input_file by calling its readline() method one time per unit skipped.
- Mutates self.args.skip_lines by decrementing it during execution (for positive integer inputs).
- No external I/O beyond reading from the provided file-like object and no network/external service calls.

### `csvkit.cli.CSVKitUtility.get_rows_and_column_names_and_column_ids` · *method*

## Summary:
Return an iterator over CSV data rows along with the header labels and resolved column identifiers, handling optional header-less input and user column selection; does not close the input but consumes the header (or first data) row and any configured skipped lines.

## Description:
This method centralizes the early-stage CSV-reading logic used by CSVKit CLI utilities. It:
- Advances the input stream past any configured skip_lines.
- Creates an agate CSV reader for the (remaining) input.
- Consumes a single row from that reader to obtain either the header row or the first data row (when --no-header-row is used).
- Produces default header names when the input lacks a header.
- Computes a numeric column_offset (0 or 1) and adjusts it if a line-numbers column will be inserted.
- Resolves the user-specified column selectors (include/exclude) to concrete 0-based indices via parse_column_identifiers.

Known callers and context:
- Intended to be called by subclasses inside their main() implementations (or equivalent command pipelines) when they need:
  - An iterator over the CSV data rows (starting after the header or first data row),
  - The sequence of column names used for labeling or matching,
  - A resolved list/range of 0-based column indices based on user-specified selectors.
- This logic is extracted to keep header/datasource handling and column-selection resolution consistent across commands (so each command can focus on higher-level processing once it has rows, names, and ids).

Why this is a separate method:
- Header detection, default header generation, and column identifier parsing are distinct concerns that multiple CLI commands require. Centralizing them avoids duplicated parsing logic, ensures consistent error messages, and makes it easy to unit-test this input-processing step in isolation.

## Args:
    **kwargs:
        Keyword arguments forwarded to the CSV reader factory (agate.csv.reader) and used for local decisions.
        - Common keys: delimiter, quotechar, quoting, escapechar, header, line_numbers, skipinitialspace, field_size_limit, encoding, etc.
        - Recognized by this method specifically:
            - line_numbers (bool): If True, a leading line-number column is expected in output; this method subtracts one from the computed column_offset to compensate.
        - Type: arbitrary mapping of str -> value. No default required by this method (empty dict allowed).

## Returns:
    tuple:
        (rows_iter, column_names, column_ids)

    - rows_iter (iterator[Sequence[str]]):
        An iterator (the agate CSV reader) that yields each subsequent CSV row as a sequence (typically a list or tuple of strings).
        - The iterator begins after any skipped lines and after the header row:
            * If a header row exists, rows_iter yields the first data row on the next iteration.
            * If --no-header-row is set, the first data row is not lost: it is re-chained back onto the iterator so the consumer receives it as the first element.
        - If the input has no rows (StopIteration on first next), rows_iter is an empty iterator (iter([])).

    - column_names (Sequence[str]):
        The header labels for the table:
        - If the input had a header row and --no-header-row is False, this is the first CSV row consumed from the input (a sequence of strings).
        - If --no-header-row is True, this is a tuple produced by make_default_headers with length equal to the number of columns detected from the first data row.
        - If the input is empty, this is an empty list [].

    - column_ids (range[int] or list[int]):
        Resolved 0-based column indices produced by parse_column_identifiers(self.args.columns, column_names, column_offset, getattr(self.args, 'not_columns', None)).
        - If both self.args.columns and self.args.not_columns are falsy, parse_column_identifiers returns a range object representing all indices (range(len(column_names))).
        - Otherwise it returns a list of ints (0-based indices) in the requested order (possibly with duplicates).
        - If the input is empty (early StopIteration), this value is [].

## Raises:
    - ValueError:
        - Raised when self.args.skip_lines is not an int. This arises from self.skip_lines() which checks isinstance(self.args.skip_lines, int) and raises ValueError('skip_lines argument must be an int') otherwise.
    - ColumnIdentifierError:
        - Propagated from parse_column_identifiers if user-specified column selectors (self.args.columns or self.args.not_columns) are invalid (unknown names, out-of-range numeric identifiers, malformed ranges, etc).
    - Any exception raised by agate.csv.reader or by lower-level I/O:
        - Examples include parsing errors or encoding-related exceptions raised while creating or iterating the reader. These exceptions are not caught here (except StopIteration for an empty input).
    - Note: StopIteration from consuming the first row is handled; it does not propagate.

## State Changes:
    Attributes READ:
        - self.args (read to inspect flags: no_header_row, columns, not_columns, zero_based via get_column_offset, line_numbers via kwargs, skip_lines)
        - self.input_file (read by skip_lines and then passed to agate.csv.reader)
        - self.get_column_offset() (method call reads self.args.zero_based indirectly)

    Attributes WRITTEN / MUTATED:
        - self.args.skip_lines: decremented to zero by self.skip_lines() as it consumes the configured number of initial lines. (skip_lines modifies this attribute in-place.)
        - The input file object's read position is advanced by skip_lines() and by consuming the first row (I/O cursor mutation).

## Constraints:
    Preconditions:
        - self.args must be populated (CSVKitUtility.__init__ parses args before callers invoke this method).
        - If the method is called outside run() context, self.input_file must already be an opened readable text file-like object; otherwise _open_input_file is normally used earlier in the lifecycle.
        - self.args.skip_lines must be an integer (or skip_lines will raise ValueError).
        - agate must be importable and its csv.reader function must accept the forwarded kwargs.

    Postconditions:
        - The returned rows_iter will produce rows beginning immediately after the header row (or after the first data row when --no-header-row is set).
        - If --no-header-row was True, column_names is a sequence of default header labels whose length equals the number of columns in the first data row.
        - column_ids, when returned as a list, contain valid 0-based indices into column_names (0 <= idx < len(column_names)). When returned as a range, it represents all valid indices.
        - self.args.skip_lines will be 0 after this call (assuming it began as a non-negative int), and the input file position will have advanced past the skipped lines and the header/first row.

## Side Effects:
    - I/O: Reads from self.input_file. This consumes lines (including skip_lines lines) and the header/first row; it advances the file read cursor.
    - Mutations outside of self:
        - The file object's read pointer is mutated by read operations.
        - self.args.skip_lines is mutated (decremented) by skip_lines().
    - No file is closed by this method; closing is the responsibility of the caller (CSVKitUtility.run closes input_file in the finally block).

### `csvkit.cli.CSVKitUtility.print_column_names` · *method*

## Summary:
Prints the CSV header row as numbered column names to the utility's output stream, honoring zero-based or one-based indexing and rejecting usage when the CSV is declared to have no header row.

## Description:
This method is intended to be invoked by CSVKitUtility command handlers when the user requests to display column names (for example via a CLI "names" option). It isolates the logic for reading the first (header) row from the input and rendering each column name with an index so that the rendering and argument validation are centralized and reusable.

Callers / lifecycle:
- Called during command execution when the utility should display column names to the user (i.e., when a "names" or similar option is used). It performs argument validation, reads the input stream up to the header, and writes formatted output lines to the configured output file.
- It belongs in the CLI/utility command pipeline after input setup (so that self.reader_kwargs, self.skip_lines, and self.output_file are initialized) but before any broader data-processing steps that assume the header has already been consumed.

Why a separate method:
- Keeps argument validation, header-reading, and column-name rendering in one place so other commands can reuse the same behavior without duplicating header-consumption logic.
- Makes unit testing and error handling (e.g., the RequiredHeaderError when headers are disabled) straightforward.

## Args:
None (method reads necessary state from the instance).
However, the method relies on instance attributes configured prior to invocation:
- self.args: object (likely argparse.Namespace) expected to contain boolean-like attributes:
    - no_header_row: if truthy, invocation is invalid and causes RequiredHeaderError.
    - zero_based: if truthy, numbering starts at 0; otherwise numbering starts at 1.
- self.reader_kwargs: dict-like mapping of keyword arguments forwarded to agate.csv.reader.
- self.output_file: file-like object with a write(string) method used to emit formatted lines.
- self.skip_lines: callable or generator-producing function that returns an iterator over CSV rows (the first row returned by that iterator is treated as the header).

## Returns:
None (implicitly returns None).
- Normal completion: writes one output line per header column to self.output_file and returns None.
- Edge-case behavior: if input contains no rows, a StopIteration will be raised when attempting to call next(rows) (this method does not catch it).

## Raises:
- RequiredHeaderError: raised immediately if getattr(self.args, 'no_header_row', None) is truthy. Message: 'You cannot use --no-header-row with the -n or --names options.'
- StopIteration: raised by next(rows) if the input iterator returned by agate.csv.reader(self.skip_lines(), **self.reader_kwargs) yields no rows (the method does not catch this).
- Any exceptions propagated from:
    - self.skip_lines() (if it raises)
    - agate.csv.reader(...) (if it raises for invalid CSV data or reader configuration)
    - self.output_file.write(...) (if write is not supported or fails)
  These are not handled here and will propagate to the caller.

## State Changes:
Attributes READ:
    - self.args (reads no_header_row and zero_based)
    - self.reader_kwargs (passed to agate.csv.reader)
    - self.skip_lines (invoked to obtain the input iterator)
    - self.output_file (read to call write method)

Attributes WRITTEN / MUTATED:
    - No instance attributes are mutated by this method.
    - External mutation: self.output_file is written to (external object state is changed by writes).

## Constraints:
Preconditions:
    - self.args must exist and be readable (it is acceptable if attributes no_header_row or zero_based are absent; getattr will return None).
    - self.output_file must be a writable file-like object with a write(str) method; otherwise writes will fail.
    - self.skip_lines must be callable or otherwise return an iterable of CSV rows where the first yielded item is the header row.
    - self.reader_kwargs must be a mapping suitable for passing as keyword arguments to agate.csv.reader.

Postconditions:
    - On successful return, self.output_file has been written with one formatted line per header column. Each line follows the format '%3i: %s\n' where %3i is the column index (zero-based or one-based depending on args.zero_based) and %s is the column name string representation.
    - The header row has been consumed from the input iterator returned by self.skip_lines() as it is taken via next(rows). The iterator remains at the first data row (if any) for any subsequent readers that reuse the same iterator.

## Side Effects:
- Writes to self.output_file: one line per column name, using a fixed format and newline termination.
- Consumes the header row from the input iterator produced by self.skip_lines(), which may affect later consumption of the same iterator.
- No other I/O or external service calls are performed directly by this method.

### `csvkit.cli.CSVKitUtility.additional_input_expected` · *method*

## Summary:
Return whether the utility should expect additional input from standard input (i.e., stdin is an interactive terminal and no input file/path was supplied), without mutating object state.

## Description:
This method answers the question: "Should the tool wait for or read additional data from sys.stdin, or did the user already provide an input path?" It is typically queried early in CLI workflows to decide whether to treat STDIN as interactive/prompting or to consume piped input.

Known callers and context:
- No explicit callers were detected in the scanned repository. Typical usage is from CLI entrypoints or higher-level run logic in subclasses of CSVKitUtility just before reading or prompting for input, to determine whether to expect piped data versus a file argument.
- Lifecycle stage: invoked during command-line processing or just before input-read operations (i.e., after arg parsing and before opening/consuming input).

Why this is a separate method:
- Encapsulates the small but semantically meaningful check "stdin is a tty AND no input path provided" in one place so callers don't repeat the conditional logic.
- Centralizes interaction with the isatty helper and access to parsed args, keeping run/main code clearer and testable.

## Args:
None (method is invoked on self; relies on self.args and global sys.stdin).

## Returns:
bool (or a falsy non-bool in some pathological cases)

- Typical values:
    - True: sys.stdin appears to be a terminal (isatty(sys.stdin) is truthy) AND self.args.input_path is falsy (for example, None).
    - False: either sys.stdin is not a terminal (isatty(sys.stdin) is falsy) or self.args.input_path is truthy (e.g., a filename string).
- Edge-case details:
    - Because the implementation uses Python's boolean operator semantics ("A and B"), if isatty(sys.stdin) returns a falsy non-boolean value (unusual), that exact falsy value will be returned (not strictly a bool). In practice isatty() returns a boolean.
    - The helper isatty(sys.stdin) handles ValueError raised by calling isatty() on a closed stream and will return False in that case. Other exceptions from isatty() (e.g., AttributeError if sys.stdin lacks isatty) will propagate.

## Raises:
- AttributeError: if self.args has no attribute input_path (this can happen when the class was constructed with override_flags that prevented adding the input argument to the parser), or if sys.stdin lacks an isatty attribute and the caller did not guard against that (the isatty helper intentionally allows AttributeError to propagate).
- Any exception other than ValueError raised by sys.stdin.isatty() will propagate (the isatty helper only suppresses ValueError).

## State Changes:
Attributes READ:
    - self.args.input_path

Attributes WRITTEN:
    - None (this method does not modify any attributes on self)

## Constraints:
Preconditions:
    - self.args must exist (CSVKitUtility.__init__ sets self.args via the parser).
    - Preferably the parser included an input_path argument (i.e., override_flags did not suppress adding the FILE argument); otherwise callers should expect AttributeError.

Postconditions:
    - The method returns immediately without changing object state.
    - After the call, no attributes on self are modified.

## Side Effects:
    - Calls the isatty helper with sys.stdin, which in turn calls sys.stdin.isatty(). This is a read-only query; there are no I/O writes, no file opening/closing, and no global state mutation.
    - Exceptions from sys.stdin.isatty() other than ValueError (which is handled by the helper) may be raised to the caller.

## `csvkit.cli.isatty` · *function*

## Summary:
Safely determine whether a file-like object's stream is a terminal: returns the underlying isatty() result (commonly a bool) or False if the stream is closed.

## Description:
A tiny helper that invokes a file-like object's isatty() method while handling the specific case where the underlying I/O object is closed. Centralizing this logic avoids repetitive try/except blocks around isatty() calls across CLI code.

Known callers within this repository:
    - None detected in the scanned codebase. Typical use is in CLI entrypoints to test sys.stdin or sys.stdout for terminal attachment before enabling interactive behavior (colorization, prompts, pagination).

Typical trigger/context:
    - Called when code must detect whether input/output is attached to a tty and must be robust against previously-closed streams that raise ValueError when queried.

Why this logic is extracted:
    - Responsibility is to provide a single reliable, minimal wrapper around isatty() that explicitly treats a ValueError (commonly raised for operations on closed files) as "not a tty". This keeps higher-level CLI logic simpler and consistent.

## Args:
    f (object): A file-like object expected to implement an isatty() method. No coercion is performed.

    Notes:
        - If f lacks an isatty attribute, an AttributeError will propagate to the caller.
        - If f is None, calling will raise AttributeError.

## Returns:
    The exact return value of f.isatty() if that call completes without raising ValueError; otherwise, False.

    Details:
        - If f.isatty() returns a boolean (the common case), that boolean is returned.
        - If f.isatty() returns a non-boolean truthy/falsy value, that value is returned unchanged.
        - If calling f.isatty() raises ValueError (e.g., I/O operation on closed file), the function returns False.

## Raises:
    AttributeError: If f does not have an isatty attribute (this helper does not catch this).

    Any exception other than ValueError raised by f.isatty() (for example, OSError) will propagate to the caller.

## Constraints:
    Preconditions:
        - Caller should pass an object that implements isatty(). If callers cannot guarantee this, they should guard with hasattr(f, 'isatty') or handle AttributeError.

    Postconditions:
        - If f.isatty() raises ValueError, the function returns False.
        - Otherwise, the function returns whatever value f.isatty() returned (commonly bool).
        - The function does not modify f or other global state.

## Side Effects:
    - None beyond calling f.isatty(). No file writes, network access, global mutations, or other I/O side effects are performed by this helper.

## Control Flow:
flowchart TD
    Start[Start: receive f] --> CheckAttr{has isatty attribute?}
    CheckAttr -- No --> AttrErr[AttributeError propagates to caller]
    CheckAttr -- Yes --> TryCall[Call f.isatty() inside try]
    TryCall --> NoException{call returned without exception}
    NoException -- ReturnVal --> ReturnValue[/Return f.isatty() result/]
    TryCall --> ValueErr{call raised ValueError}
    ValueErr -- Yes --> ReturnFalse[/Return False/]
    TryCall --> OtherErr{call raised other exception}
    OtherErr -- Yes --> OtherErrProp[Other exception propagates to caller]

## Examples:
    - Example: decide whether to colorize output
        if hasattr(sys.stdout, 'isatty') and isatty(sys.stdout):
            enable_color()
        else:
            disable_color()

    - Example: handling unknown objects safely
        # If callers may pass None or arbitrary objects, guard first:
        output = sys.stdout if hasattr(sys, 'stdout') else None
        if output is not None and hasattr(output, 'isatty') and isatty(output):
            # interactive terminal behavior
            ...
        else:
            # non-interactive fallback
            ...

    - Notes on error cases:
        * Closed file object -> isatty() typically raises ValueError -> helper returns False.
        * Object lacking isatty -> AttributeError will be raised by the caller unless guarded.

## `csvkit.cli.default_str_decimal` · *function*

## Summary:
Provide a JSON-friendly string representation for common non-serializable Python types (date, datetime, Decimal), returning a string for serialization or raising TypeError for unsupported types.

## Description:
This helper converts a small set of Python types that the standard JSON encoder cannot serialize into plain strings:
- datetime.date and datetime.datetime values are converted to their ISO 8601 representation (via isoformat()).
- decimal.Decimal values are converted to their textual representation using str().

Known callers within the codebase:
- No explicit internal callers were visible in the provided file-level context. This function is intended to be passed as the `default` argument to JSON serialization functions (for example, the `default` parameter of json.dump/json.dumps) when the serialized objects may include date/datetime or Decimal values.

Why this logic is extracted into its own function:
- Centralizes the mapping from non-JSON-native types to stable, textual representations.
- Keeps serialization code readable by letting callers pass a single function as the JSON encoder fallback instead of inlining multiple isinstance checks each time.
- Ensures consistent formatting of dates and Decimals across different outputs (CSV toolkit CLI JSON exports, logs, etc.).

## Args:
    obj (any): The object to convert for JSON serialization.
        - Allowed/handled types:
            * datetime.date or datetime.datetime -> returned as ISO 8601 string
            * decimal.Decimal -> returned as decimal string via str()
        - Any other type: not handled by this function and results in a TypeError.
    Note: There are no additional parameters or interdependencies.

## Returns:
    str: A string representation suitable for JSON encoding for the supported types:
        - For datetime.date or datetime.datetime: an ISO 8601 formatted string (e.g., "2020-01-02" or "2020-01-02T15:04:05").
        - For decimal.Decimal: the decimal's canonical string form (e.g., "1.23" or "0E-8").
    Edge cases:
        - Subclasses of datetime.date/datetime.datetime are treated as dates and serialized via isoformat().
        - Subclasses of decimal.Decimal are treated as Decimal and serialized via str().

## Raises:
    TypeError: Raised when `obj` is not an instance of datetime.date, datetime.datetime, or decimal.Decimal.
        - The raised message is formatted as: "<repr(obj)> is not JSON serializable"
        - This mirrors the expectation of JSON encoder `default` callables that must raise TypeError for unsupported types.

## Constraints:
    Preconditions:
        - Caller should pass only objects that either are JSON-serializable by the default encoder or are one of the supported types handled here. Typically, the JSON library invokes this function only when it encounters a non-serializable object; callers that call this function directly should ensure it's used in that context.
    Postconditions:
        - If the function returns, the return value is a str and safe for JSON encoding.
        - If the function raises TypeError, no side effects occur and the caller must propagate or handle the error per JSON encoder expectations.

## Side Effects:
    - None. The function is pure: it performs no I/O, does not mutate global or external state, and makes no external service calls.

## Control Flow:
flowchart TD
    Start --> IsDateOrDatetime{isinstance(obj, date or datetime)}
    IsDateOrDatetime -->|yes| ToISO[obj.isoformat()]
    IsDateOrDatetime -->|no| IsDecimal{isinstance(obj, Decimal)}
    IsDecimal -->|yes| ToStr[str(obj)]
    IsDecimal -->|no| Raise[raise TypeError("<repr(obj)> is not JSON serializable")]
    ToISO --> End
    ToStr --> End
    Raise --> End

(Note: "date", "datetime", and "Decimal" in the chart correspond to datetime.date, datetime.datetime, and decimal.Decimal respectively.)

## Examples:
- Typical usage as a JSON serializer fallback:
    - When serializing a structure that may contain dates and Decimal values, pass this function as the `default` argument to a JSON encoding routine so that date/datetime values become ISO 8601 strings and Decimal values become decimal strings. If an unsupported type is encountered, the JSON encoder will receive a TypeError from this function and should propagate or handle it according to the encoder's semantics.

- Behavior examples described in prose:
    1) Input: a datetime.date representing 2020-01-02
       Outcome: returns the string "2020-01-02" (ISO 8601).
    2) Input: a datetime.datetime representing 2020-01-02 15:04:05
       Outcome: returns the string "2020-01-02T15:04:05" (ISO 8601 with time).
    3) Input: a decimal.Decimal('1.23')
       Outcome: returns the string "1.23".
    4) Input: an unsupported type (e.g., a set object)
       Outcome: raises TypeError with a message like "set() is not JSON serializable".

These examples illustrate expected outcomes and error handling without relying on code snippets.

## `csvkit.cli.default_float_decimal` · *function*

## Summary:
Return a JSON-friendly representation where Decimal values are converted to native floats; for other non-JSON-native types, delegate to the string-producing decimal/date serializer.

## Description:
This small helper normalizes objects for JSON serialization with a preference to convert decimal.Decimal values into Python floats. Specifically:
- If the input is an instance of decimal.Decimal (including subclasses), it is converted to a float and returned.
- Otherwise, the function delegates to the module-level default_str_decimal helper, which converts datetime.date/datetime.datetime to ISO 8601 strings and converts decimal.Decimal to their canonical string form or raises TypeError for unsupported types.

Known callers within the codebase:
- No explicit internal callers were discovered in the provided file-level context. This function is intended to be used as the `default` callback passed to JSON encoding routines (for example, json.dump/json.dumps) or other serialization paths that need a fallback for non-JSON-native objects when Decimals should be represented as floats.

Why this logic is extracted into its own function:
- Encapsulates a single serialization policy: prefer float for Decimal values but reuse existing string-based serialization for other non-native types.
- Keeps call sites concise by allowing callers to pass one function to JSON encoders rather than inlining type checks and conversions.
- Ensures consistent handling of Decimal/Date/Datetime across different parts of the CLI export code.

## Args:
    obj (any): The object to convert for JSON serialization or downstream output.
        - If obj is an instance of decimal.Decimal (including subclasses), the function converts it to float(obj).
        - For all other objects, behavior is delegated to default_str_decimal(obj).
    Note: There are no additional parameters or interdependencies other than requiring the default_str_decimal function to be present in the same module namespace.

## Returns:
    float or str: One of:
        - float: when obj is a decimal.Decimal instance — the result of float(obj).
        - str: when obj is handled by default_str_decimal (e.g., datetime.date/datetime.datetime converted to ISO 8601 strings).
    Edge-case returns:
        - decimal.Decimal values are always handled by the first branch (float) — default_str_decimal's Decimal-to-str path is not reached for plain Decimal instances.
        - Subclasses of the accepted types follow the same branching rules (isinstance checks are used).

## Raises:
    TypeError: Propagated from default_str_decimal when obj is neither a decimal.Decimal nor one of the date/datetime types it handles. The exact message and condition follow default_str_decimal (commonly "<repr(obj)> is not JSON serializable").
    Other exceptions from float conversion: Any exceptions raised by the built-in float(obj) conversion (for example, runtime errors due to extreme/unrepresentable Decimal values) will propagate unchanged. The function does not catch or translate these exceptions.

## Constraints:
    Preconditions:
        - The name default_str_decimal must be defined and importable in the same module (it is called unqualified).
        - Callers should expect that Decimal-to-float conversion will lose precision for Decimal values that cannot be exactly represented as IEEE 754 double-precision floats.
    Postconditions:
        - If the function returns normally, the value is a JSON-serializable primitive (float or str) according to the two branches above.
        - No global state is modified.

## Side Effects:
    - None. The function is pure: it performs no I/O, does not mutate global or external state, and makes no external service calls.

## Control Flow:
flowchart TD
    Start --> IsDecimal{isinstance(obj, decimal.Decimal)?}
    IsDecimal -->|yes| ToFloat[return float(obj)]
    IsDecimal -->|no| Delegate[return default_str_decimal(obj)]
    ToFloat --> End
    Delegate --> End

## Examples:
- Typical usage (described):
    - When serializing a structure that may contain Decimal values but you want numeric JSON output (numbers rather than strings), pass this function as the `default` callable to your JSON encoder. Decimal values will be emitted as JSON numbers (via float), while date/datetime values will become ISO 8601 strings via the delegated logic.
- Behavior examples (inputs → outcomes):
    1) Input: decimal.Decimal('1.23') → Outcome: returns the float 1.23 (note: binary float representation may not exactly equal the Decimal's rational value).
    2) Input: datetime.date(2020, 1, 2) → Outcome: delegated to default_str_decimal, returns "2020-01-02".
    3) Input: an unsupported type (e.g., set()) → Outcome: default_str_decimal will raise TypeError; that TypeError is propagated to the caller for the JSON encoder to handle.

## `csvkit.cli.make_default_headers` · *function*

## Summary:
Generate a tuple of column header labels for n columns by delegating each 0-based index to agate.utils.letter_name.

## Description:
This small utility returns a fixed sequence of header names for a table with n columns. It is intended for use wherever code needs consistent, deterministic default column names (for example, when reading a CSV that has no header row and a set number of columns has been detected). The function delegates the label formatting to agate.utils.letter_name so the exact label style (letter-based naming) is determined by agate.

Known callers:
    - No direct callers are visible in this isolated component snapshot. Typical callers in a CSV/CLI or table-processing pipeline would be CSV-reading code paths or CLI code that must synthesize header names when the input has no header row or when column identifiers are requested by index.

Reason for extraction:
    - Encapsulates the policy "use agate's letter-style names for default headers" in one place.
    - Keeps higher-level code readable (callers only request n default headers instead of iterating and calling agate.utils.letter_name themselves).
    - Makes future changes to the labeling strategy (e.g., switching to numeric labels) easy by updating a single function.

## Args:
    n (int):
        Number of columns for which to produce default header names.
        - Expected type: integer.
        - Allowed values: any integer. When n <= 0 the result is an empty tuple.
        - Note: Passing a non-integer (e.g., float or None) will cause a TypeError from the built-in range() call (or when agate.utils.letter_name is called), since the function iterates over range(n).

## Returns:
    tuple[str]:
        A tuple of length max(0, n) containing header labels, in order, one per column index from 0 to n-1.
        - Each element is produced by calling agate.utils.letter_name(i) for the corresponding index i.
        - For n <= 0 the return value is an empty tuple.

## Raises:
    TypeError:
        If n is not an integer type accepted by range(), a TypeError (or similar) will be raised when range(n) is evaluated. No explicit exceptions are raised by this function itself.
    Any exception raised by agate.utils.letter_name:
        If agate.utils.letter_name raises an exception for a particular index (e.g., if agate is not available or letter_name is not callable), that exception will propagate to the caller.

## Constraints:
    Preconditions:
        - The agate package must be importable and provide agate.utils.letter_name as a callable.
        - The caller should pass a numeric integer-like value for n (int recommended).

    Postconditions:
        - The returned tuple has length equal to the number of integers produced by range(n) (i.e., max(0, n) for integer n).
        - Each returned value equals the result of agate.utils.letter_name(i) for i in 0..n-1.

## Side Effects:
    - None. The function performs no I/O and mutates no external state; it only constructs and returns a tuple.
    - It relies on the agate library; any side effects (import-time or inside letter_name) are external to this function.

## Control Flow:
flowchart TD
    Start --> Check_n
    Check_n -->|n <= 0| Return_EmptyTuple
    Check_n -->|n > 0| Generate_Indices
    Generate_Indices --> ForEachIndex
    ForEachIndex --> Call_letter_name
    Call_letter_name --> Collect_Result
    Collect_Result --> Return_Tuple
    Return_EmptyTuple --> End
    Return_Tuple --> End

## Examples:
Assume agate.utils.letter_name maps integer indices to letter-style column labels (this mapping is implemented by agate and not by this function).

Example 1 — zero columns:
    >>> make_default_headers(0)
    ()

Example 2 — three columns (illustrative, depends on agate's letter_name implementation):
    >>> make_default_headers(3)
    ('A', 'B', 'C')  # assuming agate.utils.letter_name returns 'A','B','C' for 0,1,2 respectively

Example 3 — defensive usage with non-integer input:
    try:
        headers = make_default_headers('3')  # incorrect type
    except TypeError:
        # handle the error: convert to int or report to user
        headers = make_default_headers(int('3'))

Notes:
    - This function is intentionally minimal: it focuses on delegation to agate for labeling semantics and on producing a stable, ordered sequence of labels for downstream code.
    - If you require a different naming scheme (e.g., numeric "col_1", "col_2", ...), replace callers with a different helper or modify this function.

## `csvkit.cli.match_column_identifier` · *function*

## Summary:
Convert a user-provided column identifier (column name or numeric position) into a 0-based column index, or raise ColumnIdentifierError with a precise diagnostic message when the identifier is invalid.

## Description:
Centralizes validation and resolution of column identifiers supplied as either names or numeric positions. In the provided source context no direct callers were discovered; when used in the larger project this function is intended for CLI or library code that accepts column references from users (for example, flags or options that accept either a column name or a column number). The function is separated to ensure consistent interpretation, standardized error messages, and to allow callers to adjust numeric base via column_offset.

## Args:
    column_names (Sequence[str]):
        Ordered, indexable sequence of column names (e.g., list or tuple). Must support membership testing (in), indexing ([] or .index()), and len().
    c (str | int):
        Column identifier to resolve.
        - If c is a str that is not composed only of digits (str.isdigit() == False) and exactly equals an element of column_names, it is resolved by name.
        - Otherwise, c is treated as a numeric identifier: the function will call int(c) and subtract column_offset to compute a 0-based index.
    column_offset (int, optional):
        Number subtracted from int(c) to produce a 0-based index. Default 1, meaning numeric input is treated as 1-based user-facing positions. If set to 0, numeric inputs are treated as 0-based.

    Interdependencies:
        - Non-digit strings that match a column name are returned immediately; numeric parsing is not attempted for those values.
        - Strings composed only of digits (e.g., "2") are parsed as integers and interpreted according to column_offset.

## Returns:
    int:
        The resolved 0-based index into column_names.

    Possible return cases:
    - A matching non-digit string: returns column_names.index(c).
    - A numeric identifier that is in-range after subtracting column_offset: returns that 0-based index.
    - The returned value satisfies 0 <= index < len(column_names).

## Raises:
    ColumnIdentifierError:
        - If c is neither a column name nor convertible to int:
            Exact message raised:
            "Column '%s' is invalid. It is neither an integer nor a column name. Column names are: %s"
            where the first %s is the original c (as passed to the function) and the second %s is repr(column_names)[1:-1] (the sequence repr without the surrounding brackets).
        - If numeric conversion succeeds but (int(c) - column_offset) < 0:
            Exact message raised:
            "Column %i is invalid. Columns are 1-based."
            where %i is the numeric value supplied by the user (int(c), before subtracting column_offset).
        - If numeric conversion succeeds but (int(c) - column_offset) >= len(column_names):
            Exact message raised:
            "Column %i is invalid. The last column is '%s' at index %i."
            where the first %i is the numeric value supplied by the user (int(c) before subtracting column_offset), '%s' is column_names[-1] (the last column name), and the final %i is the last valid user-facing numeric index (len(column_names) - 1 + column_offset).

    IndexError:
        - If column_names is an empty sequence and a numeric identifier is out-of-range (any numeric identifier will be >= len(column_names) since len == 0), the function attempts to read column_names[-1] when composing the out-of-range error message and will raise an IndexError. Callers that rely on ColumnIdentifierError for all invalid inputs should ensure column_names is non-empty prior to calling.

## Constraints:
    Preconditions:
        - column_names must be an ordered, indexable sequence of strings.
        - If callers expect only ColumnIdentifierError to be raised for invalid identifiers, column_names must be non-empty (len(column_names) > 0).
        - column_offset must be an integer appropriate to the caller's numbering convention.
        - c should be either a string or an object convertible to int when intended as numeric.
    Postconditions:
        - On success, the returned integer is a valid 0-based index into column_names.
        - No inputs or global state are mutated.

## Side Effects:
    - None in normal operation. The function performs local computation and raises exceptions on invalid input; it does not perform I/O or modify external state.
    - Exception behavior: an IndexError may be raised when column_names is empty and a numeric identifier is handled as out-of-range.

## Control Flow:
flowchart TD
    START([start]) --> CHECK_NAME{isinstance(c,str) AND not c.isdigit() AND c in column_names?}
    CHECK_NAME -- Yes --> RETURN_NAME[return column_names.index(c)]
    CHECK_NAME -- No --> TRY_PARSE[try: parsed = int(c); c = parsed - column_offset]
    TRY_PARSE --> PARSE_FAIL{ValueError raised?}
    PARSE_FAIL -- Yes --> RAISE_NEITHER[raise ColumnIdentifierError("Column '%s' is invalid. It is neither an integer nor a column name. Column names are: %s")]
    PARSE_FAIL -- No --> CHECK_NEG{c < 0?}
    CHECK_NEG -- Yes --> RAISE_NEG[raise ColumnIdentifierError("Column %i is invalid. Columns are 1-based.")]
    CHECK_NEG -- No --> CHECK_TOO_LARGE{c >= len(column_names)?}
    CHECK_TOO_LARGE -- Yes --> RAISE_BIG[raise ColumnIdentifierError("Column %i is invalid. The last column is '%s' at index %i.")]
    CHECK_TOO_LARGE -- No --> RETURN_INDEX[return c]

## Examples:
- By name:
    column_names = ['id', 'name', 'age']
    match_column_identifier(column_names, 'name')  # returns 1

- By numeric string (1-based default):
    column_names = ['id', 'name', 'age']
    match_column_identifier(column_names, '2')     # returns 1

- By integer:
    column_names = ['id', 'name', 'age']
    match_column_identifier(column_names, 3)       # returns 2

- Custom column_offset (0-based numeric interpretation):
    column_names = ['a', 'b']
    match_column_identifier(column_names, '0', column_offset=0)  # returns 0

- Error cases:
    column_names = ['a', 'b', 'c']
    match_column_identifier(column_names, 'foo')
    # Raises ColumnIdentifierError:
    # "Column 'foo' is invalid. It is neither an integer nor a column name. Column names are: 'a', 'b', 'c'"

    column_names = ['a', 'b']
    match_column_identifier(column_names, '3')
    # Raises ColumnIdentifierError:
    # "Column 3 is invalid. The last column is 'b' at index 2"

    column_names = []
    match_column_identifier(column_names, '1')
    # May raise IndexError because the function attempts to access column_names[-1] while composing the out-of-range error message.

## `csvkit.cli.parse_column_identifiers` · *function*

## Summary:
Resolve user-specified column selectors (names, numeric positions, comma-separated lists, and ranges) into concrete 0-based column indices, optionally removing excluded selectors.

## Description:
This helper parses CLI-style column specifications and converts them into numeric 0-based indices referencing the provided header list.

Known callers within the codebase:
- No direct callers were discovered in the preloaded context. In typical usage it is invoked by CLI argument parsing and commands that accept column selection arguments (select, cut, drop, etc.).

Why this logic is extracted:
- Interpretation of user column selectors involves multiple rules (name vs numeric, 1-based vs 0-based, ranges, exclusions). Centralizing parsing ensures consistent behavior and error messages across commands and makes testing and maintenance simpler.

## Args:
    ids (str | None):
        Comma-separated specification of columns to include. Each element can be:
        - A column name (string not composed only of digits).
        - A numeric identifier (string of digits or int), interpreted with column_offset.
        - A range using "a:b" or "a-b", where a or b may be omitted to indicate open-ended ranges (see Range semantics below).
        If ids is falsy (None or empty string) and excluded_columns is also falsy, the function returns a range object representing all indices (see Returns).
    column_names (Sequence[str]):
        Ordered, indexable sequence of header names (list or tuple). Must support len(), indexing, membership testing, and .index().
        If this argument is falsy (e.g., empty list), the function immediately returns an empty list.
    column_offset (int, optional):
        Offset to subtract from numeric identifiers to obtain 0-based indices. Default 1 (user-facing 1-based numbering). If 0, numeric identifiers are treated as 0-based.
    excluded_columns (str | None, optional):
        Comma-separated specification (same syntax as ids) of columns to exclude from the final result. If None, nothing is excluded.

Interdependencies and parsing notes:
- Non-digit strings that exactly match a column name are resolved by name via match_column_identifier.
- Strings composed only of digits are parsed as integers and interpreted according to column_offset by match_column_identifier.
- Range elements are recognized only if parsing the individual element with match_column_identifier fails and the element contains ':' or '-'. Range endpoints that are empty default to the first or last column according to the code's behavior (see Range semantics).
- The included identifiers are parsed first, producing an ordered collection "columns". The excluded identifiers are then parsed into "excludes". The final output is those indices from "columns" that are not in "excludes" (preserves order and duplicates from "columns").

## Returns:
    range[int] or list[int]:
        - If column_names is falsy (empty), returns [] (empty list).
        - If both ids and excluded_columns are falsy, the function immediately returns range(len(column_names)) (a range object representing all indices).
        - Otherwise, the function returns a list of 0-based integers produced by parsing ids (or all columns if ids falsy) and then filtering out any indices derived from excluded_columns. The final return is always a list in this path.
    Notes:
        - Because of the early return, callers must be prepared to accept either a range object (when both ids and excluded_columns are falsy) or a list of ints in general.
        - Returned indices are intended to satisfy 0 <= index < len(column_names) (match_column_identifier enforces range checks).

## Raises:
    ColumnIdentifierError:
        - If a single identifier cannot be resolved by match_column_identifier and is not a syntactic range (no ":" or "-"), the propagated ColumnIdentifierError is raised.
        - If an element is treated as a range but either non-empty endpoint cannot be parsed as an integer, raises:
            "Invalid range %s. Ranges must be two integers separated by a - or : character."
            where %s is the original range string.
        - match_column_identifier may raise ColumnIdentifierError for invalid names or out-of-range numeric identifiers; those errors propagate.
    IndexError:
        - The function itself guards against empty column_names and returns [] early; therefore IndexError should not be raised by this function. However, if match_column_identifier constructs error messages by indexing column_names[-1] and column_names is empty, that helper might raise IndexError. Given the top-level guard, this is avoided.

## Constraints:
Preconditions:
    - column_names must be an ordered, indexable sequence of strings.
    - column_offset must be an integer.
    - ids and excluded_columns should follow the comma-separated syntax described above.

Postconditions:
    - On success, returned indices are valid 0-based positions into column_names (when the return is a list). If a range object is returned, it represents all indices 0..len(column_names)-1.
    - No external state is modified.

Range semantics (explicit):
    - For an include range element (when parsing ids), after splitting "a:b" or "a-b":
        a defaults to 1 when omitted.
        b defaults to len(column_names) + 1 when omitted.
        The code iterates for x in range(a, b) and passes x to match_column_identifier, so the upper bound is exclusive; using len(column_names) + 1 ensures the last column is included when b is omitted.
    - For an exclude range element (when parsing excluded_columns), after splitting:
        a defaults to 1 when omitted.
        b defaults to len(column_names) when omitted (note: this is different from the include-path default and yields a different exclusive/inclusive behavior).
    - This difference between include and exclude range upper-bound defaults exists in the referenced implementation. If you reproduce this function exactly, keep this difference; if you intend consistent semantics, adjust both paths consistently and update tests.

## Side Effects:
    - None. The function performs parsing and index resolution only; it does not perform I/O or mutate external/global state.

## Control Flow:
flowchart TD
    START([Start]) --> CHECK_HEADERS{column_names falsy?}
    CHECK_HEADERS -- Yes --> RETURN_EMPTY[return []] 
    CHECK_HEADERS -- No --> CHECK_IDS_EXCLUDES{ids falsy AND excluded_columns falsy?}
    CHECK_IDS_EXCLUDES -- Yes --> RETURN_RANGE[return range(len(column_names))]
    CHECK_IDS_EXCLUDES -- No --> IDS_PRESENT{ids truthy?}
    IDS_PRESENT -- Yes --> PARSE_IDS[columns = [] ; for each part in ids.split(',')]
    PARSE_IDS --> TRY_MATCH_ID[try match_column_identifier(column_names, part, column_offset)]
    TRY_MATCH_ID -- Success --> APPEND_COL[append index to columns]
    TRY_MATCH_ID -- ColumnIdentifierError --> IS_RANGE{':' in part OR '-' in part?}
    IS_RANGE -- No --> RAISE_PROPAGATE[re-raise ColumnIdentifierError]
    IS_RANGE -- Yes --> SPLIT_RANGE[split into a,b ; parse ints with defaults (include: b defaults to len(column_names)+1)]
    SPLIT_RANGE --> PARSE_FAIL{ValueError during int parse?}
    PARSE_FAIL -- Yes --> RAISE_INVALID_RANGE[raise ColumnIdentifierError("Invalid range %s...")]
    PARSE_FAIL -- No --> FOR_X_RANGE[for x in range(a,b): columns.append(match_column_identifier(..., x, column_offset))]
    FOR_X_RANGE --> IDS_DONE
    IDS_PRESENT -- No --> COLUMNS_ALL[columns = range(len(column_names))]
    COLUMNS_ALL --> IDS_DONE
    IDS_DONE --> EXCLUDES_INIT[excludes = []]
    EXCLUDED_PRESENT{excluded_columns truthy?} -->|Yes| PARSE_EXCLUDES[for each part in excluded_columns.split(',')]
    PARSE_EXCLUDES --> TRY_MATCH_EX[try match_column_identifier(column_names, part, column_offset)]
    TRY_MATCH_EX -- Success --> APPEND_EX[append index to excludes]
    TRY_MATCH_EX -- ColumnIdentifierError --> IS_EX_RANGE{':' in part OR '-' in part?}
    IS_EX_RANGE -- No --> RAISE_PROP_EX[re-raise ColumnIdentifierError]
    IS_EX_RANGE -- Yes --> SPLIT_EX_RANGE[split a,b ; parse ints with defaults (exclude: b defaults to len(column_names))]
    SPLIT_EX_RANGE --> PARSE_EX_FAIL{ValueError?}
    PARSE_EX_FAIL -- Yes --> RAISE_INVALID_RANGE
    PARSE_EX_FAIL -- No --> FOR_X_EX_RANGE[for x in range(a,b): excludes.append(match_column_identifier(..., x, column_offset))]
    FOR_X_EX_RANGE --> EXCLUDES_DONE
    EXCLUDED_PRESENT -- No --> EXCLUDES_DONE
    EXCLUDES_DONE --> RETURN_FILTER[return [c for c in columns if c not in excludes]]
    RETURN_FILTER --> END([End])

## Examples:
- Basic inclusion by name and numeric position:
    column_names = ['id', 'name', 'age']
    parse_column_identifiers('name,1', column_names)
    # 'name' -> index 1 ; '1' -> index 0 (1-based numeric default)
    # Returns [1, 0]

- Full-table shortcut (early return is a range object):
    column_names = ['a', 'b', 'c']
    parse_column_identifiers(None, column_names)
    # ids falsy and excluded_columns falsy -> returns range(0, 3) (a range object, not a list)

- Include range to end:
    column_names = ['a', 'b', 'c', 'd']
    parse_column_identifiers('2:', column_names)
    # Interpreted as range(2, len+1)=range(2,5) -> match_column_identifier called with 2,3,4 -> indices [1,2,3]
    # Returns [1,2,3]

- Exclude specific columns:
    column_names = ['id','x','y','z']
    parse_column_identifiers(None, column_names, excluded_columns='2,4')
    # Start with all columns (since ids falsy) represented internally as range(len(...)), then exclude indices for '2' and '4' -> result [0,2]

- Overlapping references and duplicates:
    column_names = ['id','first','last','age','email']
    parse_column_identifiers('2-4,first', column_names)
    # '2-4' expands to x in 2..4 -> indices [1,2,3]; 'first' -> index 1
    # Final list preserves order and duplicates: [1,2,3,1]

- Invalid range endpoint:
    parse_column_identifiers('a:b', ['a','b'])
    # Raises ColumnIdentifierError("Invalid range a:b. Ranges must be two integers separated by a - or : character.")

