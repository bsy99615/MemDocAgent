# `tasks.py`

## `flower.utils.tasks.iter_tasks` · *function*

## Summary:
Yields (uuid, task) pairs from the events store that match the supplied filters, with optional sorting, pagination (offset/limit) and free-text search.

## Description:
This generator obtains tasks from events.state.tasks_by_timestamp(), optionally re-sorts them, applies successive filters (task type/name, worker hostname, state, received/started timestamp windows, and text search), and yields matching (uuid, task) pairs in order. It performs filtering lazily as the caller iterates.

Known callers within the codebase:
- None discovered in the provided context. Typical callers are UI or API layers that need to present or export filtered task lists (for example, administrative endpoints or CLI commands).

Why this logic is extracted:
- Consolidates task enumeration, filtering, pagination, sorting and search in one place so different callers don't duplicate the selection logic. It enforces a clear responsibility: produce a filtered, paginated iterator of tasks from the events/state store.

## Args:
    events (object):
        Required. Must expose .state.tasks_by_timestamp() which returns an iterable of (uuid, task) pairs. Each task object is expected to have attributes referenced below.
    limit (int or None):
        Optional. Maximum number of matching tasks to yield after skipping offset matching tasks. If None (default), iteration continues until the source is exhausted. Negative values are permitted by Python typing but will not produce meaningful results.
        Note: The implementation treats limit == 0 specially (see "Limit and offset behavior" below).
    offset (int):
        Optional. Number of matching tasks to skip before yielding begins. Default 0.
    type (str or None):
        Optional. If provided, only tasks whose task.name equals this value are considered matches.
    worker (str or None):
        Optional. If provided, tasks are filtered by the worker hostname: only tasks where task.worker is truthy and task.worker.hostname equals this value are guaranteed to pass; tasks with a missing/falsey task.worker are not excluded by this check (they pass the worker filter).
    state (str or None):
        Optional. If provided, only tasks with task.state equal to this value are considered.
    sort_by (Any or None):
        Optional. If provided, the function calls sort_tasks(tasks, sort_by) to obtain a sorted iterable. The allowed values and semantics depend on sort_tasks (not included here).
    received_start / received_end / started_start / started_end (str or None):
        Optional. Timestamp filter bounds. If provided, they are parsed with datetime.strptime using the format '%Y-%m-%d %H:%M' (example: '2024-01-01 13:45') and converted to seconds since epoch. A task is excluded only when both the filter bound is provided and the corresponding task attribute (task.received or task.started) is truthy and outside the bound.
    search (Any):
        Optional. Passed through parse_search_terms(search or {}) to produce search_terms, which are evaluated with satisfies_search_terms(task, search_terms). The accepted search format and semantics are controlled by parse_search_terms.

Interdependencies:
- Date filters only apply when both the filter parameter is truthy and the task attribute (task.received or task.started) is truthy.
- Sorting behavior depends on the external sort_tasks implementation.
- Search behavior depends on parse_search_terms and satisfies_search_terms implementations.

## Returns:
    Iterator[tuple]:
        A generator that yields (uuid, task) tuples lazily for tasks that pass all filters.

Edge-case behaviors:
- If no task matches, the generator yields nothing.
- Exceptions from date parsing, parse_search_terms, satisfies_search_terms, or attribute access will be raised at iteration time when the offending task or parameter is processed.

## Raises:
    ValueError:
        Raised by datetime.strptime if any provided date string (received_start, received_end, started_start, started_end) does not match '%Y-%m-%d %H:%M'.
    Any exceptions propagated from:
        - parse_search_terms(search)
        - satisfies_search_terms(task, search_terms)
        - sort_tasks(tasks, sort_by)
    AttributeError / TypeError:
        If events.state.tasks_by_timestamp() or expected task attributes are missing or of unexpected types, attribute access or comparisons may raise.

## Constraints:
Preconditions:
- events.state.tasks_by_timestamp() must be callable and return an iterable of (uuid, task).
- task objects should expose attributes used by filters: name, worker (with hostname), state, received, started when the corresponding filters are used.
- Date filter strings must match '%Y-%m-%d %H:%M' format.

Postconditions:
- After the generator completes normally, up to limit matching tasks (after skipping offset matching tasks) will have been yielded. If limit is None, all matching tasks will be yielded.
- The function does not mutate global state.

Limit and offset behavior (precise semantics):
- The function maintains a counter i that counts how many tasks have passed all filters (i.e., matching tasks encountered so far).
- For each matching task:
    - If i >= offset, the function yields the task.
    - i is incremented.
    - If limit is not None and i == limit + offset, the loop breaks.
- Consequences:
    - offset skips the first offset matching tasks.
    - limit (when not None) yields at most limit matching tasks after the offset.
    - limit == 0 has unintuitive behavior:
        - If offset == 0 and limit == 0, the implementation never reaches the break condition and will yield all matching tasks (effectively treated like no limit).
        - If offset > 0 and limit == 0, the loop will break once i reaches offset (after processing offset matching tasks) and therefore yield zero tasks.
    - For predictable behavior, use limit as None (no limit) or a positive integer.

## Side Effects:
- No I/O is performed by this function.
- No direct mutation of events/state is performed.
- Side effects may occur if parse_search_terms, satisfies_search_terms or sort_tasks have side effects.

## Control Flow:
flowchart TD
    Start([start])
    A[tasks = events.state.tasks_by_timestamp()]
    B{sort_by is not None?}
    C[if yes: tasks = sort_tasks(tasks, sort_by)]
    D[search_terms = parse_search_terms(search or {})]
    E[for each (uuid, task) in tasks]
    F{type and task.name != type?}
    G{worker and task.worker and task.worker.hostname != worker?}
    H{state and task.state != state?}
    I{received_start and task.received and task.received < convert(received_start)?}
    J{received_end and task.received and task.received > convert(received_end)?}
    K{started_start and task.started and task.started < convert(started_start)?}
    L{started_end and task.started and task.started > convert(started_end)?}
    M{not satisfies_search_terms(task, search_terms)?}
    N{i >= offset?}
    O[yield (uuid, task)]
    P[i += 1]
    Q{limit is not None and i == limit + offset?}
    R[break]
    End([end])
    Start --> A --> B
    B -- yes --> C --> D
    B -- no --> D
    D --> E
    E --> F
    F -- true --> P
    F -- false --> G
    G -- true --> P
    G -- false --> H
    H -- true --> P
    H -- false --> I
    I -- true --> P
    I -- false --> J
    J -- true --> P
    J -- false --> K
    K -- true --> P
    K -- false --> L
    L -- true --> P
    L -- false --> M
    M -- true --> P
    M -- false --> N
    N -- false --> P
    N -- true --> O --> P
    P --> Q
    Q -- true --> R --> End
    Q -- false --> E

## Examples:
1) Iterate up to 50 matching tasks, skipping the first 10 matching tasks:
    for uuid, task in iter_tasks(events, limit=50, offset=10):
        process(task)

2) Filter by task name, worker and received window:
    for uuid, task in iter_tasks(
            events,
            type='generate_report',
            worker='worker-1.example.com',
            received_start='2024-01-01 00:00',
            received_end='2024-01-31 23:59'):
        process(task)

3) Search based on parse_search_terms-compatible input:
    for uuid, task in iter_tasks(events, search={'term': 'urgent'}):
        process(task)

Notes:
- Because the function parses date strings using datetime.strptime, malformed date strings will raise ValueError when the generator reaches the relevant comparison.
- Tasks missing worker/received/started attributes will not be excluded by the corresponding filters (the code checks attribute truthiness before comparing).
- Prefer using limit as None or a positive integer to avoid unintuitive limit==0 behaviors.

## `flower.utils.tasks.sort_tasks` · *function*

## Summary:
Yields the input tasks in a deterministic sorted order according to a string key (optionally descending when prefixed with '-') using task attributes and fallback default values from the module-level sort_keys mapping.

## Description:
This generator orders an iterable of task items by reading a named attribute from each task object and yielding the items in sorted order. It supports reversing the sort order by prefixing the sort key with a leading '-' (minus) sign.

Known callers in the provided context:
    - None found in the supplied source material. Typical callers (not discovered here) are list or view functions that render or filter task lists for reporting or UI endpoints where tasks must be displayed in a chosen order.

Why this is a separate function:
    - Centralizes the logic for sorting tasks so multiple callers can request consistent ordering without duplicating the reverse-prefix parsing, attribute access and fallback-to-default behavior.
    - Encapsulates the dependency on the module-level sort_keys mapping (which provides default values when a task attribute is falsy) and thereby isolates fallback semantics from callers.

## Args:
    tasks (Iterable[tuple[Any, object]]):
        An iterable (e.g., list, generator) of task items. Each item must be an indexable/iterable of length >= 2 (the implementation uses x[1]) where the second element (x[1]) is an object exposing attributes named by the sort keys (see sort_by). Typical shape: (task_id, task_obj). The function will consume the iterable (sorted() evaluates it).
    sort_by (str):
        The name of the attribute to sort by, optionally prefixed with '-' to indicate descending order.
        - Allowed values: any key present in the module-level mapping sort_keys (the code asserts membership).
        - Example values (illustrative): 'name', 'received', 'state' (actual available keys depend on the module-level sort_keys mapping).

Interdependencies:
    - The function expects a module-level mapping sort_keys where:
        * sort_keys is subscriptable by the bare key name (the sort_by string with any leading '-' removed).
        * sort_keys[bare_key] is a callable returning a default value to use when the task attribute evaluates to falsy (None, '', 0, etc).
    - If the attribute is missing entirely on the task object, getattr(...) (called without a default) will raise AttributeError (see Raises).

## Returns:
    generator:
        A generator that yields the same task items passed in (same object identity and ordering determined by sorting). The generator yields items in ascending order by default; yields in descending order if the sort_by string begins with '-'.

    Possible return behaviors / edge-case returns:
        - If tasks is empty, the generator yields nothing.
        - The generator yields tasks in the order produced by Python's built-in sorted() using the computed key for each item.
        - sorted() consumes the input iterable; the function does not return a collection but yields from the sorted sequence.

## Raises:
    AssertionError:
        If sort_by.lstrip('-') is not a key in the module-level sort_keys mapping. The exact triggering code is:
            assert sort_by.lstrip('-') in sort_keys
        This fails immediately when the bare key is not recognized.

    AttributeError:
        If a task's second element (x[1]) does not have the requested attribute named by the (bare) sort key. The code calls getattr(x[1], sort_by) with no default; missing attributes raise AttributeError and will propagate out of the generator.

    Any exception raised by sort_keys[bare_key]():
        Because the fallback value is obtained by calling a callable from sort_keys, any exception thrown by that callable will propagate.

## Constraints:
    Preconditions:
        - The caller must ensure sort_keys is defined in the module and is a mapping from key name (str) to a callable that returns a default sort value.
        - Each task item must be indexable and have a second element (x[1]) that is the task object.
        - The task object must expose the requested attribute (even if its value is None or falsy; if absent entirely, AttributeError will be raised).

    Postconditions:
        - After the generator has been fully iterated, all yielded items have been produced in the requested ordering (ascending or descending).
        - The original iterable has been consumed by Python's sorted(), so if it was a one-shot iterator it will be exhausted.

## Side Effects:
    - No I/O (no file, network, or stdout operations) are performed by this function.
    - No external state is mutated by the function itself (it only reads from the tasks iterable and the module-level sort_keys mapping).
    - The only side effect beyond yielding values is that sorted() will fully evaluate/consume the input iterable.

## Control Flow:
flowchart TD
    A[Start] --> B{sort_by starts with '-'}
    B -- True --> C[strip '-' from sort_by; set reverse=True]
    B -- False --> D[keep sort_by; set reverse=False]
    C --> E[Assert bare sort_by in sort_keys]
    D --> E
    E --> F[Call sorted(tasks, key=keyfunc, reverse=reverse)]
    F --> G[For each task in sorted list: yield task]
    G --> H[End]

    subgraph keyfunc
        K1[Receive task item x] --> K2[Get attr = getattr(x[1], bare_sort_by)]
        K2 --> K3{attr is truthy?}
        K3 -- True --> K4[Use attr as key]
        K3 -- False --> K5[Call sort_keys[bare_sort_by]() and use returned value as key]
    end

## Examples:
Note: these examples are illustrative; actual sort key names depend on the module's sort_keys mapping.

1) Basic ascending sort:
    - Given tasks = [(id1, task_obj1), (id2, task_obj2), ...] and sort_by = 'received'
    - Iterate: for item in sort_tasks(tasks, 'received'): process(item)
    - Behavior: tasks are yielded oldest-to-newest (ascending by the 'received' attribute) assuming 'received' is a comparable value.

2) Descending sort:
    - Use sort_by = '-name' to yield tasks in reverse alphabetical order by their 'name' attribute.

3) Handling falsy attribute values:
    - If a task has attribute task_obj.some_key == None (or '' / 0), the function uses sort_keys['some_key']() to obtain a fallback key to compare.
    - If the attribute is missing entirely on task_obj, an AttributeError will be raised and should be caught by the caller if desired.

4) Error handling sketch:
    - Validate sort key first:
        try:
            gen = sort_tasks(tasks, user_selected_sort_by)
        except AssertionError:
            handle_unknown_sort_key()
        else:
            try:
                for t in gen:
                    process(t)
            except AttributeError:
                handle_missing_task_attribute()

## `flower.utils.tasks.get_task_by_id` · *function*

## Summary:
Return the task object stored under the given key from the events object's task registry, or None if no such task exists.

## Description:
This function is a minimal accessor that retrieves a task by its identifier from the runtime events state. It performs a single dictionary-like lookup using the mapping stored at events.state.tasks.

Known callers within the codebase:
    - No direct callers were found in the provided context. Typical callers (in similar codebases) are task-listing or task-inspection handlers, event processors, or debugging/administration commands that need to obtain a Task object by id.

Why this logic is extracted:
    - Encapsulates the single responsibility of retrieving a task from the events state so higher-level code does not need to know the exact path (events.state.tasks) used to store tasks. It centralizes the lookup semantics (including the implicit None-if-missing behavior) and makes future changes to storage location simpler.

## Args:
    events (object): An object that must expose a `.state` attribute. The `.state` object in turn must expose a `.tasks` attribute that implements a mapping-like interface supporting `.get(key)`.
        - Accepted types: any object meeting the attribute requirements (no concrete class required here).
    task_id (hashable): Key used to look up the task in events.state.tasks (commonly a str or UUID). Must be a valid key for the underlying mapping.

Interdependencies:
    - The function depends on the nested attributes events.state.tasks existing and being a mapping-like object. If any of these attributes are missing or if `.tasks.get` is not callable, an AttributeError or TypeError may be raised.

## Returns:
    The object stored at events.state.tasks[task_id] if present, otherwise None.

    Possible return values:
        - A Task-like object (type depends on how tasks are stored in the repository).
        - None if the key is not present in the mapping.
        - If the underlying mapping implements an alternative semantics for get, the function returns whatever that `.get` returns for the provided key.

## Raises:
    AttributeError:
        - If `events` has no attribute `state`, or `events.state` has no attribute `tasks`, or if `.get` is not an attribute of `.tasks`.
    TypeError:
        - If `.tasks.get` is not callable (e.g., `.tasks` is present but not a mapping-like object).
    Any exceptions raised by the underlying `.get` implementation will propagate.

## Constraints:
Preconditions:
    - Caller must ensure `events` is not None and has the nested attributes `state` and `state.tasks` before calling, unless the caller intends to handle AttributeError/TypeError.
    - The `task_id` must be a key acceptable by the underlying mapping (hashable if underlying is a dict).

Postconditions:
    - No mutation is performed by this function; the mapping at `events.state.tasks` is unchanged.
    - The return value will be either the stored object for `task_id` or None.

## Side Effects:
    - None intrinsic to this function: it performs no I/O, does not mutate global state, and does not alter the tasks mapping.
    - Side effects may occur indirectly if the mapping's `.get` implementation has side effects, but that would be specific to the mapping used.

## Control Flow:
flowchart TD
    Start --> HasState{events has attribute "state"?}
    HasState -->|No| ErrAttrState[Raise AttributeError]
    HasState -->|Yes| HasTasks{state has attribute "tasks"?}
    HasTasks -->|No| ErrAttrTasks[Raise AttributeError]
    HasTasks -->|Yes| HasGet{tasks has "get" callable?}
    HasGet -->|No| ErrTypeGet[Raise TypeError]
    HasGet -->|Yes| CallGet[Call tasks.get(task_id)]
    CallGet --> ReturnValue[Return result (object or None)]
    ErrAttrState --> End
    ErrAttrTasks --> End
    ErrTypeGet --> End
    ReturnValue --> End

## Examples:
- Minimal successful lookup:
    - Prepare an events-like object whose state.tasks is a mapping: set events.state.tasks = {'task-1': task_obj}
    - Call get_task_by_id(events, 'task-1') -> returns task_obj

- Missing task id:
    - If 'task-x' is not a key in events.state.tasks, get_task_by_id(events, 'task-x') -> returns None
    - Caller should check for None to handle "not found" case.

- Defensive usage pattern:
    - If callers cannot guarantee the structure of events, guard access:
        - If events is None or lacks required attributes, catch AttributeError or TypeError around the call and handle accordingly.

## `flower.utils.tasks.as_dict` · *function*

## Summary:
Calls and returns the result of the provided object's as_dict() method, producing a serializable representation of the task-like object.

## Description:
- Known callers:
    - No specific callers were discovered in the supplied context. In a typical codebase this utility is used where code needs a consistent, serializable representation of a task object for APIs, logging, RPC responses, or storage.
- Responsibility and rationale:
    - Isolates the single responsibility of converting a task-like object to its dictionary/serializable form.
    - Keeps call sites decoupled from the concrete task implementation and centralizes a single location for future enhancements (e.g., normalization, validation, caching, or safe-fallbacks) without touching every call site.

## Args:
    task (object): Any object that implements an as_dict attribute that is callable with no arguments.
        - Allowed values: any Python object.
        - Interdependency: The wrapper requires that task.as_dict exists and is callable; otherwise the call will raise an exception.

## Returns:
    Any: The exact value returned by invoking task.as_dict(). Commonly a dict or mapping that represents the task state, but the function does not enforce or transform the returned value.

## Raises:
    AttributeError:
        - Condition: The provided task does not have an attribute named as_dict (e.g., task is None or lacks that attribute).
        - Evidence: Accessing task.as_dict in Python raises AttributeError when the attribute is missing.
    TypeError:
        - Condition: task.as_dict exists but is not callable (e.g., it's a property or other non-callable object). Attempting to call it raises TypeError.
    Any exception raised inside task.as_dict():
        - Condition: If the underlying as_dict implementation raises an exception (ValueError, RuntimeError, KeyError, etc.), that exception is propagated unchanged to the caller.

## Constraints:
- Preconditions:
    - Caller should ensure task is a task-like object exposing a callable as_dict method that accepts no parameters.
    - There is no internal validation or fallback in this wrapper; invalid inputs will raise as described in Raises.
- Postconditions:
    - On successful return, the output equals what the underlying task.as_dict() returned.
    - No additional mutation of the task object is performed by this wrapper beyond whatever task.as_dict() may do.

## Side Effects:
- The wrapper itself performs no I/O, logging, or external interactions.
- Any side effects (I/O, state mutation, logging) are entirely due to the implementation of task.as_dict() and will occur when this function invokes it.

## Control Flow:
flowchart TD
    Start([Start])
    HasAttr{Does task have attribute "as_dict"?}
    AttrMissing[Python raises AttributeError]
    IsCallable{Is task.as_dict callable?}
    NotCallable[Python raises TypeError on call]
    CallAsDict[Invoke task.as_dict()]
    AsDictRaises[Underlying exception propagated]
    ReturnValue[Return value from task.as_dict()]
    Start --> HasAttr
    HasAttr -- no --> AttrMissing
    HasAttr -- yes --> IsCallable
    IsCallable -- no --> NotCallable
    IsCallable -- yes --> CallAsDict
    CallAsDict -- raises --> AsDictRaises
    CallAsDict -- returns --> ReturnValue

## Examples:
- Serializing a single task for an API response:
    task = some_task_object  # some_task_object implements as_dict()
    try:
        payload = as_dict(task)
        # payload can now be JSON-encoded or included in an HTTP response
    except (AttributeError, TypeError) as exc:
        # The object was not task-like; handle or translate into a client error
        raise

- Converting a list of heterogeneous objects with safe filtering:
    tasks = [maybe_task1, maybe_task2, maybe_task3]
    serializable = []
    for candidate in tasks:
        try:
            serializable.append(as_dict(candidate))
        except (AttributeError, TypeError):
            # skip objects that are not task-like
            continue
        except Exception:
            # if a task's as_dict fails unexpectedly, log/handle and continue
            continue

- Handling errors from the underlying implementation explicitly:
    try:
        result = as_dict(task_with_possible_faults)
    except AttributeError:
        # provided object lacks as_dict
        result = None
    except TypeError:
        # as_dict exists but is not callable
        result = None
    except Exception as e:
        # an unexpected error inside the task's as_dict
        # take appropriate remedial action (logging, retry, alerting)
        raise

