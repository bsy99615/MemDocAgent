# `tree.py`

## `bplustree.tree.BPlusTree` · *class*

## Summary:
Represents a persistent on-disk B+ tree mapping keys to byte-string values. Provides insertion, batch insertion, point lookup, iteration, slicing, and checkpoint/close semantics while delegating page and node storage to a FileMemory backend.

## Description:
BPlusTree is a high-level persistence abstraction implementing a B+ tree stored in a paged file via FileMemory. Instantiate this class when you need an ordered mapping from keys (any comparable objects used consistently by callers) to binary values (bytes). The class:
- Manages tree-wide configuration (page size, order, key/value sizes, serializer).
- Creates and updates nodes (leaf/internal/root) through the FileMemory layer.
- Handles overflow storage for values larger than the configured value_size by writing multi-page overflow chains.
- Provides convenience mapping-like methods (get, __getitem__, __setitem__, __contains__, __len__, iteration, keys/items/values).

Typical callers/factories:
- User code creating a persistent index: BPlusTree(filename, page_size=..., order=..., ...)
- Context-managed usage: with BPlusTree(filename) as tree: ...
- Batch ingestion pipelines calling batch_insert for sorted inputs where the caller can guarantee ordering relative to existing data.

Responsibility boundary:
- BPlusTree implements tree-level algorithms (search, splits, root creation, overflow chains) and orchestrates persistence operations via FileMemory.
- Node layout, individual node serialization and in-memory representation are delegated to Node and related classes (LeafNode, InternalNode, RootNode, LonelyRootNode).
- FileMemory is responsible for low-level page allocation, page reads/writes, transactions, checkpointing, and metadata storage.

## State:
Listed attributes (from __slots__) with types, valid ranges, and invariants:

- _filename (str)
  - The path used to open or create the backing file. Immutable after init.

- _tree_conf (TreeConf)
  - Holds configuration: page_size (int), order (int), key_size (int), value_size (int), serializer (Serializer).
  - Constraints: page_size and sizes must be compatible with underlying FileMemory and node implementations; value_size determines when overflow pages are used.

- _mem (FileMemory)
  - FileMemory instance used for all persistence operations.
  - Assumed to expose attributes and methods used by BPlusTree: get_metadata(), set_metadata(), get_node(page), set_node(node), next_available_page (int), get_page(page), set_page(page,data), last_page (int), read_transaction (context manager), write_transaction (context manager), perform_checkpoint(reopen_wal=True), close().

- _root_node_page (int)
  - Page number of the current root node.
  - Invariant: always points to a page that contains the root node; updated via set_metadata whenever root changes.

- _is_open (bool)
  - True while the tree is open; set to False by close().
  - Methods that perform writes use self._mem.write_transaction which expects the tree to be open.

- LonelyRootNode, RootNode, InternalNode, LeafNode, Record, Reference (callable factories created by functools.partial)
  - Each is a partial binding of corresponding classes from node/entry modules with the current TreeConf.
  - Usage invariant: these partials must be created before any nodes/records are created; they are created in __init__ via _create_partials().

Class invariants:
- After initialization, _mem is set, and _root_node_page references a valid root (either created by reading metadata or by _initialize_empty_tree()).
- All mutations that persist state call FileMemory methods under the write_transaction context manager.
- Node.parent links are set by _search_in_tree when descending; parent references must be consistent before performing split operations that expect parent to be set.

## Lifecycle:
Creation:
- Call BPlusTree(filename: str, page_size: int=4096, order: int=100, key_size: int=8, value_size: int=32, cache_size: int=64, serializer: Optional[Serializer]=None)
  - Required: filename.
  - Optional: page_size, order, key_size, value_size, cache_size, serializer. If serializer is None, an IntSerializer() is used by default.
  - Behavior:
    - Stores configuration in a TreeConf.
    - Prepares partial constructors for node/entry types (so they are bound to the tree configuration).
    - Opens or creates FileMemory(filename, tree_conf, cache_size=cache_size).
    - Attempts to read metadata from FileMemory.get_metadata(); if get_metadata raises ValueError, an empty tree is initialized (a LonelyRootNode is created at mem.next_available_page and written; metadata written). Otherwise metadata returns (_root_node_page, tree_conf) which becomes current state.
    - Sets _is_open = True.

Usage (typical method sequencing):
- Read-only operations:
  - get(key, default=None)
  - __contains__(item)
  - __getitem__(item) for single key or slice
  - __len__, __iter__, keys(), items(), values() iterate over leaf records. These use read_transaction context manager from FileMemory.
- Mutations:
  - insert(key, value: bytes, replace=False)
    - Acquires write_transaction.
    - Locates target leaf via _search_in_tree.
    - If key exists, behavior depends on replace flag; may update the existing record in-place (and create or clear overflow pages as needed).
    - If key does not exist, creates a Record (direct value or an overflow chain) and inserts it, splitting leaf if needed.
  - batch_insert(iterable)
    - Intended for sorted insertions. Precondition: the provided iterable must supply items in strictly increasing key order and each new key must be strictly greater than keys currently present in the tree at the insertion position. If this precondition is violated (a key is less than or equal to the biggest_entry.key found in the target node), batch_insert raises ValueError with the message 'Keys to batch insert must be sorted and bigger than keys currently in the tree'. Because batch_insert runs entirely inside the FileMemory.write_transaction context, such a ValueError will abort the write transaction — no partial changes from that batch call will be persisted. Use batch_insert only when you can guarantee ordering, or be prepared to handle transaction aborts raised as ValueError.
  - checkpoint()
    - Performs _mem.perform_checkpoint(reopen_wal=True) inside write_transaction.
- Auxiliary lifecycle operations:
  - _create_overflow(value: bytes) -> int
    - Splits large byte values into overflow pages and writes them; returns first overflow page index.
  - _read_from_overflow(first_overflow_page) -> bytes
    - Reads overflow chain and reconstructs the bytes.
  - _split_leaf, _split_parent, _create_new_root manage node splits and root replacement; they expect node.parent and node.page values to be consistent.
- Destruction / cleanup:
  - close()
    - Uses write_transaction context, calls _mem.close() and sets _is_open = False.
  - Context manager support: use "with BPlusTree(...) as tree:" to ensure close() is called at exit.

Important sequencing / transactional constraints:
- All write operations are executed under _mem.write_transaction context manager to ensure atomicity and durability as provided by FileMemory.
- After splitting or mutating nodes, set_node(node) must be called to persist the node back to FileMemory (BPlusTree does this for changed nodes).
- _root_node_page must be persisted to metadata whenever the root is created or changed (done in _create_new_root and _initialize_empty_tree).
- Violations detected during mutations (e.g., batch_insert ordering check) raise exceptions inside the write_transaction; the transaction semantics of FileMemory determine rollback — BPlusTree assumes write_transaction will abort and prevent partial persistence when an exception is raised.

## Method Map:
Flowchart (method call dependencies and typical invocation order)

graph LR
    A[__init__] --> B[_create_partials]
    A --> C[FileMemory(...) init]
    A --> D[read metadata or _initialize_empty_tree]
    E[insert] --> F[_search_in_tree]
    F --> G[FileMemory.get_node]
    E --> H[_create_overflow]
    H --> I[FileMemory.next_available_page/set_page]
    E --> J[_split_leaf]
    J --> K[_create_new_root]
    J --> L[_split_parent]
    L --> M[InternalNode.pop_smallest]
    N[batch_insert] --> F
    O[get] --> F
    P[_iter_slice] --> F
    Q[_read_from_overflow] --> I
    R[checkpoint] --> C.perform_checkpoint
    S[close] --> C.close

(Note: arrows indicate "calls" or "depends on" relationships. FileMemory methods and Node factories are used throughout.)

## Raises:
Documented exceptions and their trigger conditions observed in the source:

- ValueError
  - __init__: FileMemory.get_metadata() may raise ValueError to indicate no metadata; BPlusTree treats this as "empty file" and initializes an empty tree (this ValueError is caught and handled, not re-raised).
  - insert:
    - The code intends to validate that value is bytes, but the statement used is `if not isinstance(value, bytes): ValueError('Values must be bytes objects')`. As written, this constructs a ValueError but does not raise it. Therefore, in the current implementation this check does not prevent non-bytes values and will not raise. (This appears to be a bug.)
    - When inserting and the key already exists and replace is False, insert raises ValueError('Key {} already exists'.format(key)).
  - get:
    - If node.get_entry(key) raises ValueError (used to signal missing key), get returns the default value passed by the caller. The ValueError is caught and not propagated.
  - _iter_slice:
    - Raises ValueError('Cannot iterate with a custom step') if slice_.step is not None.
    - Raises ValueError('Cannot iterate backwards') if both slice_.start and slice_.stop are present and start >= stop.
  - _search_in_tree:
    - Uses assert page is not None; if the algorithm fails to select a child page, an AssertionError may be raised.
  - batch_insert:
    - Raises ValueError('Keys to batch insert must be sorted and bigger than keys currently in the tree') when a supplied key is less than or equal to the biggest_entry.key in the current node found for insertion. Because batch_insert runs inside a single write_transaction, such an exception will abort that transaction and prevent partial persistence of the batch operation.
  - Other exceptions may be raised by underlying components (FileMemory I/O errors, Node/Record factory errors); these are not explicitly raised by BPlusTree but can propagate.

Note: BPlusTree relies on Node APIs that may raise IndexError (e.g., reading biggest_entry from an empty node); batch_insert checks for this and treats it as no biggest_entry.

## Example:
Creating and using a BPlusTree (illustrative usage pattern):

1) Open a tree and insert single values:
   with BPlusTree('data.db', page_size=4096, order=100) as tree:
       tree.insert('k1', b'value1')
       tree.insert('k2', b'a'*1000)         # large value -> stored in overflow pages
       v = tree.get('k1')                   # returns b'value1'
       contains = 'k1' in tree              # True

2) Batch insert sorted items:
   # Precondition: the iterable must produce items with strictly increasing keys,
   # and each new key must be strictly greater than keys currently in the tree
   # at the insertion positions. Violating this raises ValueError and aborts
   # the write transaction, leaving no partial writes from that batch call.
   pairs = [('k3', b'v3'), ('k4', b'v4')]
   with BPlusTree('data.db') as tree:
       tree.batch_insert(pairs)

3) Iteration and slicing:
   with BPlusTree('data.db') as tree:
       for key in tree:                    # iterates all keys in order
           pass
       items = tree[slice('k1', 'k9')]     # returns mapping of keys->values in range

4) Explicit close and checkpoint:
   tree = BPlusTree('data.db')
   try:
       tree.insert('k5', b'v5')
       tree.checkpoint()
   finally:
       tree.close()

Notes:
- Ensure values passed to insert are bytes. Due to an implementation bug, insert's initial type check does not raise; callers should ensure type correctness.
- When inserting large values exceeding value_size, BPlusTree writes them into overflow pages and stores a pointer (page number) in the Record. Reading transparently returns reconstructed bytes.

### `bplustree.tree.BPlusTree.__init__` · *method*

## Summary:
Prepare a B+ tree instance by storing the filename, creating a TreeConf and helper partials, instantiating the FileMemory backend, attempting to load persisted metadata (or initializing an empty tree), and marking the instance as open.

## Description:
This constructor runs when a caller instantiates a BPlusTree object. It performs the following observable steps in order:
1. Assigns the provided filename to the instance.
2. Constructs a TreeConf from the supplied page_size, order, key_size, value_size and the provided serializer (or IntSerializer() when serializer is None).
3. Calls self._create_partials() to prepare any internal factory/partial functions used elsewhere by the instance.
4. Instantiates FileMemory with the filename and TreeConf (plus cache_size).
5. Calls FileMemory.get_metadata(); if that call raises ValueError the constructor treats that as "no existing metadata" and calls self._initialize_empty_tree(); otherwise it unpacks metadata into self._root_node_page and self._tree_conf.
6. Sets self._is_open = True.

Why this is a constructor:
- The sequence sets up multiple interdependent instance attributes and must run atomically at object creation; separating this logic into __init__ centralizes open/create semantics for the BPlusTree.

Known callers and context:
- Any code that creates a persistent B+ tree by calling BPlusTree(filename, ...). Typically invoked at the start of using a BPlusTree to either open an existing store or create a new one.

## Args:
    filename (str)
        Path to the backing file used for persistence. This exact value is stored in self._filename.
    page_size (int, optional)
        Passed to TreeConf. Defaults to 4096.
    order (int, optional)
        Passed to TreeConf. Defaults to 100.
    key_size (int, optional)
        Passed to TreeConf. Defaults to 8.
    value_size (int, optional)
        Passed to TreeConf. Defaults to 32.
    cache_size (int, optional)
        Passed to FileMemory as cache_size. Defaults to 64.
    serializer (Optional[Serializer], optional)
        Passed to TreeConf; if None, an IntSerializer() instance is used.

Note: The constructor forwards these values into TreeConf and FileMemory; it does not perform additional validation itself in the visible code.

## Returns:
    None

## Raises:
    - ValueError from FileMemory.get_metadata() is explicitly caught and handled by invoking self._initialize_empty_tree(); that specific ValueError does not propagate.
    - Any other exception raised during:
        * TreeConf(...) construction,
        * self._create_partials(),
        * FileMemory(...) constructor,
        * FileMemory.get_metadata() (exceptions other than the caught ValueError),
        * self._initialize_empty_tree()
      will propagate to the caller. The constructor does not catch these in the visible code.

## State Changes:
Attributes READ:
    - No existing self.<attr> attributes are read before assignment in this constructor.

Attributes WRITTEN (visible in this method):
    - self._filename: set to the provided filename argument.
    - self._tree_conf: assigned to the TreeConf constructed from the provided parameters; possibly overwritten by the TreeConf returned in persisted metadata.
    - self._mem: set to the new FileMemory instance.
    - self._root_node_page: assigned only when metadata is returned by FileMemory.get_metadata(); otherwise responsibility for setting root-related attributes is delegated to _initialize_empty_tree().
    - self._is_open: set to True.

Note: _create_partials() and _initialize_empty_tree() may modify additional instance state; those effects are not visible in this method and are implementation-dependent.

## Constraints:
Preconditions:
    - The caller must supply a filename (string). Beyond that, the constructor forwards the other arguments to TreeConf and FileMemory without additional checks in the visible code.

Postconditions:
    - If the constructor returns normally (no exception propagated), then:
        * self._filename, self._tree_conf, and self._mem are assigned.
        * Either persisted metadata was loaded and self._root_node_page and self._tree_conf were set from that metadata, or _initialize_empty_tree() was invoked to set up an empty tree state.
        * self._is_open is True.

## Side Effects:
    - Instantiates FileMemory and calls its get_metadata() method; any external effects (file creation, I/O, or other persistent state changes) depend on the FileMemory implementation.
    - Calls self._create_partials() and, conditionally, self._initialize_empty_tree(); those helper methods may perform further state mutation and/or I/O. The constructor itself does not directly perform I/O in the visible code except via these called components.

### `bplustree.tree.BPlusTree.close` · *method*

## Summary:
Performs an orderly shutdown of the tree's underlying storage: enters a write transaction, closes the underlying FileMemory, and marks the tree instance as closed (changes the object's open/closed state).

## Description:
- Known callers and contexts:
    - BPlusTree.__exit__: invoked automatically when a BPlusTree instance is used as a context manager (with BPlusTree(...) as t:). This ensures the tree is closed when leaving the with-block.
    - User code: callers may call close() explicitly to terminate use of the tree and release underlying resources.
    - Lifecycle stage: called at teardown/shutdown of the tree object to flush and close resources and to mark the instance as no longer usable for further operations.
- Why this is a dedicated method:
    - Encapsulates the shutdown semantics (acquire a write transaction, close the memory backend, update the open state) in one place so __exit__ and other callers share identical, atomic teardown behavior.
    - Keeps resource-release logic separate from other mutations and avoids duplicating error-handling and transaction handling across the class.

## Args:
    None

## Returns:
    None

## Raises:
    - Any exception raised by acquiring or entering the self._mem.write_transaction context manager (e.g., locking or transaction initialization failures).
    - Any exception raised by self._mem.close() (e.g., I/O errors while closing underlying file handles or persistence layers).
    - The method does not catch these exceptions; they propagate to the caller.
    - Note: when close() raises, the object's _is_open flag may remain True because the assignment that sets it to False occurs after self._mem.close().

## State Changes:
- Attributes READ:
    - self._mem
    - self._is_open
- Attributes WRITTEN:
    - self._is_open (set to False on successful close)

## Constraints:
- Preconditions:
    - self must have been initialized so that self._mem exists and exposes:
        - a write_transaction context manager attribute usable in a with-statement
        - a close() method callable with no arguments
    - self._is_open must be a boolean attribute present on the instance (the constructor initializes it to True).
- Postconditions:
    - If close() completes without raising, then:
        - self._mem.close() has been called (underlying memory/storage is closed).
        - self._is_open is False.
    - If close() returns early because the tree was already closed:
        - No calls to self._mem.close() are made and the object's state remains unchanged.
    - If an exception is raised during the write_transaction or during self._mem.close(), the exception is propagated and the object may still be in the pre-call state (in particular, _is_open may remain True).

## Side Effects:
- I/O: invokes self._mem.close(), which typically closes file descriptors, releases persistent resources, flushes buffers, or performs other I/O cleanup (behavior depends on the FileMemory implementation).
- Concurrency/transactional side effects: entering self._mem.write_transaction may acquire locks, start/commit a WAL or transaction, or otherwise serialize access; these side effects depend on the memory backend.
- Logging: when the tree is already closed, the method emits an informational log message via the module logger indicating the tree is already closed.
- No additional in-memory data structures of the BPlusTree instance are modified beyond setting self._is_open to False on success.

### `bplustree.tree.BPlusTree.__enter__` · *method*

## Summary:
Returns the same BPlusTree instance to the caller when entering a context manager block, leaving the object's internal state unchanged.

## Description:
This method implements the context manager entry protocol so that a BPlusTree instance can be used in a with-statement (for example: with BPlusTree(filename) as tree: ...). It is invoked immediately after the with-statement acquires the context and before the with-block body executes.

Known callers and context:
- Any code that uses a BPlusTree instance in a with-statement, e.g. "with BPlusTree('dbfile') as tree:". In that usage the with machinery calls __enter__ at the start of the block and __exit__ at block end.
- It pairs with BPlusTree.__exit__, which closes the tree (via BPlusTree.close) when the with-block completes.

Why this logic is its own method:
- Conforming to Python's context manager protocol requires a dedicated __enter__ method. Keeping it as a separate, minimal method keeps symmetry with __exit__ (which performs cleanup) and allows the with-statement to receive the usable object (self) directly. It remains trivial because no additional setup is required at enter time.

## Args:
This method takes no arguments beyond self.

## Returns:
- Type: BPlusTree (the same instance it was called on)
- Value: returns self unmodified.
- Edge cases: There are no alternate return values; __enter__ never returns None or a different object.

## Raises:
- This method does not raise any exceptions itself. If object construction failed earlier, __enter__ will not be invoked. Any exceptions raised inside the with-block are handled by __exit__.

## State Changes:
- Attributes READ: none (the implementation does not access any attributes)
- Attributes WRITTEN: none (the implementation does not modify any attributes)

## Constraints:
- Preconditions:
    - The BPlusTree instance must be fully constructed (its __init__ completed) before calling __enter__. In practice, the typical call pattern is: instantiate and immediately use in a with-statement.
    - Calling __enter__ on an instance that was previously closed will return the instance but will not reopen or otherwise reinitialize it. The caller is responsible for ensuring the instance is in a usable state before using it inside the with-block.
- Postconditions:
    - After __enter__ returns, the same object is returned to the with-block and no internal state has been changed by this call.
    - The object's lifecycle and resource management are not altered by __enter__; cleanup is performed by __exit__/close on context exit.

## Side Effects:
- None. __enter__ performs no I/O, creates no transactions, and does not mutate objects outside self. Any transactional behavior used by BPlusTree methods (for example, those that call into self._mem.read_transaction or self._mem.write_transaction) must be started explicitly by those methods; __enter__ itself does not start or commit transactions.

### `bplustree.tree.BPlusTree.__exit__` · *method*

## Summary:
Delegates context-manager exit handling to the tree's cleanup routine, ensuring the underlying storage is closed and the tree is marked not open.

## Description:
This method is the context-manager exit hook invoked by Python's with-statement machinery at the end of a with-block. It simply calls the instance's close() method to perform shutdown and resource cleanup.

Known callers and context:
- Implicitly called by the with-statement when a BPlusTree instance is used as a context manager:
    with BPlusTree('file') as tree:
        ...
  At the end of the with-block (whether it exits normally or due to an exception), Python calls __exit__(exc_type, exc_val, exc_tb).
- It may also be invoked directly by user code, but typical usage is via the with-statement.

Why this is its own method:
- Implements Python's context manager protocol cleanly and delegates actual cleanup to close() so that shutdown logic is centralized in one place (avoid duplicating resource-release code in two places).
- Keeping __exit__ minimal reduces surface area for errors during exception-unwinding and makes behavior explicit (it does not suppress exceptions).

## Args:
    exc_type (type | None): Exception class/type raised in the with-block, or None if the block exited normally.
    exc_val (BaseException | None): Exception instance raised in the with-block, or None.
    exc_tb (types.TracebackType | None): Traceback object for the exception, or None.

Note: All three arguments are accepted (they are part of the context-manager protocol) but are ignored by this implementation — the method does not use them to change behavior.

## Returns:
    None

Behavioral consequence:
- Returning None (implicit) means this __exit__ does not suppress exceptions raised inside the with-block. If an exception occurred in the block, it will propagate after __exit__ returns (unless close() itself raises another exception).

## Raises:
    Any exception raised by close() or by underlying FileMemory operations (for example, errors from entering/exiting the write transaction or from FileMemory.close()).

Exact conditions:
- If the tree's close() raises (for example, due to I/O errors in the underlying FileMemory), that exception will propagate out of __exit__.
- If an exception was raised in the with-block and close() raises while handling cleanup, the exception from close() may mask the original exception.

## State Changes:
- Attributes READ (as a consequence of calling close()):
    - self._mem (FileMemory): accessed when close() enters its write_transaction or calls FileMemory.close()
    - self._is_open (bool): read by close() to determine whether there is work to do

- Attributes WRITTEN (as a consequence of calling close()):
    - self._is_open (bool): set to False by close() when cleanup completes

Note: __exit__ itself does not directly access these attributes in its body; the above reads/writes occur because __exit__ delegates to close().

## Constraints:
- Preconditions:
    - The BPlusTree instance must have completed __init__ and hold a valid self._mem and self._is_open attribute.
    - It is safe to call __exit__ regardless of whether the tree is currently open; close() checks self._is_open and will return early if the tree is already closed.

- Postconditions:
    - If close() completes successfully, self._is_open will be False and FileMemory.close() will have been invoked (underlying storage is closed).
    - The BPlusTree instance will no longer be in an "open" state; subsequent operations that require an open tree may fail or raise.

## Side Effects:
- Starts and runs the write-transaction context manager on the underlying FileMemory (close() uses self._mem.write_transaction), which may perform I/O or metadata writes.
- Calls FileMemory.close(), which closes underlying file handles and releases storage-related resources.
- Emits an informational log entry if the tree was already closed (via logger.info inside close()).
- Does not perform any exception suppression; exceptions from the with-block or from close()/FileMemory will propagate to the caller.

### `bplustree.tree.BPlusTree.checkpoint` · *method*

## Summary:
Triggers a checkpoint on the B+Tree's underlying memory backend by entering its write transaction and calling its checkpoint routine; does not modify BPlusTree attributes.

## Description:
This method opens the underlying memory backend's write transaction context and invokes its checkpoint operation with reopen_wal=True. It is a small wrapper that delegates the checkpointing responsibility to the memory implementation.

Known callers:
    - No callers were found in the provided code snapshot. It is intended to be called by higher-level code that wants to force a checkpoint of the on-disk/in-memory storage used by this BPlusTree instance (for example, maintenance, shutdown, or durability guarantees).

Why this is a separate method:
    - Encapsulates the memory backend checkpoint action behind the BPlusTree API so callers do not need to interact with the memory object directly.
    - Keeps checkpoint logic in one place in case additional tree-level bookkeeping is required in the future (logging, metrics, or pre/post checks) without changing external call sites.

## Args:
    None

## Returns:
    None

## Raises:
    - Any exception raised by the underlying memory backend's write_transaction context manager or perform_checkpoint call will propagate out of this method unchanged. Examples (not exhaustive, dependent on memory implementation): context manager __enter__/__exit__ errors, I/O errors, or errors raised by perform_checkpoint.

## State Changes:
    Attributes READ:
        - self._mem

    Attributes WRITTEN:
        - None of the BPlusTree's own attributes are modified by this method.

## Constraints:
    Preconditions:
        - self._mem must be present and must implement:
            * a write_transaction context manager (supporting the with statement)
            * a perform_checkpoint method that accepts the reopen_wal keyword argument
        - The caller must accept that exceptions from the memory implementation will propagate.

    Postconditions:
        - After successful return, the memory backend's perform_checkpoint(reopen_wal=True) has been invoked while inside the memory's write_transaction context.
        - No BPlusTree instance attributes are changed by this call.

## Side Effects:
    - Delegates to the underlying memory backend which may perform side effects such as flushing pages to storage, rotating or reopening a write-ahead log, or other persistence-related I/O. The exact external effects depend entirely on the memory implementation referenced by self._mem.

### `bplustree.tree.BPlusTree.insert` · *method*

## Summary:
Persist a key → value mapping into the B+ tree inside a write transaction: store small values inline, allocate overflow pages for large values, update an existing record only when replace=True, and trigger leaf splitting when a leaf is full. This method mutates the located leaf node and calls the memory layer to persist node changes.

## Description:
This method implements the tree insertion logic visible in the provided source and is intended to be invoked when a caller needs to add or update an entry in the tree storage.

Why this is a separate method:
- The method coordinates locating the target leaf, handling existing keys with optional replacement, deciding between inline and overflow storage, inserting or updating a record, persisting the modified node when appropriate, and invoking leaf-splitting when required. Combining these steps ensures a single transactional boundary and centralizes insertion policy.

Known implementation-level behaviors (directly observable from the source):
- Execution is wrapped by a write transaction context manager obtained from self._mem.write_transaction.
- The leaf node is located by calling self._search_in_tree(key, self._root_node).
- Presence of an existing key is determined by calling node.get_entry(key) and treating a raised ValueError as "not found".
- When replacing an existing record, the method calls self._mem.set_node(node) and returns immediately.
- When inserting a new record, if node.can_add_entry is truthy the method calls self._mem.set_node(node) after insert; otherwise it calls self._split_leaf(node) (and does not call set_node in that branch in the provided source).

## Args:
    key:
        - Type: any type acceptable to the tree's key handling (serialization/comparison).
        - This method does not validate key type or serialization; it simply passes key to lower-level routines.
    value (bytes):
        - Type: bytes
        - Requirement: value must be a bytes instance. (See "Raises" for observed implementation bug.)
    replace (bool, optional):
        - Default: False
        - If False and an existing record with key is found, the method raises ValueError.
        - If True and an existing record is found, the method updates that record in-place.

## Returns:
    None.
    The method returns after persisting or delegating persistence of the change (see "State changes" and "Observed persistence behavior").

## Raises:
    ValueError:
        - Trigger 1 (existing key + replace is False):
            * Condition: node.get_entry(key) returns an existing record (i.e., does not raise ValueError) and replace == False.
            * Effect: raises ValueError with message 'Key {} already exists'.format(key)
        - Note about type-checking (observed bug):
            * The provided source constructs ValueError('Values must be bytes objects') when value is not an instance of bytes but does not raise it. That means the current implementation does not prevent non-bytes values from proceeding.
            * Correct reimplementation should raise ValueError('Values must be bytes objects') when value is not bytes.
    Other exceptions:
        - Any exception raised by self._search_in_tree, node.get_entry, node.insert_entry, self._create_overflow, self._mem.set_node, self._split_leaf, or the write transaction context will propagate; this method does not catch those exceptions.

## State Changes:
Attributes READ (methods/fields referenced):
    - self._mem.write_transaction (context manager entered)
    - self._root_node (passed as argument to _search_in_tree)
    - self._search_in_tree (called to obtain leaf node)
    - node.get_entry (called to detect existing record)
    - self._tree_conf.value_size (used to decide inline vs overflow storage)
    - len(value) (evaluated to compare with value_size)
    - self.Record (constructor used to create new Record instances)
    - self._create_overflow (called when value is bigger than value_size)
    - node.insert_entry (called to insert a new record into node)
    - node.can_add_entry (checked to determine whether to call set_node or _split_leaf)
    - self._mem.set_node (called to persist node in two branches)
    - self._split_leaf (called when node can't accept another entry after insertion)

Attributes WRITTEN / Mutated (directly by this method's code):
    - existing_record.value (assigned when replacing an existing record with inline data)
    - existing_record.overflow_page (assigned or set to None when replacing)
    - node (mutated by node.insert_entry or when an existing_record's fields are updated)
    - Persistence: self._mem.set_node(node) is invoked to record node changes (in the "replace" path and in the "insert without split" path)

Delegated side-effecting calls (mutations performed by called routines; this method invokes them but does not modify their internals):
    - self._create_overflow(value) — expected to allocate and persist overflow pages; the returned page reference is stored on the record.
    - self._split_leaf(node) — expected to handle node splitting and any necessary structural updates; the method calls _split_leaf but does not itself perform those updates.

## Constraints:
Preconditions:
    - The caller must provide value as a bytes object (the provided source fails to enforce this due to a missing raise; reimplementation must enforce it).
    - self._mem.write_transaction must be a functioning write-transaction context manager.
    - self._search_in_tree must accept (key, self._root_node) and return a node object that implements get_entry, insert_entry, and can_add_entry.

Postconditions (strictly deduced from source):
    - If an existing record was found and replace is True:
        * existing_record.value and existing_record.overflow_page are updated according to the value size.
        * self._mem.set_node(node) is called before the method returns.
    - If an existing record was not found and node.can_add_entry was truthy at the branch check:
        * node.insert_entry(record) is called and then self._mem.set_node(node) is called before the method returns.
    - If an existing record was not found and node.can_add_entry was falsy at the branch check:
        * node.insert_entry(record) is called and then self._split_leaf(node) is invoked; the provided source does not call self._mem.set_node in this branch.
    - In all cases, the method returns None on normal completion.

## Side Effects:
    - Enters and exits a write transaction via self._mem.write_transaction (commit/rollback behavior depends on the transaction implementation).
    - Calls self._mem.set_node(node) in two code paths to persist node changes (replace path, insert-without-split path).
    - Calls self._create_overflow(value) when value length exceeds self._tree_conf.value_size; this call is expected to allocate storage and return a page reference which the method stores on the record.
    - Calls self._split_leaf(node) when the leaf was full at insertion; this method is invoked but its persistence behavior is not visible in the provided source.

## Exact control flow (line-by-line mapping):
1. Type check: if not isinstance(value, bytes): ValueError('Values must be bytes objects')
   - Observed: ValueError object is constructed but not raised in provided source (bug).
2. Enter with self._mem.write_transaction:
3. node = self._search_in_tree(key, self._root_node)
4. Try: existing_record = node.get_entry(key)
   - If node.get_entry raises ValueError: treat as "key not found" and continue to create a new record.
   - Else (existing_record found):
       a. If not replace: raise ValueError('Key {} already exists'.format(key))
       b. Else (replace is True):
           i. If len(value) <= self._tree_conf.value_size:
               - existing_record.value = value
               - existing_record.overflow_page = None
           ii. Else:
               - existing_record.value = None
               - existing_record.overflow_page = self._create_overflow(value)
           iii. self._mem.set_node(node)
           iv. return
5. (Key not found path) If len(value) <= self._tree_conf.value_size:
       - record = self.Record(key, value=value)
   Else:
       - first_overflow_page = self._create_overflow(value)
       - record = self.Record(key, value=None, overflow_page=first_overflow_page)
6. node.insert_entry(record)
7. If node.can_add_entry is truthy:
       - self._mem.set_node(node)
   Else:
       - self._split_leaf(node)
8. End write transaction and return None.

## Implementation checklist for reimplementation (minimal, exact steps):
- Step A: Begin by raising ValueError('Values must be bytes objects') if not isinstance(value, bytes).
- Step B: Open a write transaction using self._mem.write_transaction.
- Step C: Find leaf: node = self._search_in_tree(key, self._root_node).
- Step D: Attempt to read existing_record = node.get_entry(key). Treat a raised ValueError as "not found".
- Step E: If existing_record found:
    - If not replace: raise ValueError('Key {} already exists'.format(key)).
    - Else:
        * If len(value) <= self._tree_conf.value_size:
            - existing_record.value = value
            - existing_record.overflow_page = None
        * Else:
            - existing_record.value = None
            - existing_record.overflow_page = self._create_overflow(value)
        * Call self._mem.set_node(node)
        * Return
- Step F: If not found, create record:
    - If len(value) <= self._tree_conf.value_size:
        * record = self.Record(key, value=value)
    - Else:
        * first_overflow_page = self._create_overflow(value)
        * record = self.Record(key, value=None, overflow_page=first_overflow_page)
- Step G: node.insert_entry(record)
- Step H: If node.can_add_entry:
    - Call self._mem.set_node(node)
  Else:
    - Call self._split_leaf(node)
- Step I: Exit write transaction and return.

## Observed bug and recommended fix:
- Observed bug: The provided source constructs ValueError('Values must be bytes objects') when value is not bytes but does not raise it. As a result non-bytes values are not rejected by the implementation.
- Recommendation: Replace that line with "raise ValueError('Values must be bytes objects')" to enforce the precondition.

(End of documentation)

### `bplustree.tree.BPlusTree.batch_insert` · *method*

## Summary:
Performs an in-transaction bulk append of sorted (key, value) pairs into the tree's leaves, creating records (and overflow pages when needed) and mutating leaf nodes and persistent memory accordingly.

## Description:
This method consumes an iterable of (key, value) pairs and inserts them one-by-one at the end of the appropriate leaf node(s) while holding a write transaction on the tree's storage. For each pair it:
- Locates the leaf node for the given key (the first time for each run or when a leaf split forces re-location).
- Validates that each incoming key is strictly greater than the current biggest key in the leaf it targets (raising ValueError if not).
- Creates either an in-line Record or a Record that references an overflow page (by calling _create_overflow) depending on the value length relative to self._tree_conf.value_size.
- Inserts the Record at the end of the leaf node via node.insert_entry_at_the_end.
- If the insertion overflows the leaf (node.can_add_entry is false after insertion), it triggers a leaf split via self._split_leaf and resets the local node reference so the next iteration will re-locate the correct leaf.

Known callers and usage context:
- Intended for bulk loading or appending a sequence of already-sorted keys into an existing B+ tree instance. The method itself is the implementation of a bulk-insert step and is expected to be invoked by higher-level bulk-load helpers or directly by client code that has prepared a sorted iterable.
- The repository's call-sites for this method were not provided; assume external usage for bulk insertion.

Why this logic is a separate method:
- Bulk insert requires a single write transaction spanning many insertions and a controlled algorithm for appending to the current leaf and splitting only when necessary. Isolating this loop prevents repeated transaction handling and centralizes the performance-sensitive path for sorted inserts.

## Args:
    iterable (Iterable):
        An iterable of 2-tuples (key, value). Each tuple must contain:
        - key: a value comparable with keys already stored in the tree (must support comparison operators used by the tree).
        - value: an object for which len(value) is valid (the method uses len(value) to decide overflow behavior).
        No default. The iterable may be finite or empty.

## Returns:
    None
    - The method does not return a value. All modifications are applied to in-memory node objects and persisted via the tree's memory abstraction within the write transaction.

## Raises:
    ValueError:
        - If the current leaf's biggest_entry exists and the incoming key is less than or equal to that biggest_entry.key.
        - Exact trigger in source: when biggest_entry and key <= biggest_entry.key.

    Any exceptions raised by the following operations propagate outwards:
        - self._search_in_tree(self._root_node) (if searching fails)
        - self.Record(...) (Record construction)
        - self._create_overflow(value) (overflow page allocation/creation)
        - node.insert_entry_at_the_end(record) (leaf insertion)
        - self._split_leaf(node) (splitting logic)
    These are not caught by this method and will abort the write transaction.

## State Changes:
Attributes READ:
    - self._mem (accessed for the write transaction context manager and set_node)
    - self._root_node (read once when locating the initial leaf for a run via _search_in_tree)
    - self._tree_conf (used to read value_size)
    - self.Record (used as the Record constructor / factory)
    - node properties accessed: node.biggest_entry, node.can_add_entry

Attributes WRITTEN / Mutated:
    - node (a LeafNode): mutated by node.insert_entry_at_the_end (one or more times).
    - persistent memory through self._mem: the method runs inside self._mem.write_transaction and calls self._mem.set_node(node) for the last active node (persisting the node state). Also, self._create_overflow(value) is invoked when necessary and will create overflow storage (pages) via the memory layer.
    - The tree structure may be mutated indirectly via self._split_leaf(node) (this method is invoked when a leaf overflows after insertion).

Note: The method does not explicitly assign to self._root_node in the shown code; any changes to root or other nodes are effected indirectly by methods it calls (e.g., _split_leaf).

## Constraints:
Preconditions:
    - The iterable must yield pairs (key, value).
    - Each yielded value must support len(value); len(value) is compared to self._tree_conf.value_size.
    - Keys must be in ascending order across the entire iterable relative to the target leaf's existing biggest key: for any inserted key that targets a leaf with an existing biggest_entry, key must be strictly greater than biggest_entry.key. (The method enforces this per leaf at insertion time.)
    - The tree instance must be in a valid usable state (valid self._root_node and a functioning self._mem write transaction context provider).

Postconditions:
    - All records from the iterable that were successfully processed before any raised exception have been inserted into leaf nodes in-memory; the last active node is persisted by calling self._mem.set_node(node) if node remains non-None at loop end.
    - Any overflow pages required for values exceeding value_size have been created via _create_overflow and referenced in the resulting Record objects.
    - Leaf splits occurred as needed via _split_leaf; insertion proceeds so that subsequent keys will be located in the correct leaf(s).

## Side Effects:
    - Runs within a write transaction: acquiring write locks or beginning a transactional write context on the memory abstraction self._mem (via self._mem.write_transaction).
    - May allocate and persist overflow pages by calling self._create_overflow(value).
    - Mutates in-memory leaf node objects and persists the final node via self._mem.set_node(node).
    - Calls to helper methods (e.g., _split_leaf) may mutate other tree nodes or the root; those side effects are performed by the invoked helpers and propagate outward.
    - No external I/O beyond the tree's memory abstraction is performed directly in this method.

### `bplustree.tree.BPlusTree.get` · *method*

## Summary:
Retrieve the bytes value associated with a key from the tree, performing a read-only transaction and returning the provided default when the key is not present.

## Description:
Known callers:
    - __contains__: uses get(key, default=o) to check existence.
    - __getitem__: calls get(key) to obtain the value for subscription access.
    - Any external user code that needs a safe, read-only lookup.

Context / lifecycle:
    - Invoked when a caller wants to read a stored value without modifying the tree.
    - Runs inside a read transaction provided by the underlying FileMemory to ensure a consistent snapshot for the duration of the lookup.

Why this is a separate method:
    - Encapsulates the full read-path: locating the correct leaf node, extracting the Record for the key, and materializing the stored bytes (including reading overflow pages when necessary).
    - Separates read-only lookup logic from insertion/splitting logic and centralizes conversion from Record -> bytes.

## Args:
    key: comparable
        The lookup key. Must be comparable using Python ordering operators and of the same logical type used when inserting keys (i.e., compatible with the tree's serializer; the default serializer is IntSerializer so integer keys are typical).
    default: Any = None
        Value to return when the key is not found. Defaults to None. The method returns this value unchanged when the key does not exist.

## Returns:
    bytes or Any
        - If the key exists in the tree: returns the stored value as bytes (guaranteed by an assertion in the code).
        - If the key does not exist: returns the provided default value (exact object passed as default).
        Note: although the function signature is annotated -> bytes, callers must expect the default's type when the key is absent.

## Raises:
    AssertionError
        - If the retrieved Record does not yield a bytes value (the code asserts that _get_value_from_record returns bytes). This indicates an internal inconsistency or bug.
    Any exceptions raised by underlying storage or traversal
        - Errors raised by the FileMemory transaction context, _search_in_tree (e.g., AssertionError from unexpected tree structure), or by lower-level node code will propagate. Only missing-key ValueError raised by node.get_entry is caught and converted to returning default.

## State Changes:
    Attributes READ:
        - self._mem: used for the read_transaction context, and for fetching nodes/pages during traversal and overflow reads.
        - self._root_node / self._root_node_page: accessed indirectly via the _root_node property to start the search.
        - (transitively) nodes returned by self._mem.get_node and any overflow pages read by _get_value_from_record / _read_from_overflow.
    Attributes WRITTEN:
        - None. This method performs read-only operations and does not modify tree metadata or node state.

## Constraints:
    Preconditions:
        - The BPlusTree instance should be initialized and its underlying FileMemory usable (typically the tree has been constructed or opened and not closed).
        - The key must be of the same type/format used when inserting entries (comparable and serializer-compatible).
    Postconditions:
        - If a Record for key existed at call time, the tree state is unchanged and the method returns the corresponding bytes value.
        - If no Record existed, the tree state is unchanged and the method returns the provided default.

## Side Effects:
    - Performs read I/O via self._mem (disk/page reads and possible overflow-page reads) inside a read transaction (no writes are performed).
    - No mutation of external objects is performed apart from reading pages/nodes through FileMemory.

### `bplustree.tree.BPlusTree.__contains__` · *method*

## Summary:
Perform a read-only membership check and return True if the provided key exists in the tree, otherwise return False.

## Description:
This method implements the Python membership protocol so client code can use `key in tree` to test presence. Its behavior is entirely read-only with respect to the BPlusTree state. The method:
- Enters the FileMemory read-transaction context (with self._mem.read_transaction).
- Calls BPlusTree.get(item, default=sentinel) using a unique sentinel object to distinguish "key absent" from any stored value.
- Returns True when get() returns a value other than the sentinel, and False when get() returns the sentinel.

Known callers and usage contexts:
- Invoked implicitly by Python when evaluating the membership operator (`in`) on a BPlusTree instance (e.g., `if key in tree:`).
- Intended for query/read-time checks where callers only need presence information and do not wish to mutate or fetch the value payload.

Why this method exists separately:
- Provides the standard container membership hook (__contains__) so the BPlusTree behaves like a Python mapping/collection.
- Centralizes the read-transaction and sentinel-lookup pattern so client code does not have to duplicate that logic.

## Args:
    item: Any
        The key to test for membership. The key will be compared against stored keys during tree traversal; therefore it must support the comparison operations used by the tree (e.g., <, <=) with keys already stored in the tree.

## Returns:
    bool
        True if a record with key equal to `item` exists in the tree, False otherwise.
        Notes:
        - The detection of "absent" uses object identity with a unique sentinel created inside the method; there is no risk of collision with stored bytes values because stored values are returned as bytes by get().

## Raises:
The method does not raise to indicate a missing key; missing keys are converted to False. The method will propagate exceptions raised during the read/lookup operations. Exceptions directly evidenced by this module's code include:
    - AssertionError
        - BPlusTree.get() contains an assertion that ensures any retrieved value is bytes (assert isinstance(rv, bytes)); if that assertion fails, AssertionError will propagate.
        - Internal traversal assertions (for example, assertions in _search_in_tree) may raise AssertionError if structural invariants are violated.
    - TypeError
        - Comparisons performed during traversal (e.g., in _search_in_tree) may raise TypeError if the provided key cannot be compared with stored keys.

Any exception raised by the read-transaction context manager or by methods called on self._mem will propagate through __contains__, but specific types and conditions for those exceptions are determined by the self._mem implementation and are not defined in this file.

## State Changes:
Attributes READ:
    - self._mem
        - The FileMemory instance is used (entered via self._mem.read_transaction) and used by get()/_search_in_tree to read nodes/pages.
    - self._root_node_page (indirectly)
        - BPlusTree.get() calls self._root_node which reads self._root_node_page and uses self._mem.get_node to fetch the root node.
    - Node objects and their entry fields accessed during traversal (read-only).

Attributes WRITTEN:
    - None. The method performs read-only operations and does not modify attributes on self.

## Constraints:
Preconditions:
    - The BPlusTree instance must have been initialized such that self._mem is available and usable.
    - The supplied key must be comparable with keys stored in the tree (otherwise comparison operations may raise).

Postconditions:
    - No persistent or in-memory state of the BPlusTree is modified by this call.
    - The return value is a boolean indicating membership unless an exception raised by underlying calls is propagated.

## Side Effects:
    - Acquires the FileMemory read-transaction context for the duration of the lookup. The implementation as written opens a read-transaction in __contains__ and then calls get(), which itself opens a read-transaction; therefore two nested read-transaction context managers are entered according to the current code.
    - Performs read-only I/O via self._mem (node/page reads) as part of lookup; it does not write pages, nodes, metadata, or otherwise mutate persisted data.

### `bplustree.tree.BPlusTree.__setitem__` · *method*

## Summary:
Provide mapping-style assignment semantics by inserting or replacing the record for key with the given value, updating the tree's persistent state.

## Description:
This method implements item-assignment (tree[key] = value) by delegating to the tree's insert logic with replacement enabled. It is typically invoked by user code or higher-level mapping wrappers that perform assignments into the B+ tree. There are no internal callers in the class other than external code using the mapping API.

Why a separate method:
- It exists to implement Python's mapping protocol (item assignment) and keep the mapping interface ergonomic.
- It delegates to BPlusTree.insert(replace=True) so the insertion logic — transactions, overflow handling, node-splitting, and persistence — remains centralized in a single method rather than being duplicated here.

## Args:
    key (any): A key compatible with the tree's ordering and serializer. Keys must be comparable (support ordering operations such as <, <=) because the tree uses ordering to locate insertion points.
    value (bytes): The value to store for the key. The insert logic expects a bytes object; values larger than the configured value_size are stored in overflow pages.

## Returns:
    None

## Raises:
    Any exception raised by BPlusTree.insert is propagated unchanged. See BPlusTree.insert for specific conditions that may raise exceptions (for example, ValueError conditions originating from insert or node operations). __setitem__ itself does not wrap or alter those exceptions.

## State Changes:
Attributes READ:
    - self._mem: accessed to start a write transaction and to read/write nodes/pages (used extensively by insert).
    - self._tree_conf: read to determine value size and other configuration used during insertion and overflow handling.
    - self._root_node (via property): read to locate the leaf node where the key belongs.
    - self.Record: used to construct Record objects for insertion.
    - Other helper methods accessed: self._search_in_tree, self._create_overflow (invoked by insert).

Attributes WRITTEN:
    - Persistent storage reachable from self._mem: insert will call self._mem.set_node, self._mem.set_page, and self._mem.set_metadata as needed, modifying on-disk/stateful storage.
    - self._root_node_page: may be updated when a new root is created during splits (via insert/_create_new_root).
    - Node objects stored in persistent memory (their entries, next_page, and record fields) are modified as part of insertion/splitting and persisted via self._mem.

## Constraints:
Preconditions:
    - The BPlusTree instance must have an initialized FileMemory backend available as self._mem (the tree was constructed/opened successfully).
    - The key must be comparable to existing keys (support ordering operations used by the tree).
    - The value should be a bytes object (the insert logic expects bytes; values exceeding value_size are stored using overflow pages).

Postconditions:
    - After successful completion, the tree contains an entry for key mapping to value. If a record for key previously existed, it is replaced with the new value.
    - If the value exceeded the configured in-node value size, one or more overflow pages will be allocated and linked; the record will reference the first overflow page.
    - The persistent backing (self._mem) will reflect the node changes (nodes written, new pages used, and metadata updated if a new root was created).

## Side Effects:
    - Performs write operations on the underlying storage (self._mem). This includes writing nodes, pages (overflow pages), and possibly updating metadata (root page).
    - May allocate new pages in the storage and modify multiple nodes (leaf and internal nodes) as part of splitting and parent updates.
    - Uses the FileMemory write-transaction context to group writes atomically according to the memory backend's semantics.

### `bplustree.tree.BPlusTree.__getitem__` · *method*

## Summary:
Perform a read-only subscription lookup under the tree's read transaction: for a single key return its stored bytes value, or for a slice return a dict mapping keys in that half-open range to their bytes values. The method does not modify BPlusTree state.

## Description:
- Invocation context: executed when code uses the subscription operator (tree[item]) to read from the tree.
- Behavior branches:
    - Single-key lookup: delegates to self.get(key) and, if a value is found, returns the bytes; if get returns None the method raises KeyError(key).
    - Range lookup: delegates to self._iter_slice(slice_) to iterate Record objects for the requested range and converts each Record into a bytes value using self._get_value_from_record(record), collecting results into a dict keyed by record.key.
- Concurrency/consistency: the entire operation runs inside self._mem.read_transaction, providing a consistent read snapshot as implemented by FileMemory.
- Rationale: separates subscription-level semantics from the underlying search and record-materialization logic by reusing existing helpers (get, _iter_slice, _get_value_from_record) rather than duplicating that logic.

## Args:
    item (slice | Any):
        - If a slice: a standard Python slice used as a half-open key range [start, stop). Restrictions enforced by _iter_slice:
            * slice.step must be None (custom step not supported).
            * If both slice.start and slice.stop are provided, slice.start must be less than slice.stop (slice.start >= slice.stop is rejected).
        - If a non-slice: a single key value compatible with the tree's ordering/comparison semantics.

## Returns:
    If item is a slice:
        dict: mapping each record.key (the stored key type) to its associated bytes value. If no records fall in the range, an empty dict is returned.
    If item is a single key:
        bytes: the value bytes associated with the key (overflow pages, if present, are read and concatenated by helper code).
    Notes:
        - The method never returns None for an existing key; absence of a key results in KeyError.

## Raises:
    KeyError:
        - Condition: item is not a slice and self.get(item) returns None (the key is not present).
    ValueError:
        - Conditions propagated from self._iter_slice:
            * slice.step is not None
            * both slice.start and slice.stop are provided and slice.start >= slice.stop
    Propagated errors:
        - Any exceptions raised while entering or during self._mem.read_transaction or by the helper methods (self.get, self._iter_slice, self._get_value_from_record and underlying FileMemory operations) will propagate to the caller.

## State Changes:
    Attributes READ:
        - self._mem: used to enter the read_transaction and permit the called helpers to read pages/nodes.
        - The method also calls these member methods (which in turn read tree state): self.get, self._iter_slice, self._get_value_from_record.
    Attributes WRITTEN:
        - None. This method performs read-only operations and does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
        - self._mem must be usable for read transactions (the FileMemory instance must be initialized and not closed).
        - Keys or slice bounds provided must be of types that support the tree's ordering/comparison operations; otherwise the underlying search/iteration helpers may raise.
    Postconditions:
        - No mutation to tree metadata, nodes, or pages.
        - Returned bytes values are fully materialized (values stored across overflow pages are concatenated before being returned).
        - For a single-key lookup, either a bytes result is returned or KeyError is raised; no fallback/default is used here.

## Side Effects:
    - Read I/O through FileMemory: the method (via called helpers) will read node pages and, when necessary, overflow pages to materialize values.
    - Acquires and holds a read_transaction on self._mem for the duration of the operation; no writes to disk or tree state are performed.

### `bplustree.tree.BPlusTree.__len__` · *method*

## Summary:
Return the total number of stored records by scanning all leaf nodes from the leftmost leaf to the right, without modifying the tree.

## Description:
This method obtains a read-only transaction on the underlying storage and walks the sequence of leaf nodes starting at the leftmost record-bearing node, summing the number of entries in each leaf. It is the implementation invoked when Python's built-in len() is called on the BPlusTree instance (len(tree)). There are no internal callers in this class (the class uses iteration and other accessors for different purposes), so this logic is provided as a dedicated method to isolate the full-tree counting behavior (which is expensive and read-only) from other operations.

Known callers and context:
- Invoked by Python when calling len(tree).
- Can be called by external user code or tests that need an exact count of records.
- Not used internally by other methods in this class for routine operations (those use iterators or more lightweight hints).

Why this is its own method:
- Counting requires a full traversal of all leaf nodes; keeping the traversal separate keeps read-only counting logic encapsulated and avoids duplicating traversal code in other methods.
- The method acquires a read transaction for the duration of the traversal to ensure a consistent snapshot and to prevent concurrent write-side interference.

## Args:
    None

## Returns:
    int: The total number of stored record entries across all leaf nodes.
    - Always a non-negative integer (0 if the tree contains no records).
    - Edge cases:
        - If the leftmost node has zero entries and no next page, returns 0.
        - If next_page is a falsey sentinel (e.g., 0 or None) the traversal stops and the accumulated count is returned.

## Raises:
    None explicitly raised by this method.
    - This method does not raise application-specific exceptions itself; however, exceptions raised by underlying components may propagate:
        - Errors from the memory layer (for example if the read transaction context manager or get_node raises) will propagate to the caller.
        - Any exceptions raised by node implementations when accessing attributes (e.g., if a node is malformed) will propagate.

## State Changes:
    Attributes READ:
        - self._mem.read_transaction (uses the memory's read-only transaction context manager)
        - self._left_record_node (property; reads self._root_node and navigates to the leftmost leaf)
        - self._mem.get_node (used to fetch nodes by page when following next_page)
        - node.entries (length is read to count records)
        - node.next_page (used to determine whether to continue traversal)

    Attributes WRITTEN:
        - None. This method performs no writes to the BPlusTree instance or the memory layer.

## Constraints:
    Preconditions:
        - self._mem must be initialized and provide:
            * a read_transaction context manager supporting 'with'
            * a get_node(page) method that returns node-like objects
        - The property self._left_record_node must return a node object with attributes entries and next_page.
        - Nodes returned by self._mem.get_node must expose a sequence-like entries (so len(node.entries) is valid) and a next_page attribute that is falsey when there are no further leaf pages.

    Postconditions:
        - The tree is left unchanged by this call (no mutations performed).
        - The return value equals the sum of len(entries) for every leaf node reachable from the leftmost leaf by following next_page links at the moment the read transaction snapshot was acquired.

## Side Effects:
    - No external I/O is performed by this method itself beyond read access through the memory abstraction (via get_node and the read transaction). All operations are read-only and limited to the memory layer and node objects returned by it.

### `bplustree.tree.BPlusTree.__length_hint__` · *method*

## Summary:
Provides a read-only, integer estimate of how many records the tree contains; intended as a non-exact length hint for consumers that inspect __length_hint__.

## Description:
This method implements the Python length-hint protocol: it computes and returns a best-effort integer estimate of stored records without mutating tree state. It executes entirely inside a read transaction to get a consistent view of on-disk metadata.

Implementation behavior (directly reflected in the code):
- Acquire a read transaction via self._mem.read_transaction.
- Read the current root node via the property self._root_node (the property obtains the node by calling self._mem.get_node(self._root_node_page) and asserts the node type).
- If the root node is a LonelyRootNode, return node.max_children // 2.
- Otherwise:
  - Read last_page from self._mem (treated as a numeric page count).
  - Estimate number of leaf pages as int(last_page * 0.70).
  - Estimate average records per leaf as int((node.max_children + node.min_children) / 2).
  - Return the product of those two integer estimates.

This logic is kept as a dedicated method because it is a read-only heuristic relying on multiple persisted metadata fields (root node capacities and memory page count) and must be executed under the memory read-transaction context.

## Args:
    None

## Returns:
    int: Non-negative integer estimate of the number of records in the tree.
         - For a single-node tree (LonelyRootNode): node.max_children // 2.
         - Otherwise: int(last_page * 0.70) * int((node.max_children + node.min_children) / 2).
         - All intermediate calculations use integer conversion; fractional parts are truncated toward zero (floor for positive numbers).
         - If last_page is zero or very small, the returned value may be 0.

## Raises:
    - Any exception propagated from entering or executing the read transaction (exceptions raised by the context manager).
    - AssertionError: if the _root_node property fails its internal type assertion.
    - AttributeError/TypeError: if required attributes or properties (self._mem, self._mem.last_page,
      self._root_node, node.max_children, node.min_children) are missing or of unexpected types.
    (The method itself does not raise custom exceptions; it only propagates exceptions from called properties/attributes.)

## State Changes:
    Attributes READ:
        - self._mem (to open the read transaction and to read last_page)
        - self._root_node (property; which calls self._mem.get_node(self._root_node_page))
        - node.max_children
        - node.min_children
        - self._mem.last_page

    Attributes WRITTEN:
        - None. No attribute of self or external objects is modified.

## Constraints:
    Preconditions:
        - self._mem must be initialized and expose a functioning read_transaction context manager and last_page attribute.
        - self._root_node_page must point to a valid node such that self._root_node returns a node object.
        - node.max_children and node.min_children must be integers.

    Postconditions:
        - No mutation of tree state occurs.
        - The returned integer is a heuristic estimate only and must not be treated as an exact record count.

## Side Effects:
    - Acquires and releases the read transaction on self._mem (read-only).
    - No I/O beyond read-only access to in-memory/on-disk metadata via self._mem.
    - No mutation of objects outside self.

### `bplustree.tree.BPlusTree.__iter__` · *method*

## Summary:
Provides a lazy, read-only iterator over the tree's keys (optionally restricted by a slice). Iteration takes place inside a FileMemory read transaction and does not modify the tree.

## Description:
This method returns a generator that yields keys (record.key) from the tree in sorted order. When called without arguments it iterates all keys; when given a slice it yields keys in the half-open range [slice.start, slice.stop) with no custom step allowed.

Known callers and usage contexts:
- The builtin iter(tree) and for key in tree: constructs call this method (directly or via the keys alias).
- The keys property is an alias for this method.
- __bool__ uses iteration (for _ in self:) to determine emptiness.
- Typical lifecycle: opened BPlusTree instances use this to enumerate keys for read-only operations such as membership tests, scans, exporting keys, or building collections (list(tree), tuple(tree)).

Why this is a distinct method:
- Encapsulates the common pattern of acquiring a read transaction and iterating over records returned by _iter_slice, then projecting to keys. Keeping it separate avoids duplicating the read-transaction + projection logic in other callers (items, values, membership checks, etc.) and provides a clear, memory-efficient keys iterator.

## Args:
    slice_ (Optional[slice]): A Python slice object describing the range to iterate.
        - If None (the default) or any falsy value, the method treats it as slice(None) (iterate all keys).
        - Allowed values: None or a slice instance. The method does not accept a custom step (slice.step must be None).
        - Semantics: start is inclusive, stop is exclusive.

## Returns:
    Iterator[KeyType]: A generator that yields each key stored in the tree that falls within the requested slice.
        - KeyType is the same Python type used for keys in this BPlusTree (e.g., int when the default IntSerializer is used).
        - The iterator is lazy: keys are produced on demand as the generator is consumed.
        - The iteration ends normally (StopIteration) when records are exhausted or when slice_.stop is reached.

## Raises:
    ValueError: If the provided slice has a non-None step (raised by _iter_slice with message 'Cannot iterate with a custom step').
    ValueError: If slice_.start and slice_.stop are both provided and slice_.start >= slice_.stop (raised by _iter_slice with message 'Cannot iterate backwards').
    Any exceptions raised by the underlying FileMemory read_transaction context or by _iter_slice (e.g., I/O errors, ValueErrors) are propagated to the caller.

## State Changes:
Attributes READ:
    self._mem         - used for acquiring the read_transaction and for fetching nodes/pages during iteration
    self._iter_slice  - the method invoked to produce Record objects (method call; not modified)
    (indirectly read by _iter_slice) self._left_record_node, self._root_node and node entries via FileMemory

Attributes WRITTEN:
    None. This method does not modify BPlusTree attributes or stored nodes.

## Constraints:
Preconditions:
    - The tree should be in a usable/open state (the backing FileMemory must be operable). Calling this on a closed tree may cause underlying FileMemory to error (this method does not itself check _is_open).
    - slice_, if provided, must be a slice object; otherwise attribute access to slice_.step etc. will raise an AttributeError.

Postconditions:
    - No mutation of the tree: the tree state (nodes, metadata) remains unchanged.
    - A read transaction on self._mem is opened when the returned generator is advanced for the first time and remains active for the duration of iteration; it is released when iteration completes (generator finishes) or when the generator is discarded/garbage-collected.
    - The caller receives keys in ascending order, limited to [slice.start, slice.stop) when a slice is provided.

## Side Effects:
    - Acquires a read transaction on the backing FileMemory (self._mem.read_transaction). The read transaction may perform I/O (page/node reads) via FileMemory while yielding keys.
    - No writes or external network calls are performed by this method itself.
    - The surrounding read transaction may hold resources (locks) for the lifetime of the generator; callers should exhaust or explicitly close/discard the iterator to ensure timely release of those resources.

### `bplustree.tree.BPlusTree.items` · *method*

## Summary:
Yields (key, value) pairs for records in ascending key order within an optional slice/range; iteration is performed under a read-only memory transaction and returns values as bytes without modifying BPlusTree metadata.

## Description:
- Known callers and context:
    - Used by client code that needs to enumerate records or scan a contiguous key range (for example to construct a dict, export data, or perform read-only analytics).
    - Typical lifecycle stage: read-only access / scanning. It is a public convenience generator analogous to dict.items().
    - The method delegates traversal to _iter_slice and payload resolution to _get_value_from_record; transaction management is handled here to provide a consistent read view.

- Why this logic is a dedicated method:
    - Centralizes the pattern of range-aware traversal combined with resolving a Record's payload while ensuring a single read transaction covers the operation.
    - Prevents duplicating transaction-handling and record-resolution logic across callers.

## Args:
    slice_ (Optional[slice]): A Python slice object that defines a half-open key range [start, stop).
        - Default: None, interpreted as slice(None) — iterate the whole tree.
        - Constraints:
            * slice_.step must be None (custom steps are not supported).
            * If both slice_.start and slice_.stop are provided, slice_.start must be less than slice_.stop (cannot iterate backwards).

## Returns:
    Iterator[tuple]: A generator yielding tuples (key, value) for each record in the specified slice/range, in ascending key order.
        - key: the record key; concrete Python type depends on the tree's serializer (default IntSerializer -> int).
        - value: the record payload as bytes. Inline-stored payloads are returned directly; overflow-stored payloads are assembled and returned as bytes.
        - If no records match the requested range, the iterator yields nothing.

## Raises:
    ValueError:
        - If slice_.step is not None: raised by _iter_slice with message 'Cannot iterate with a custom step'.
        - If both slice_.start and slice_.stop are provided and slice_.start >= slice_.stop: raised by _iter_slice with message 'Cannot iterate backwards'.
    Propagated exceptions:
        - Any exceptions from FileMemory (I/O errors, invalid page references, etc.) or from overflow/page reads propagate to the caller; items() does not convert these exceptions.

## State Changes:
- Attributes READ (self.<attr>):
    - self._mem — to enter a read_transaction and fetch nodes/pages during iteration and overflow reads.
    - self._iter_slice — invoked to obtain Record objects within the requested range.
    - self._get_value_from_record — invoked to translate a Record into its bytes payload (may call _read_from_overflow).
    - Indirectly reads via helpers: self._left_record_node and self._root_node may be accessed by _iter_slice to locate a starting node.
- Attributes WRITTEN (self.<attr>):
    - None. The BPlusTree instance's own attributes (e.g., _root_node_page, _is_open, _tree_conf) are not modified by this method.

- Mutations to retrieved objects (important):
    - During traversal when resolving a start key, _search_in_tree (used by _iter_slice) sets child_node.parent = node while descending the tree. This mutates the Node objects returned by self._mem.get_node. These node-level parent assignments are the only observable writes performed as a side-effect of iteration.

## Constraints:
- Preconditions:
    - The BPlusTree instance must be open (not closed) and its backing FileMemory must be available for reads.
    - The slice_ argument must satisfy the constraints noted under Args.
- Postconditions:
    - No BPlusTree metadata or persistent state is modified.
    - Node objects fetched from the memory may have their parent attributes set (see State Changes).
    - The returned iterator yields records in ascending key order for the requested range.
    - Read resources (the read transaction) remain acquired for the lifetime of the generator until the generator is finalized (see Side Effects / Resource lifetime).

## Side Effects:
    - I/O: Performs read operations on the backing FileMemory while inside a read_transaction, including reading node pages and assembling overflow values.
    - In-memory mutation: Assigns parent references on Node objects returned by self._mem during tree descent performed by _search_in_tree (this does not modify on-disk metadata but does alter in-memory node.parent fields).
    - Resource lifetime note (important):
        - The generator enters a with self._mem.read_transaction: context and yields while inside that context. Consequently, the read transaction remains active while the generator is suspended between yields.
        - If a caller stops iterating early but does not explicitly close or exhaust the generator, the read transaction may remain open until the generator is garbage-collected or explicitly closed.
        - To ensure the read_transaction is released promptly, callers should:
            * fully consume the iterator (e.g., list(tree.items())), or
            * explicitly close the generator with generator.close(), or
            * use contextlib.closing() to ensure the generator is closed, or
            * avoid long-lived partial-consumption patterns that leave the generator object alive.
    - No writes to persistent storage or BPlusTree metadata occur.

### `bplustree.tree.BPlusTree.values` · *method*

## Summary:
Yield the stored payload bytes for every record in a specified key-range (or for the entire tree when no slice is given) without modifying tree state.

## Description:
- Known callers and context:
    - No internal callers within the class that implicitly consume this method; it is intended as a public convenience API for callers who want to iterate over values only (for example, user code calling tree.values()).
    - Conceptually invoked during read-only access patterns and range queries where only stored payloads are required (not keys or full entries).
    - Typical lifecycle: called while the caller expects a stable read view of the tree; the method itself enters the memory layer's read transaction context to provide consistent reads.

- Why this is a separate method:
    - Keeps the traversal logic (handled by _iter_slice) and the value-materialization logic (handled by _get_value_from_record) separated from the user-facing iteration API.
    - Provides a simple, memory-efficient iterator that yields only payload bytes in ascending key order, avoiding the need for callers to extract values from records or tuples themselves.

## Args:
    slice_ (Optional[slice]): A Python slice describing the (half-open) key interval [start, stop).
        - If None or falsy, the entire key range is iterated (equivalent to slice(None)).
        - slice_.start: starting key (inclusive) or None to begin at the smallest key.
        - slice_.stop: end key (exclusive) or None to iterate until the end.
        - slice_.step: must be None. If not None, iteration will raise ValueError (delegated from _iter_slice).

## Returns:
    Iterator[bytes]: A generator yielding bytes objects. Each yielded item is the full payload for a record in ascending key order, reconstructed either from inline record.value or by reading overflow pages when necessary.
    - If the range contains no records, the iterator yields nothing.
    - Always yields bytes objects (never None) for each record that successfully resolves.

## Raises:
    - Propagated exceptions originating from helpers or the memory layer:
        * ValueError:
            - If slice_.step is not None: "Cannot iterate with a custom step" (raised by _iter_slice).
            - If slice_.start and slice_.stop are both provided and slice_.start >= slice_.stop: "Cannot iterate backwards" (raised by _iter_slice).
        * Any exception raised by _get_value_from_record or its called helpers (for example, errors from reading overflow pages, invalid overflow page ids, or I/O errors from the memory backend).
        * Exceptions raised by entering the read transaction context (for example, transaction-related errors from the memory backend).
    - The method itself does not raise new error types beyond those propagated from called components.

## State Changes:
Attributes READ:
    - self._mem: used to enter the read transaction and to fetch node/page data indirectly via called helpers.
    - self._root_node (property) and self._left_record_node (property): may be read indirectly by _iter_slice when determining the starting node for iteration.
Attributes WRITTEN:
    - None on self. The method does not assign to any self.<attr> attributes.

## Constraints:
Preconditions:
    - Caller-supplied slice_.step must be None (enforced by _iter_slice).
    - If both slice_.start and slice_.stop are provided, the caller must ensure slice_.start < slice_.stop (enforced by _iter_slice).
    - Keys used in slice_.start/stop must be comparable against stored entry.key values; no implicit coercion is performed.
    - Caller should expect to obtain values while holding a consistent read view; the method itself opens a read transaction to enforce this.

Postconditions:
    - The tree object and its stored nodes are unchanged by this call.
    - The returned iterator yields the sequence of payload bytes for records whose keys lie in the specified half-open interval, in ascending key order, until the stop bound or end of tree.

## Side Effects:
    - Enters self._mem.read_transaction (a read-only transaction) for the duration of iteration; this may involve the memory backend and influence concurrency/locking behavior.
    - Delegates to _iter_slice which may call _search_in_tree and self._mem.get_node; those calls can load nodes and (internally) set child_node.parent on node objects — this mutates node objects but does not assign attributes on self.
    - Delegates to _get_value_from_record which may read overflow pages via the memory backend; reading pages may incur disk I/O or cache loads.
    - No network I/O, logging, or writes to persistent storage are performed by this method itself.

### `bplustree.tree.BPlusTree.__bool__` · *method*

## Summary:
Return True if the tree contains at least one key, otherwise False; the check stops at the first found key and does not mutate the tree.

## Description:
This method implements the boolean truth-testing protocol for the BPlusTree so Python and user code can use expressions like if tree: or bool(tree). It performs a minimal existence check by attempting to obtain the first key from the tree and returning immediately if one is found.

Known callers / contexts:
- Implicitly invoked by Python in truth-testing contexts (if, while, bool(), not).
- Can be called explicitly by user code as bool(tree).
- May be used by higher-level utilities or tests that treat the tree as a container and test it for emptiness.

Why a separate method:
- Encapsulates an efficient, semantic "non-empty" test that short-circuits on first key rather than computing length.
- Centralizes the required memory-transaction handling so callers do not need to replicate transaction logic.

## Args:
    None

## Returns:
    bool: 
        - True: if at least one key exists in the tree. This happens as soon as iteration yields a key.
        - False: if iteration yields no keys (tree is empty).
    Edge behavior:
        - If an exception occurs while acquiring the read transaction or during iteration, that exception propagates and no boolean is returned.

## Raises:
    - Any exception raised by the memory backend when entering or exiting self._mem.read_transaction (e.g., I/O, transaction errors) will propagate.
    - Any exception raised by iteration over the tree also propagates. Example sources of such exceptions include:
        * Exceptions from FileMemory.get_node / get_page called during iteration.
        * ValueError raised by internals if internal metadata is corrupt.
      Note: under normal operation with an initialized tree and the default slice(None) iteration path, iteration does not raise ValueError from slice checks.

## State Changes:
Attributes READ:
    - self._mem: used to acquire the read_transaction context manager and to fetch nodes/pages during iteration.
    - Transitive reads performed by the iteration invoked inside __bool__:
        * self._root_node (property): may call self._mem.get_node(self._root_node_page) to obtain the root node.
        * self._left_record_node (property): may traverse nodes via self._mem.get_node(...) to find the leftmost leaf.
        * Node entries accessed via node.entries during _iter_slice (to obtain the first record/key).
      These reads happen indirectly because __bool__ iterates (for _ in self), which delegates to __iter__ and _iter_slice.

Attributes WRITTEN:
    - None. This method does not modify any attributes on self.

## Constraints:
Preconditions:
    - self must be a properly initialized BPlusTree instance with a valid memory backend assigned to self._mem.
    - The memory backend must provide a read_transaction context manager.
    - Important: __bool__ opens a read transaction and then iterates by calling self.__iter__ (which itself also acquires self._mem.read_transaction). Therefore the memory backend should tolerate nested acquisition of read_transaction (for example by returning the same transaction context for nested enters or by being reentrant). If the backend does not support nested read transactions, calling bool(tree) may raise or deadlock.

Postconditions:
    - No mutation of the tree or its metadata is performed.
    - The read transaction opened by this method is exited (the context manager is left) before the method returns or before any propagated exception escapes.

## Side Effects:
    - Acquires and releases a read transaction on the FileMemory backend; this may trigger internal reads from disk or cache depending on the backend implementation.
    - No writes, external I/O writes, or mutations to objects outside self are performed by this method.

### `bplustree.tree.BPlusTree.__repr__` · *method*

## Summary:
Return a concise developer-facing string that identifies this B+ tree instance by its filename and TreeConf; does not modify the object's state.

## Description:
- Known callers and contexts:
    - This method is the object's Python representation hook and is invoked implicitly by built-in functions and contexts such as repr(obj), print(obj) (when Python falls back to repr for printing objects without __str__), debuggers, and logging/formatting routines that request the object's representation.
    - There are no explicit direct calls to this method inside the BPlusTree class implementation provided; it exists to satisfy Python's data model and to provide a stable, single place to customize the textual representation of the tree.
- Why this logic is its own method:
    - __repr__ is the standard Python hook for obtaining an unambiguous, developer-focused textual representation of an object. Implementing it as a dedicated method centralizes the representation logic (filename + configuration) so that any external tooling or debugging that needs a short identifying string uses a consistent format.

## Args:
    None

## Returns:
    str: A string of the form "<BPlusTree: {filename} {tree_conf}>"
    - filename is taken from self._filename and is expected to be a string (or an object whose str() is meaningful).
    - tree_conf is taken from self._tree_conf and is represented using its own textual representation (its __repr__ or __str__); the returned string concatenates these two pieces inside the angle-bracket wrapper shown above.
    - Edge cases:
        - If self._tree_conf or self._filename are present but have unusual __repr__/__str__ implementations, their output appears verbatim inside the returned string.
        - If either attribute is missing (AttributeError) or their formatting raises an exception, that exception will propagate (see Raises).

## Raises:
    AttributeError: If self._filename or self._tree_conf attributes do not exist on the instance.
    Any exception raised by formatting/representation of self._filename or self._tree_conf (these will propagate out of the method).

## State Changes:
- Attributes READ:
    - self._filename
    - self._tree_conf
- Attributes WRITTEN:
    - None

## Constraints:
- Preconditions:
    - The instance must have attributes _filename and _tree_conf already set (the BPlusTree.__init__ establishes these).
    - The caller should expect a synchronous, side-effect-free call — no locks, no I/O required by this method.
- Postconditions:
    - The object state is unchanged after the call.
    - A str as described in Returns is produced (unless an exception is raised).

## Side Effects:
    - None. The method performs no I/O, external service calls, or mutations to self or other objects; it simply formats and returns a string.

### `bplustree.tree.BPlusTree._initialize_empty_tree` · *method*

## Summary:
Create and persist an initial lonely root node on the tree's next available page and record that page and the current tree configuration in persistent metadata, updating the BPlusTree instance state.

## Description:
This method is invoked by BPlusTree.__init__ when the underlying FileMemory has no metadata (the call to get_metadata raised ValueError), i.e., when constructing a brand-new/empty tree. It performs the allocation of a root page, writes an initial LonelyRootNode into storage inside a write transaction, and then stores the root page and TreeConf as the tree metadata.

This logic is isolated into its own method because it groups the page allocation, node creation (a durable write performed inside a write transaction), and metadata persistence into a single, reusable unit. Separating these steps keeps the constructor concise and makes the initialization sequence testable, atomic (for the node write via the write_transaction), and easy to reason about.

## Args:
    None

## Returns:
    None

## Raises:
    This method does not explicitly raise exceptions itself. Any exceptions raised by the underlying FileMemory operations (accessing next_available_page, entering or executing the write_transaction, set_node, or set_metadata) will propagate out to the caller.

## State Changes:
Attributes READ:
    - self._mem (FileMemory): used for next_available_page, write_transaction, set_node, and set_metadata.
    - self._mem.next_available_page (int): read to determine the page allocated for the root.
    - self.LonelyRootNode (callable/partial): read to construct the initial root node instance.
    - self._tree_conf (TreeConf): read when persisting metadata.

Attributes WRITTEN:
    - self._root_node_page (int): assigned to the value returned by self._mem.next_available_page.

Additionally, persistent state outside of self is modified:
    - FileMemory.set_node(...) is called to persist the LonelyRootNode at the allocated page.
    - FileMemory.set_metadata(self._root_node_page, self._tree_conf) is called to persist tree metadata.

## Constraints:
Preconditions:
    - self._mem must be a valid, initialized FileMemory instance.
    - self.LonelyRootNode must be a callable (the partial created by _create_partials) that accepts a page keyword argument.
    - self._tree_conf must be initialized to a valid TreeConf instance.
    - The caller should expect that FileMemory operations may perform I/O and may raise exceptions.

Postconditions:
    - self._root_node_page equals the page number obtained from self._mem.next_available_page at the time of the call.
    - The persistent page identified by self._root_node_page contains a LonelyRootNode instance (written via set_node inside the write transaction).
    - The persistent metadata is set to the tuple (self._root_node_page, self._tree_conf) via set_metadata.
    - The in-memory BPlusTree state reflects the root page allocation; no other BPlusTree attributes are modified by this method.

Important ordering note:
    - set_node(...) is executed inside the FileMemory.write_transaction context manager, while set_metadata(...) is called after leaving that context. If set_metadata raises after set_node completed, the persistent node may exist without updated metadata; callers should be prepared to handle or report such failures.

## Side Effects:
    - Allocates/consumes the next available page number from FileMemory.
    - Writes a new LonelyRootNode to persistent storage via FileMemory.set_node.
    - Writes/updates persistent tree metadata via FileMemory.set_metadata.
    - No network I/O is performed by this method itself, but FileMemory may perform disk I/O; there are no returns that reference external objects (only in-memory assignment of _root_node_page).

### `bplustree.tree.BPlusTree._create_partials` · *method*

## Summary:
Create and assign callable factory partials on the instance that bind the tree configuration to node and entry classes, so later code can instantiate nodes/entries without passing the TreeConf explicitly.

## Description:
Known callers and context:
- BPlusTree.__init__: invoked immediately after self._tree_conf is created during tree construction. This is the only call site in the class; the method runs during the object's initialization lifecycle so all later operations can use the bound factories (e.g., self.Record(...), self.LeafNode(...)).
- Although not used elsewhere in the current codebase, the method is separated so it can be re-run if the tree configuration changes and the instance needs its factories rebound.

Why this is its own method:
- Encapsulates the one-time binding of the TreeConf to node/entry constructors, keeping __init__ concise and making the binding logic reusable (idempotent and safe to call again).
- Avoids passing the TreeConf repeatedly throughout the class by exposing concise instance attributes that act as class factories.

## Args:
    None

## Returns:
    None

## Raises:
    AttributeError: If self._tree_conf is not set on the instance when called (accessing self._tree_conf will raise).
    NameError: If any of the referenced class names (LonelyRootNode, RootNode, InternalNode, LeafNode, Record, Reference) are not available in the module scope when this method executes.
    (These exceptions are raised implicitly by attribute lookup / name resolution; the method does not explicitly raise errors.)

## State Changes:
Attributes READ:
    - self._tree_conf

Attributes WRITTEN:
    - self.LonelyRootNode: set to functools.partial(LonelyRootNode, self._tree_conf)
    - self.RootNode: set to functools.partial(RootNode, self._tree_conf)
    - self.InternalNode: set to functools.partial(InternalNode, self._tree_conf)
    - self.LeafNode: set to functools.partial(LeafNode, self._tree_conf)
    - self.Record: set to functools.partial(Record, self._tree_conf)
    - self.Reference: set to functools.partial(Reference, self._tree_conf)

Note: Calling the method again will overwrite any existing values for these attributes.

## Constraints:
Preconditions:
    - self._tree_conf must be initialized and hold a valid TreeConf instance before calling.
    - The classes LonelyRootNode, RootNode, InternalNode, LeafNode, Record, and Reference must be importable/defined in the module scope.

Postconditions:
    - Each of the six attributes listed above is a functools.partial object whose first (pre-bound) argument is the instance's TreeConf. These partials are callable and behave like the original constructors with the TreeConf argument pre-supplied (i.e., calling self.LeafNode(page=...) is equivalent to LeafNode(self._tree_conf, page=...)).
    - The instance can use self.Record, self.Reference, and node factory attributes throughout its methods without manually supplying TreeConf.

## Side Effects:
    - No I/O, no filesystem, and no external service calls.
    - Only mutates attributes of self (as listed under Attributes WRITTEN).
    - No other objects are mutated.

### `bplustree.tree.BPlusTree._root_node` · *method*

## Summary:
Returns the current root node object for the tree by loading it from the tree's backing memory; does not mutate BPlusTree state.

## Description:
This read-only property fetches the node stored at the page indicated by the tree's _root_node_page and returns it as either a LonelyRootNode (tree contains a single leaf/root) or a RootNode (internal root with children). It is a thin accessor that centralizes the logic for retrieving and type-checking the root node so callers need not repeatedly call the memory layer or re-check types.

Known callers and call contexts:
- insert: used to obtain the root when searching for the insertion point; typically invoked inside a write transaction.
- batch_insert: used to locate the starting leaf for bulk insertions; typically invoked inside a write transaction.
- get: used to find the leaf node containing the requested key; invoked inside a read transaction.
- __length_hint__: used to inspect the root in order to estimate size; invoked inside a read transaction.
- _left_record_node (property): obtains the root as the starting point for descending to the leftmost leaf.
- _iter_slice: used when starting iteration from a specific key; invoked inside a read transaction.
- _search_in_tree: callers pass self._root_node as the initial node for recursive descent.

Why this is a separate method:
- Encapsulates the memory layer call and a runtime type assertion in a single place.
- Ensures all callers receive a node of the expected root types and reduces duplication of get_node + type-checking logic across the class.
- Keeps intent explicit (accessing the root) rather than inlining page lookups.

## Args:
    None

## Returns:
    Union[LonelyRootNode, RootNode]: The node instance loaded from backing memory at page self._root_node_page.
    - Typical return values:
        - LonelyRootNode: when the tree currently has a single-node tree (root is also a leaf).
        - RootNode: when the root is an internal node (has children).
    - Edge cases:
        - If the page referenced by self._root_node_page refers to an unexpected node type, an AssertionError will be raised (see Raises).
        - Any errors raised by the underlying memory layer (self._mem.get_node) propagate to the caller.

## Raises:
    AssertionError: If the object returned by self._mem.get_node(self._root_node_page) is not an instance of LonelyRootNode or RootNode.
    (Other exceptions raised by self._mem.get_node, such as those for invalid pages or I/O errors, are not handled here and will propagate.)

## State Changes:
    Attributes READ:
        - self._mem
        - self._root_node_page
    Attributes WRITTEN:
        - None (this property does not modify BPlusTree attributes)

## Constraints:
    Preconditions:
        - self._mem must be initialized (FileMemory instance created).
        - self._root_node_page must be set to a valid page number (this is guaranteed by constructor or by _initialize_empty_tree and maintained by methods that create a new root).
        - In normal usage callers access this property while inside a memory transaction (read or write) to ensure consistent reads; the code does not enforce a transaction here, but many callers acquire one.

    Postconditions:
        - Returns a live node object corresponding to the root page.
        - No attributes of self are modified by this call.

## Side Effects:
    - Invokes self._mem.get_node(self._root_node_page), which may perform I/O (load page(s) from disk or cache) or other memory-layer operations; those effects depend on FileMemory implementation and are not hidden by this accessor.
    - No other external side effects or mutations outside of potential memory-layer read activity.

### `bplustree.tree.BPlusTree._left_record_node` · *method*

## Summary:
Returns the leftmost node that can contain records (either the unique root leaf or the leftmost leaf) by walking down from the current root; does not modify tree state.

## Description:
This property-like helper locates the leftmost record-containing node in the tree by repeatedly following the smallest child reference from the root until a LeafNode or LonelyRootNode is reached.

Known callers and contexts where it is invoked:
- __len__: used to start counting records from the leftmost leaf (invoked inside a read transaction).
- _iter_slice: when slice_.start is None, used to begin iteration from the leftmost leaf (invoked inside a read transaction). By extension, __iter__, keys, items, values, and __bool__ (which iterate over the tree) indirectly rely on this method when iterating from the beginning.
- Any other internal routine that needs to start a scan from the leftmost records may use this helper.

Why this logic is a separate method:
- The traversal from root to the leftmost leaf is a reusable operation needed in multiple higher-level read operations (length, iteration). Encapsulating it avoids duplicated traversal code and centralizes the assumption about how to descend along the smallest-entry references.

## Args:
    None

## Returns:
    Union[LonelyRootNode, LeafNode]:
        - The node instance at the far left of the tree that may contain records.
        - Guaranteed (by the function's loop condition) to be an instance of either LonelyRootNode or LeafNode as soon as it returns.
        - The returned node may contain zero or more entries.

## Raises:
    - This method contains no explicit raises in its body. However, it may propagate exceptions raised by called operations, for example:
        - Any exception raised by self._mem.get_node (propagated as-is).
        - AttributeError (or similar) if a node encountered during traversal lacks the expected attributes (e.g., smallest_entry or its 'before' field) — this would indicate a corrupted or malformed node structure.
    Note: callers typically invoke this method inside memory read transactions; transaction-related errors from the memory layer may also propagate.

## State Changes:
    Attributes READ:
        - self._root_node (property access; reads memory to obtain the current root node)
        - self._mem (used to call get_node during traversal)
    Attributes WRITTEN:
        - None (this method does not assign to any self.* attribute)

## Constraints:
    Preconditions:
        - self._mem must be initialized and able to serve get_node requests (normally set in __init__).
        - self._root_node_page (used by the _root_node property) must reference a valid page; the tree must have a valid root node.
        - Nodes in the path from root to a leaf must expose smallest_entry and its 'before' reference when they are not LeafNode/LonelyRootNode.
    Postconditions:
        - The tree object is unchanged by this call.
        - The return value is an instance of LonelyRootNode or LeafNode representing the leftmost node reachable from the current root.

## Side Effects:
    - Calls self._mem.get_node(page) repeatedly while descending. Depending on the memory backend, these calls may perform read I/O, cache lookups, or raise memory-layer exceptions.
    - No mutation of nodes or metadata; the method is read-only with respect to the BPlusTree state.

### `bplustree.tree.BPlusTree._iter_slice` · *method*

## Summary:
Generate and yield record entries from the tree in ascending key order for the half-open interval [slice.start, slice.stop); the call does not assign to BPlusTree attributes.

## Description:
- Callers found in repository snapshot: none directly reference this private helper. It is intended to be invoked by higher-level range/slice query logic that needs an iterator over records within a key interval.
- What it does: positions a starting leaf node (leftmost when start is None, otherwise by descending the tree via _search_in_tree) and then linearly scans forward through leaf pages, yielding each entry whose key satisfies the requested bounds.
- Why a separate method: separates the concerns of (a) locating the initial leaf for a given start key and (b) performing the linear forward scan across consecutive leaf pages. This enables reuse by any slice/range API and keeps navigation logic distinct from public API wiring.

## Args:
    slice_ (slice): A Python slice object describing the requested interval.
        - slice_.start: None or a key value comparable to entry.key. If None, iteration begins at the tree's smallest key (leftmost record node).
        - slice_.stop: None or a key value comparable to entry.key. If None, iteration continues until the end of the tree.
        - slice_.step: Must be None. If not None, the method raises ValueError with message "Cannot iterate with a custom step".

## Returns:
    Iterator[Record]: A generator that yields the entries stored in leaf nodes (the method's annotation is Iterator[Record]). The yielded elements come from node.entries and are produced in ascending key order. Yielding semantics:
        - If slice_.start is provided, produced entries satisfy entry.key >= slice_.start.
        - If slice_.stop is provided, produced entries satisfy entry.key < slice_.stop (stop is exclusive).
        - Iteration ends by raising StopIteration when the stop bound is reached or no further leaf pages exist.

## Raises:
    ValueError:
        - If slice_.step is not None: "Cannot iterate with a custom step"
        - If both slice_.start and slice_.stop are not None and slice_.start >= slice_.stop: "Cannot iterate backwards"
    StopIteration:
        - Used internally to terminate the generator when the stop bound is reached or when there are no further leaf pages (node.next_page is falsy).
    AssertionError:
        - Propagated if _search_in_tree fails its structural assertion (it asserts that a child page id is found). This indicates a corrupt or inconsistent tree structure.
    Propagated exceptions:
        - The method does not perform defensive checks for missing attributes or incompatible key comparisons. AttributeError, TypeError, or other exceptions raised during comparison or node access will propagate to the caller.

## State Changes:
Attributes READ:
    - self._left_record_node: read when slice_.start is None to obtain the leftmost leaf node.
    - self._root_node: read when slice_.start is not None and passed into _search_in_tree.
    - self._mem: read to call self._mem.get_node(page) when following next_page or descending the tree.

Attributes WRITTEN:
    - This method assigns no attributes on self.
    - Note: _search_in_tree (called when start is not None) sets child_node.parent = node; that is a mutation on node objects, not on top-level self attributes.

## Constraints:
Preconditions:
    - slice_.step must be None (enforced by code).
    - If both slice_.start and slice_.stop are provided, they must compare such that slice_.start < slice_.stop (enforced by code).
    - Keys provided in slice_.start/stop must be comparable with the entry.key values stored in nodes; the method does not coerce or validate types.
    - The tree should contain leaf nodes (self._left_record_node should be a valid leaf node) for full traversal from the leftmost edge.

Postconditions:
    - No attributes on self are changed by the method.
    - The returned iterator yields a sequence of node.entries satisfying the range bounds; iteration finishes when the stop condition is reached or when the final leaf is exhausted.

## Side Effects:
    - Calls self._search_in_tree(start, self._root_node) when start is provided; that helper will recursively call self._mem.get_node(page) and set child_node.parent = node while descending.
    - Calls self._mem.get_node(node.next_page) to load subsequent leaf nodes while scanning. Depending on the memory/storage backend, these calls may perform disk I/O or allocate in-memory node objects.
    - No network I/O or external service calls originate from this method itself.

## Complexity:
    - Time: O(h + r) where h is the tree height (cost to descend with _search_in_tree when start is provided) and r is the number of records yielded.
    - Space: O(1) additional working memory; nodes loaded via self._mem.get_node are provided by the memory backend.

## Implementation notes and edge behaviors:
    - The stop bound is exclusive: entry.key >= slice_.stop stops iteration.
    - The method relies on node.entries being an iterable of objects exposing a key attribute used for comparisons.
    - If the tree structure is inconsistent (missing a child page during descent), _search_in_tree's assertion will trigger AssertionError.
    - The method intentionally rejects slice.step to keep iteration semantics simple and to preserve ascending-order scanning.

### `bplustree.tree.BPlusTree._search_in_tree` · *method*

## Summary:
Traverse down the internal nodes from a given starting node to locate and return the leaf (or lonely-root) node that should contain the provided key, establishing parent links for each child visited.

## Description:
This recursive helper performs the core B+ tree traversal step: given a key and a node (typically the root or another internal node), it selects the appropriate child pointer (page) and descends until a leaf or lonely-root node is reached. It sets the parent attribute on each child it loads during traversal.

Known callers and typical context:
- Search operations (e.g., public lookup methods): invoked as the traversal phase to find the leaf that should contain a key.
- Insert or delete operations: used during the locate-step to find the target leaf for insertion or removal.
- Split/merge helpers: used when an operation needs to locate a specific leaf or descendant node.

This logic is separated into its own method because:
- It centralizes the child-selection and descent logic, which is used by multiple higher-level operations (search, insert, delete).
- It maintains parent pointers across dynamic node loads in one place.
- It keeps recursion and boundary/inclusive/exclusive comparison semantics consistent and isolated from higher-level logic.

## Args:
    key: comparable
        The search key; must support comparison operations with node keys (<= and <). No specific numeric/string type is enforced: any object implementing the comparison operators used below is acceptable.
    node: Node
        The node from which to start traversal. Expected to be an InternalNode or Root-like internal node when descent is required; if a LeafNode or LonelyRootNode is passed, the method immediately returns it.

## Returns:
    Node
        The leaf or lonely-root node where the key belongs (i.e., the node that should contain the key or the place for insertion). The returned node will have its parent attribute set (unless it is the starting node and is a leaf/lonely root). Possible return values:
        - If the input node is a LeafNode or LonelyRootNode, that same node is returned unchanged.
        - Otherwise, the returned value is a descendant LeafNode or LonelyRootNode reached by following child pointers.

## Raises:
    AssertionError
        Raised if the method cannot determine a child page to follow (i.e., the internal node's entries and boundary entries do not yield a page). This indicates corrupted or inconsistent node state (missing entries or pointers).
    TypeError (or other comparison-related exception)
        If 'key' is not comparable to the node's stored keys, Python may raise a TypeError during comparisons.
    Any exception raised by self._mem.get_node(page)
        For example, an I/O or validation error if the page reference is invalid or the memory layer fails to load the node.

## State Changes:
Attributes READ:
    self._mem
        The memory manager is accessed in order to load child nodes via get_node(page).

Attributes WRITTEN:
    (none on self)
        This method does not modify attributes on self.

Non-self mutations (side effects on returned/loaded nodes):
    - child_node.parent is set to the parent node each time a child node is loaded. As the recursion proceeds, the parent pointers for all nodes along the visited path from the starting node down to the returned leaf will be assigned.

## Constraints:
Preconditions:
    - The 'node' argument must be a valid tree node object exposing:
        * smallest_key (comparable)
        * biggest_key (comparable)
        * smallest_entry and biggest_entry attributes, each exposing .before and .after page references respectively
        * entries: an iterable sequence of Reference-like objects, where each reference has at least .key and .after attributes
      These properties must reflect a consistent internal node: smallest_entry.before, biggest_entry.after, and the entries iterable must collectively cover all child pointers.
    - Keys stored in node entries and the provided 'key' must support the comparison operations used:
        * key < node.smallest_key
        * node.biggest_key <= key
        * ref_a.key <= key < ref_b.key
    - self._mem must implement get_node(page) and return a Node instance for valid page references.

Postconditions:
    - The returned object is a LeafNode or a LonelyRootNode that should contain (or be the place for) the key.
    - For every internal node visited during traversal (starting node's children, grandchildren, etc.), the child node's parent attribute will be set to the node from which it was loaded.
    - No attributes on self are modified.

## Side Effects:
    - Loads nodes via self._mem.get_node(page) (memory layer access / potential I/O).
    - Mutates parent attributes on nodes returned from the memory layer (child_node.parent = node).
    - May trigger exceptions propagated from the memory layer (e.g., corrupt/invalid page).
    - No external network I/O is performed by this method itself beyond interactions with the in-process memory abstraction.

### `bplustree.tree.BPlusTree._split_leaf` · *method*

## Summary:
Splits an overflowing leaf node by creating a new sibling leaf, moving entries produced by the leaf's split operation into it, creating a parent Reference for the sibling, and persisting the changed nodes via the tree memory.

## Description:
This method is invoked during the tree's insertion pathway when a leaf node must be split due to overflow. The implementation steps visible in the code are:
- Read the parent of the target leaf (old_node.parent).
- Create a new leaf node by calling the tree's LeafNode constructor with page=self._mem.next_available_page and next_page=old_node.next_page.
- Call old_node.split_entries() and assign its return value to new_node.entries.
- Construct a Reference by calling self.Reference(new_node.smallest_key, old_node.page, new_node.page).
- If old_node is a LonelyRootNode:
    * Replace old_node by calling old_node.convert_to_leaf() and create a new root by invoking self._create_new_root(ref).
  Else:
    * Insert the reference into parent via parent.insert_entry(ref).
    * If parent.can_add_entry is True, persist parent with self._mem.set_node(parent).
    * Otherwise, call self._split_parent(parent) to handle parent overflow.
- Update old_node.next_page to new_node.page.
- Persist old_node and new_node by calling self._mem.set_node(old_node) and self._mem.set_node(new_node).

This logic is separated into its own method because it encapsulates the leaf-splitting control flow and the specific sequence of allocations, entry movement, parent updates, and persistence calls expressed above.

Known callers / lifecycle stage:
- Called when a leaf node overflows during insertion (i.e., from insertion logic that detects a full leaf and invokes the split routine).

## Args:
    old_node (Node): The leaf node instance to split.
        - Required; no default.
        - The method accesses these attributes/methods on old_node: parent, page, next_page, split_entries(), and convert_to_leaf() (the latter only if old_node is a LonelyRootNode).

## Returns:
    None

## Raises:
    - The method contains no explicit raise statements.
    - Exceptions raised by invoked methods (e.g., old_node.split_entries(), old_node.convert_to_leaf(), parent.insert_entry(), self._create_new_root(), self._split_parent(), or self._mem.set_node()) propagate unchanged.

## State Changes:
    Attributes READ (explicit in the method body):
        - old_node.parent
        - old_node.page
        - old_node.next_page
        - new_node.smallest_key
        - parent.can_add_entry
        - self._mem.next_available_page
        - self.LeafNode (used as constructor)
        - self.Reference (used as constructor)

    Attributes WRITTEN / Mutated (explicit assignments or calls that persist state):
        - new_node.entries is assigned the value returned by old_node.split_entries()
        - old_node.next_page is assigned new_node.page
        - parent is modified by parent.insert_entry(ref) (and may be persisted)
        - Calls to self._mem.set_node(...) persist changes to:
            * parent (when parent.can_add_entry is True and parent was updated here)
            * old_node (persisted after next_page update)
            * new_node (persisted after construction and entries assignment)
        - Possible tree-topology changes via calls to:
            * old_node.convert_to_leaf()
            * self._create_new_root(ref)
            * self._split_parent(parent)

## Constraints:
    Preconditions (requirements observable from the code):
        - old_node must implement page, next_page, parent, and split_entries().
        - self._mem must provide next_available_page and set_node(...) attributes/methods.
        - If old_node is not a LonelyRootNode, old_node.parent is expected to be a valid parent node object (the code uses parent after reading old_node.parent).

    Postconditions (guarantees observable from the code):
        - A new LeafNode instance (new_node) is created and assigned entries from old_node.split_entries().
        - old_node.next_page is updated to refer to new_node.page.
        - A Reference object is constructed and either inserted into the parent or used to create a new root.
        - self._mem.set_node(...) is called for old_node and new_node; self._mem.set_node(parent) may be called if parent.can_add_entry was True.

## Side Effects:
    - Allocates a new leaf by using self._mem.next_available_page as the page argument to LeafNode (the method reads this attribute).
    - Persists nodes by calling self._mem.set_node(...) for nodes modified here (parent when written directly, old_node, and new_node).
    - Invokes routines that may alter tree topology: old_node.convert_to_leaf(), self._create_new_root(ref), and self._split_parent(parent).
    - The method does not perform direct file or network I/O itself beyond calls made through the memory abstraction (self._mem.set_node).

### `bplustree.tree.BPlusTree._split_parent` · *method*

## Summary:
Promotes the result of splitting a node into its parent by creating a new internal sibling on a fresh page, building a separator/reference that links the two siblings, and persisting the affected nodes (or creating a new root if the split was at the root).

## Description:
This private helper is used during split handling when a node's entries must be split and a separator reference produced by that split needs to be inserted into the parent. Typical callers and context:
- Invoked from split routines triggered by insert operations when a leaf or internal node overflows and a separator must be promoted to the parent (for example: invoked by _split_leaf or other internal split handlers).
- It implements the local steps required to create a right sibling for old_node, obtain the separator Reference from the new sibling, link the separator to the two sibling pages, and then insert that separator into the parent or create a new root when splitting the current root.

Why this logic is a separate method:
- Centralizes the sibling-creation + promotion + persistence pattern used when any node is split. This avoids duplicating parent-insertion and recursion logic across leaf/internal split handlers and centralizes calls to the memory persistence layer for the nodes involved.

## Args:
    old_node (Node): The node being split. Expected to have:
        - parent: reference to its parent node (may be None if old_node is a RootNode)
        - page: integer page identifier
        - split_entries() -> iterable: returns the entries intended for the new sibling (contract described under Preconditions)
    No default values.

## Returns:
    None

## Raises:
    AttributeError: If required attributes or methods are missing (for example, if old_node lacks .parent or .page, or if self._mem or self.InternalNode are missing).
    Any exception raised by the called methods will propagate:
        - self.InternalNode(page=...) construction
        - old_node.split_entries()
        - new_node.pop_smallest()
        - old_node.convert_to_internal() when old_node is a RootNode
        - parent.insert_entry(ref) or access to parent.can_add_entry
        - self._create_new_root(ref)
        - self._mem.set_node(node)
    Note: If parent is None and old_node is not a RootNode, accessing parent.can_add_entry will raise an AttributeError.

## State Changes:
Attributes READ:
    - old_node.parent (assigned to local variable parent)
    - old_node.page (used to set reference.before)
    - self._mem.next_available_page (used as the page argument to create the new InternalNode)
    - isinstance(old_node, RootNode) (type check)
    - parent.can_add_entry (in the non-root branch, to decide insert vs recurse)

Attributes WRITTEN / MUTATED:
    - new_node.entries is set to the iterable returned by old_node.split_entries()
    - ref.before and ref.after are set to old_node.page and new_node.page, respectively
    - parent entries are mutated by parent.insert_entry(ref) when parent.insert_entry is called
    - old_node may be rebound in the local scope to the result of old_node.convert_to_internal() when old_node is a RootNode (the converted node object is then persisted)
    - Persistence calls mutate external state via self._mem.set_node(...) for:
        * parent (only in the branch where parent.can_add_entry is True)
        * old_node (always called at end of this method)
        * new_node (always called at end of this method)
    - self._create_new_root(ref) may mutate tree-level state (e.g., root page and metadata) — exact effects depend on that helper

## Constraints:
Preconditions:
    - old_node must provide:
        * a .page integer attribute
        * a .split_entries() callable that returns the entries to place in the new sibling. The minimal contract assumed by this method is that the returned value can be assigned to new_node.entries and will later allow new_node.pop_smallest() to return a valid Reference. Whether split_entries mutates old_node (removes those entries) is part of the split_entries contract and is not assumed here; callers and implementers must ensure the overall split semantics leave old_node and new_node representing left/right halves before persistence.
        * a .parent attribute when old_node is not an instance of RootNode
    - self.InternalNode must be callable with a page keyword and produce an object with at least .entries and pop_smallest() attributes/methods and a .page attribute.
    - self._mem must expose next_available_page and set_node(node).
    - The Reference object returned by new_node.pop_smallest() must accept assignment to .before and .after and must be acceptable to parent.insert_entry(ref) or to _create_new_root(ref).
    - If old_node is not a RootNode, parent must be non-None and implement can_add_entry and insert_entry(ref).

Postconditions:
    - A new InternalNode instance is created and assigned entries returned by old_node.split_entries(), then persisted via self._mem.set_node(new_node).
    - A Reference (separator) obtained via new_node.pop_smallest() is updated so:
        * ref.before == old_node.page
        * ref.after == new_node.page
    - old_node and new_node are persisted via self._mem.set_node(old_node) and self._mem.set_node(new_node) before the method returns.
    - One of the following holds after this method returns successfully:
        * If old_node was a RootNode: _create_new_root(ref) was called (caller/that helper determines root metadata updates).
        * Else if parent.can_add_entry evaluated to True: parent.insert_entry(ref) was called and parent was persisted via self._mem.set_node(parent).
        * Else: parent.insert_entry(ref) was called and _split_parent(parent) was invoked to continue upward split propagation (persistence of the parent will occur by that recursive call chain or by its branch logic).

## Side Effects:
    - Calls self._mem.set_node(...) for old_node and new_node (always) and parent (in the immediate insert-into-parent branch). These calls delegate persistence to the memory layer and may perform I/O depending on the memory implementation.
    - Reads self._mem.next_available_page to obtain the page id for the new sibling. The memory layer's semantics for whether this read reserves or merely reports the next page id are defined by the memory implementation and not by this method.
    - May invoke self._create_new_root(ref), which updates tree-level metadata and persists it (effects depend on that helper).
    - No direct network or external service calls are made by this method itself; any I/O is via the memory manager API.

### `bplustree.tree.BPlusTree._create_new_root` · *method*

## Summary:
Create and persist a new root node on the next available page and update the tree to reference that page.

## Description:
This private helper allocates a new root node instance using the memory manager's next available page number, inserts the provided page reference into that root node, updates the B+ tree's recorded root page, and persists the new root and its metadata to the FileMemory.

Known callers and typical invocation context:
- Called when the tree has no root yet (initial tree creation) or when a split operation requires promoting a reference to a newly-created root. Typical callers are higher-level insertion or split-handling logic in the BPlusTree implementation (for example: initial insert into an empty tree, or a root split routine).

Why this logic is a separate method:
- Centralizes the sequence of operations required to create and persist a root (allocate page, insert reference, update in-memory pointer, write metadata, write node). Keeping this separate removes duplication wherever a new root must be created and ensures consistent persistence semantics.

## Args:
    reference (Reference): A Reference/child pointer object (from entry.Reference) that should be inserted into the newly-created root node. Must be a fully-formed reference suitable for insertion into a root node (e.g., containing a page id and/or key as required by the Reference implementation).

## Returns:
    None

## Raises:
    AttributeError: If expected attributes on self are missing (for example, if self._mem or self.RootNode are not present), the attribute access will raise AttributeError.
    Any exception raised by RootNode(page=...) construction, RootNode.insert_entry(reference), self._mem.set_metadata(...) or self._mem.set_node(...) will propagate (for example, if the memory layer validates inputs and raises).

## State Changes:
Attributes READ:
    self.RootNode - the root node class/factory used to construct the new root node.
    self._mem - the memory manager (used to obtain next_available_page and to persist metadata and node).
    self._mem.next_available_page - value read to determine which page to allocate for the new root.
    self._tree_conf - tree configuration object passed to the memory layer when persisting metadata.

Attributes WRITTEN:
    self._root_node_page - set to the newly-created root node's page number.

## Constraints:
Preconditions:
    - self._mem must expose a next_available_page (readable) and methods set_metadata(page, tree_conf) and set_node(node).
    - self.RootNode must be callable/constructible with a page keyword argument and must produce an object with:
        * a .page attribute identifying the page number
        * an insert_entry(reference) method that accepts the provided Reference
    - reference must be a Reference instance acceptable to RootNode.insert_entry.

Postconditions:
    - A RootNode object has been constructed and persisted to memory via self._mem.set_node.
    - self._root_node_page equals the page number allocated for the new root (new_root.page).
    - self._mem has been instructed to store metadata for that page using self._tree_conf.
    - No return value (None). Any failure will leave the tree in whichever partial state the underlying operations reached (exceptions propagate).

## Side Effects:
    - Allocates/claims a new page number from the memory manager (reads next_available_page).
    - Mutates in-memory tree state by setting self._root_node_page.
    - Persists metadata for the new root page via self._mem.set_metadata(page, tree_conf).
    - Persists the new root node content via self._mem.set_node(new_root).
    - No external I/O beyond what the memory manager performs (any on-disk writes are performed by the memory layer).

### `bplustree.tree.BPlusTree._create_overflow` · *method*

## Summary:
Persists a bytes value across one or more overflow pages in the underlying memory and returns the page number of the first overflow page. Effect on state: writes one page per chunk to self._mem via set_page and reads self._mem.next_available_page to obtain page numbers.

## Description:
This helper takes a byte string too large to store inline and writes it into a linked sequence of fixed-size overflow pages. Each overflow page contains a next-page reference, the payload length for that page, the payload slice, and zero padding to fill the page.

Known callers / invocation context:
- Called by higher-level B+ tree write/insert/update code when a value must be stored in overflow pages instead of inline storage. No direct callers were present in the provided snapshot; treat this method as a backend utility used during record serialization/persistence.

Why this is a separate method:
- The logic includes chunking, page allocation and a precise on-disk binary layout; factoring it out centralizes overflow storage format and avoids duplicating allocation/writing code in insertion/update paths.

## Args:
    value (bytes):
        - The complete byte sequence to persist across overflow pages.
        - Must be a bytes object. Passing other types (bytearray, memoryview, str, etc.) may raise TypeError at concatenation or produce incorrect on-disk bytes; callers should ensure a bytes instance is provided.
        - There is no explicit check for emptiness; see Preconditions / Edge cases.

## Returns:
    int:
        - The integer page number of the first overflow page allocated/read at the start of this method.
        - This is the reference callers should store where a pointer to overflow data is required.
        - Note: If the input yields no chunks (see Edge cases), the method still returns the first page number read from self._mem.next_available_page but will not call set_page for any page.

## Raises:
    - OverflowError:
        * If a numeric value (next-page number or payload length) cannot be encoded in the configured number of bytes when calling int.to_bytes(...). Specifically:
            - next page number must be < 256**PAGE_REFERENCE_BYTES
            - payload length must be < 256**USED_PAGE_LENGTH_BYTES
        * These are raised by Python's int.to_bytes and are not caught inside the method.
    - AttributeError:
        * If self._mem does not expose the attributes/methods accessed (next_available_page or set_page), attribute access will fail.
    - TypeError:
        * If value is not bytes and slicing/concatenation operations with bytes fail (this can occur if value is a type incompatible with bytes concatenation).

Note: The method does not explicitly raise an exception for the condition when the per-page payload capacity is non-positive; violation of that precondition leads to undefined behavior (see Constraints).

## State Changes:
Attributes READ:
    - self._tree_conf.page_size: used to compute per-page available payload (page_size - PAGE_REFERENCE_BYTES - USED_PAGE_LENGTH_BYTES).
    - self._mem.next_available_page: read to obtain the first page and to obtain subsequent pages when multiple pages are needed.
    - Module-level constants: PAGE_REFERENCE_BYTES, USED_PAGE_LENGTH_BYTES, ENDIAN.

Attributes WRITTEN (external state):
    - The method calls self._mem.set_page(page_number: int, data: bytes) for each chunk. This writes page-sized byte sequences to the underlying storage. No attribute on self (the BPlusTree object) is directly mutated by this method.

## Constraints:

Preconditions:
    - page_size (self._tree_conf.page_size) must be strictly greater than PAGE_REFERENCE_BYTES + USED_PAGE_LENGTH_BYTES.
        * Rationale: overflow_max_payload = page_size - PAGE_REFERENCE_BYTES - USED_PAGE_LENGTH_BYTES must be > 0.
        * If overflow_max_payload <= 0, the chunking routine will not make forward progress and the method will enter an infinite loop or behave incorrectly.
    - self._mem must provide:
        * A property/attribute next_available_page that returns an integer page number.
        * A method set_page(page_no: int, data: bytes) that accepts the bytes payload for a page.
    - value must be a bytes object and len(value) may be zero or greater.

Postconditions:
    - For every chunk produced by slicing value into parts of size up to overflow_max_payload:
        * A page is written at a page number (current_overflow_page) where set_page was called with exactly page_size bytes formed as:
            - next_overflow_page (PAGE_REFERENCE_BYTES bytes, big- or little-endian per ENDIAN)
            - length_payload (USED_PAGE_LENGTH_BYTES bytes, ENDIAN)
            - slice_value (length_payload bytes)
            - zero padding to bring the total to page_size
        * For the last chunk, next_overflow_page is encoded as 0.
    - The returned integer equals the initial value of self._mem.next_available_page read at the start of the method.
    - If the input produced zero chunks (e.g., value is empty), no set_page calls are executed and the returned page number is the initial next_available_page read, but no page content is written by this method.

## Side Effects:
    - Writes to underlying storage via self._mem.set_page for each chunk produced.
    - Reads self._mem.next_available_page one or more times (once before the loop and again for each intermediate page allocation).
    - Allocator semantics (whether reading next_available_page claims that page) are implementation-specific and not enforced here.
    - Allocates transient bytes objects on the Python heap equal in size to each page written; memory usage is proportional to page_size per iteration.

## Binary layout per overflow page (exact bytes written):
    - offset 0 .. PAGE_REFERENCE_BYTES-1: next_overflow_page encoded with int.to_bytes(PAGE_REFERENCE_BYTES, ENDIAN). A value of 0 means end-of-chain.
    - offset PAGE_REFERENCE_BYTES .. PAGE_REFERENCE_BYTES+USED_PAGE_LENGTH_BYTES-1: length_payload encoded with int.to_bytes(USED_PAGE_LENGTH_BYTES, ENDIAN).
    - offset PAGE_REFERENCE_BYTES+USED_PAGE_LENGTH_BYTES .. (PAGE_REFERENCE_BYTES+USED_PAGE_LENGTH_BYTES+length_payload-1): payload slice bytes.
    - remaining bytes up to page_size: zero bytes (bytes(padding)).

## Edge cases and recommendations:
    - Empty value (value == b''): The method will read self._mem.next_available_page and return that page number without writing any pages. Callers should handle this case explicitly (either avoid calling with empty bytes, or expect a returned page number without page content).
    - Zero or negative overflow_max_payload (page_size too small):
        * This is a critical precondition violation. The method's chunking helper expects a positive chunk size; if overflow_max_payload <= 0 the code will not progress and may loop indefinitely. Implementations should validate and raise a clear error before calling this helper.
    - Integer width limits:
        * Ensure that page numbers returned by next_available_page fit within PAGE_REFERENCE_BYTES, and slice lengths fit within USED_PAGE_LENGTH_BYTES; otherwise int.to_bytes will raise OverflowError.
    - To avoid allocating an unused page number when value is empty, consider performing a non-consuming check before reading next_available_page (e.g., compute chunk size and test len(value) == 0) if allocator behavior matters.

## Implementation recipe (step-by-step):
    1. Compute overflow_max_payload = self._tree_conf.page_size - PAGE_REFERENCE_BYTES - USED_PAGE_LENGTH_BYTES and assert > 0.
    2. Read first_overflow_page = self._mem.next_available_page and set next_overflow_page = first_overflow_page.
    3. Iterate over value in consecutive slices of at most overflow_max_payload bytes (the provided utils.iter_slice does this).
    4. For each slice_value and is_last flag:
        a. current_overflow_page = next_overflow_page
        b. If is_last: next_overflow_page = 0 else: next_overflow_page = self._mem.next_available_page
        c. length_payload = len(slice_value)
        d. padding = page_size - length_payload - PAGE_REFERENCE_BYTES - USED_PAGE_LENGTH_BYTES
        e. Build overflow_page_data by concatenating:
            - next_overflow_page.to_bytes(PAGE_REFERENCE_BYTES, ENDIAN)
            - length_payload.to_bytes(USED_PAGE_LENGTH_BYTES, ENDIAN)
            - slice_value
            - bytes(padding)
        f. Call self._mem.set_page(current_overflow_page, overflow_page_data)
    5. Return first_overflow_page as the starting page.

This description contains the precise format, interactions, preconditions, and recommended defensive checks needed to reimplement this method correctly.

### `bplustree.tree.BPlusTree._read_from_overflow` · *method*

## Summary:
Read and reconstruct a value split across an overflow-page chain by following the chain of page references, extracting each page's payload slice and concatenating them into a single immutable bytes result. The call does not mutate tree state.

## Description:
This routine implements the on-disk parsing and concatenation required to retrieve values that were stored in overflow pages when they exceeded the inline value capacity. It repeatedly reads pages from the underlying storage and appends each page's payload slice until the chain terminates.

Known callers and call context:
- BPlusTree._get_value_from_record: direct caller; invoked when a Record stores its data in overflow pages (record.value is None and record.overflow_page holds the first page).
- Higher-level read operations that cause the above: BPlusTree.get, BPlusTree.__getitem__, BPlusTree.items, BPlusTree.values, and other reader paths that resolve a record's value. Those callers typically hold a read transaction on self._mem.

Why a separate method:
- Parsing the fixed overflow page layout and managing multi-page concatenation is a self-contained responsibility. Extracting this logic into its own method centralizes layout knowledge, improves readability, and prevents duplication.

## On-page layout (constants used):
- PAGE_REFERENCE_BYTES: number of bytes at page start that encode the next overflow page reference.
- USED_PAGE_LENGTH_BYTES: number of bytes immediately after the page reference that encode the payload length on this page.
- ENDIAN: byte order used for integer encoding/decoding.
- Given these constants, the method uses these exact offsets per page:
    1. next_overflow_page = int.from_bytes(data[0:PAGE_REFERENCE_BYTES], ENDIAN)
    2. length_field_start = PAGE_REFERENCE_BYTES
       length_field_end = PAGE_REFERENCE_BYTES + USED_PAGE_LENGTH_BYTES
       length_payload = int.from_bytes(data[length_field_start:length_field_end], ENDIAN)
    3. payload_start = length_field_end
       payload_end = payload_start + length_payload
       payload_slice = data[payload_start:payload_end]

The remainder of the page past payload_end is treated as padding and ignored.

## Args:
    first_overflow_page (int): Page number of the first overflow page in the chain. Expected to be a positive integer produced by the tree's allocation logic (returned from _create_overflow and stored as Record.overflow_page). Supplying 0 or an invalid page may cause the underlying memory layer to raise.

## Returns:
    bytes: The concatenation of payload slices from each page in the overflow chain, returned as an immutable bytes object. If the overflow chain stores an empty value, an empty bytes object is returned.

Edge cases:
- If length_payload on a page is zero, that page contributes no bytes.
- If length_payload indicates more bytes than the page actually contains (malformed/truncated page), Python slicing returns fewer bytes than requested; the method will append that truncated slice — it does not validate or raise for mismatched lengths.
- The chain terminates when next_overflow_page == 0 (the terminal marker written by _create_overflow). If pages never encode a next_overflow_page of 0 (malformed chain or cycle), the method will loop indefinitely.

## Raises:
    - Any exception propagated from self._mem.get_page when reading a page (for example, invalid page number, missing/truncated page, or I/O errors). The method does not catch these exceptions.
    - No additional exceptions are raised explicitly by this method.

## Algorithm / Implementation notes (step-by-step):
    1. Initialize an empty bytearray accumulator (rv).
    2. Set next_overflow_page = first_overflow_page.
    3. Loop:
        a. Read the raw page bytes: data = self._mem.get_page(next_overflow_page)
        b. Parse next_overflow_page = int.from_bytes(data[0:PAGE_REFERENCE_BYTES], ENDIAN)
        c. Compute end_length_payload = PAGE_REFERENCE_BYTES + USED_PAGE_LENGTH_BYTES
        d. Parse length_payload = int.from_bytes(data[PAGE_REFERENCE_BYTES:end_length_payload], ENDIAN)
        e. Extract slice_value = data[end_length_payload:end_length_payload + length_payload]
        f. Append slice_value to accumulator (rv.extend(slice_value))
        g. If next_overflow_page == 0, break the loop.
    4. Return bytes(rv) to produce an immutable bytes object.

These steps reproduce the exact logic used by the method.

## State Changes:
Attributes READ:
    - self._mem (FileMemory): used to fetch page bytes via get_page.

Attributes WRITTEN:
    - None. The method does not modify any self.* attributes or persistent storage.

## Constraints:
Preconditions:
    - first_overflow_page should be a valid page number allocated by the tree (non-zero).
    - Pages in the chain should be well-formed according to the layout specified above (contain at least PAGE_REFERENCE_BYTES + USED_PAGE_LENGTH_BYTES bytes and have a payload region of length length_payload). The caller should typically hold a read transaction on self._mem.

Postconditions:
    - The returned bytes object equals the original value that was split by _create_overflow, assuming the chain and pages are well-formed.
    - No modification to the BPlusTree or storage occurs.

## Side Effects:
    - Reads page data from the underlying storage via self._mem.get_page. Depending on FileMemory implementation, this may perform file I/O and/or interact with an in-memory cache.
    - No writes to storage or other external systems are performed.

### `bplustree.tree.BPlusTree._get_value_from_record` · *method*

## Summary:
Return the value bytes represented by a record — either the inline bytes stored on the record or the bytes reconstructed by reading its overflow pages. Does not modify the tree state.

## Description:
Known callers and call sites:
- BPlusTree.get: used when retrieving a single key's value inside a read transaction.
- BPlusTree.__getitem__: used both for single-key access (via get) and for slice iteration (when assembling a dict of key→value).
- BPlusTree.items and BPlusTree.values: used while iterating records to yield actual value bytes.
- Any other internal iteration over records that needs the payload bytes.

Typical lifecycle/context:
- Invoked during read (or write) operations when a consumer requests the stored value for a Record.
- Callers generally call this method while holding self._mem.read_transaction (or write_transaction) to ensure consistent access to underlying storage.

Why this is a separate method:
- Centralizes the logic deciding whether a record's payload is inline or stored in overflow pages.
- Avoids duplicating overflow-read logic and keeps higher-level retrieval code concise and focused on traversal.
- Makes it easy to adjust how values are materialized (caching, decoding, etc.) in one place.

## Args:
    record (Record): A record instance produced by BPlusTree.Record(...).
        - Required attributes:
            * value (Optional[bytes]): If present (not None), contains the full payload bytes stored inline in the record.
            * overflow_page (Optional[int]): If value is None, this should be the page number (positive int) of the first overflow page; ignored when value is not None.
        - Allowed values:
            * record.value: either a bytes object or None.
            * record.overflow_page: positive integer page id when record.value is None; may be None when record.value is not None.

## Returns:
    bytes: The payload bytes for the record.
    - If record.value is not None, the same bytes object stored in the record is returned.
    - If record.value is None, bytes reconstructed by reading the overflow page chain via _read_from_overflow are returned.
    - Edge cases:
        * Returns b'' for an explicitly empty payload.
        * Always returns a bytes instance (never None) when it completes successfully.

## Raises:
    - This method does not explicitly raise its own exceptions, but it will propagate exceptions raised by the underlying overflow reader and memory layer:
        * If record.value is None and record.overflow_page is invalid (None, non-int, out-of-range), _read_from_overflow (or the memory layer) will raise (for example TypeError, ValueError, or an error from FileMemory.get_page). These exceptions propagate to the caller.
        * If underlying storage is corrupted or pages cannot be read, corresponding I/O or validation errors from self._mem.get_page/_read_from_overflow are propagated.

## State Changes:
    Attributes READ:
        - self._mem (indirectly, via _read_from_overflow) — used to read overflow pages.
        - record.value
        - record.overflow_page
    Attributes WRITTEN:
        - None. This method does not mutate self or the record.

## Constraints:
    Preconditions:
        - The provided record must be a valid Record with the attributes described above.
        - If record.value is None, record.overflow_page must reference the first overflow page (positive int).
        - Callers should hold an active memory transaction (typically self._mem.read_transaction or write_transaction) to ensure consistent reads from the underlying storage. Most public callers in this class already do so.

    Postconditions:
        - The tree and record remain unchanged.
        - A bytes object containing the full payload is returned if no exception is raised.

## Side Effects:
    - Performs read access to the underlying storage when record.value is None by delegating to _read_from_overflow, which calls self._mem.get_page for each overflow page. This may incur I/O or memory access through the FileMemory layer.
    - No writes, logging, or external service calls are performed by this method itself.

