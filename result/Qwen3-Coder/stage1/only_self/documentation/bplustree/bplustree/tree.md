# `tree.py`

## `bplustree.tree.BPlusTree` · *class*

*No documentation generated.*

### `bplustree.tree.BPlusTree.__init__` · *method*

## Summary:
Initializes a B+ tree instance by setting up configuration, memory management, and loading or creating the tree structure from persistent storage.

## Description:
This constructor method establishes the fundamental state of a B+ tree instance. It configures tree parameters, initializes memory management for disk-based storage, and either loads an existing tree structure from persistent storage or creates a new empty tree. The method orchestrates the tree's initialization lifecycle, ensuring proper setup for subsequent operations.

## Args:
    filename (str): Path to the file where the B+ tree data is stored persistently.
    page_size (int): Size of memory pages used for storing tree nodes. Defaults to 4096 bytes.
    order (int): Maximum number of children per internal node. Defaults to 100.
    key_size (int): Size in bytes of keys stored in the tree. Defaults to 8 bytes.
    value_size (int): Size in bytes of values stored in the tree. Defaults to 32 bytes.
    cache_size (int): Number of pages to cache in memory. Defaults to 64 pages.
    serializer (Optional[Serializer]): Serializer for key/value data. Defaults to IntSerializer().

## Returns:
    None

## Raises:
    ValueError: When metadata cannot be loaded from persistent storage, indicating a corrupted or uninitialized tree file.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._filename: Stores the file path for persistent storage
        - self._tree_conf: Stores tree configuration parameters
        - self._mem: Initializes memory manager for disk I/O
        - self._root_node_page: Stores the page number of the root node
        - self._is_open: Sets the tree state to open

## Constraints:
    Preconditions:
        - The filename parameter must specify a valid file path
        - All numeric parameters must be positive integers
        - The serializer parameter, if provided, must be a valid Serializer instance
    Postconditions:
        - The B+ tree instance is fully initialized and ready for operations
        - Either an existing tree structure is loaded or a new empty tree is created
        - Memory management is established for efficient disk I/O

## Side Effects:
    - Creates or opens a file for persistent storage
    - May perform disk I/O operations during metadata loading or initialization
    - Initializes memory caching subsystem
    - Potentially allocates new memory pages for tree structure

### `bplustree.tree.BPlusTree.close` · *method*

## Summary:
Closes the B+ tree by releasing underlying file resources and marking the tree as closed.

## Description:
This method safely closes the B+ tree by ending any active write transactions, closing the underlying file memory, and updating the internal state to reflect that the tree is no longer open. It is designed to be idempotent - calling it multiple times will not cause errors. When called on an already closed tree, it logs an informational message and returns early.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._mem, self._is_open
    Attributes WRITTEN: self._is_open (set to False)

## Constraints:
    Preconditions: The method can be called regardless of the current open/closed state
    Postconditions: The tree's _is_open attribute is set to False, and the underlying memory is closed

## Side Effects:
    I/O operations: Closes the underlying file handle through FileMemory.close()
    External service calls: None
    Mutations to objects outside self: None

### `bplustree.tree.BPlusTree.__enter__` · *method*

## Summary:
Returns the BPlusTree instance to enable usage in a context manager (`with`) statement.

## Description:
This method implements Python's context manager protocol, making BPlusTree instances compatible with the `with` statement. When used in a `with` statement, this method is called upon entering the context and returns the BPlusTree instance itself, allowing the caller to use the tree within the context. The corresponding `__exit__` method handles cleanup by closing the tree when exiting the context.

## Args:
    None

## Returns:
    BPlusTree: The BPlusTree instance itself, enabling method chaining and context usage.

## Raises:
    None

## State Changes:
    - Attributes READ: None
    - Attributes WRITTEN: None

## Constraints:
    - Preconditions: The BPlusTree instance must be properly initialized
    - Postconditions: The method returns the same instance unchanged

## Side Effects:
    - None

### `bplustree.tree.BPlusTree.__exit__` · *method*

## Summary:
Closes the B+ tree resource when exiting a context manager block.

## Description:
This method implements the context manager protocol's `__exit__` magic method. It is automatically called when exiting a `with` statement that uses a BPlusTree instance. The method ensures proper cleanup of resources by delegating to the `close()` method.

## Args:
    exc_type (type or None): Exception type if an exception was raised in the with block, otherwise None.
    exc_val (Exception or None): Exception value if an exception was raised in the with block, otherwise None.
    exc_tb (traceback or None): Traceback if an exception was raised in the with block, otherwise None.

## Returns:
    None: This method does not return any value.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying operations may raise exceptions.

## State Changes:
    Attributes READ: self._is_open, self._mem
    Attributes WRITTEN: self._is_open (set to False)

## Constraints:
    Preconditions: The BPlusTree instance must be initialized and accessible.
    Postconditions: The tree's memory resources are released and the `_is_open` flag is set to False.

## Side Effects:
    I/O operations: Calls `self._mem.close()` which performs file I/O operations to close the underlying storage.
    Resource cleanup: Releases file handles and other system resources associated with the tree.

### `bplustree.tree.BPlusTree.checkpoint` · *method*

## Summary:
Flushes pending write operations to persistent storage and reinitializes the write-ahead log state.

## Description:
This method performs a database checkpoint operation that ensures all pending write operations are committed to persistent storage. It acquires an exclusive write transaction and invokes the underlying memory manager's checkpoint mechanism with the `reopen_wal=True` parameter, which typically causes the write-ahead log to be reset and reopened for new operations. This method is typically used to guarantee data durability and manage storage space in WAL-based systems.

## Args:
    None

## Returns:
    None

## Raises:
    Exception: Propagates any exceptions raised by the underlying memory manager's checkpoint operation, such as I/O errors or storage-related failures.

## State Changes:
    Attributes READ: self._mem
    Attributes WRITTEN: None (the method doesn't modify any BPlusTree instance attributes directly)

## Constraints:
    Preconditions: The BPlusTree must be open (self._is_open = True) and the underlying memory manager must support checkpoint operations.
    Postconditions: All dirty pages are flushed to disk, and the write-ahead log is reopened for subsequent operations.

## Side Effects:
    I/O operations: Writes pending data pages to persistent storage through the memory manager.
    External service calls: Invokes the underlying FileMemory's perform_checkpoint method with reopen_wal=True parameter.

### `bplustree.tree.BPlusTree.insert` · *method*

## Summary:
Inserts a key-value pair into the B+ tree, updating existing entries when replace=True or creating new entries otherwise.

## Description:
This method implements the core insertion logic for the B+ tree data structure. It handles both creation of new key-value pairs and replacement of existing ones based on the replace parameter. When a value exceeds the configured value_size limit, the method automatically creates overflow pages to store the large data across multiple pages. The method ensures tree balance by splitting leaf nodes when they reach capacity.

This method is typically invoked during database write operations when new data needs to be stored in the B+ tree structure. It's accessible through both direct method calls and the __setitem__ magic method (e.g., tree[key] = value).

## Args:
    key (int): The key to insert or update in the tree
    value (bytes): The value to associate with the key, must be a bytes object
    replace (bool): If True, replaces existing values for the same key; if False, raises ValueError for duplicates

## Returns:
    None: This method does not return any value.

## Raises:
    ValueError: When attempting to insert a duplicate key without setting replace=True, or when the value is not a bytes object

## State Changes:
    Attributes READ: 
        - self._mem (FileMemory instance)
        - self._root_node (current root node of the tree)
        - self._tree_conf (tree configuration settings)
        - node.get_entry (method call to retrieve existing entries)
        - node.can_add_entry (property indicating if node can accept more entries)
        
    Attributes WRITTEN:
        - self._mem.set_node (persisting modified nodes back to storage)
        - existing_record.value (updating existing record value)
        - existing_record.overflow_page (updating existing record overflow page reference)
        - node.entries (modifying node entries during insertion)
        - node.next_page (updating next page reference for leaf nodes)

## Constraints:
    Preconditions:
        - The value parameter must be a bytes object
        - The tree must be in an open state (self._is_open is True)
        - The tree must have valid memory management initialized
        - Keys must be comparable with existing keys in the tree
        
    Postconditions:
        - If replace=False and key exists, raises ValueError
        - If replace=True and key exists, updates the existing record with new value
        - If key doesn't exist, creates a new record with the provided key-value pair
        - Large values (> value_size) are stored across overflow pages with proper chaining
        - Tree structure maintains B+ tree properties through node splitting when needed

## Side Effects:
    - Performs memory writes through FileMemory operations (set_node, set_page)
    - May trigger disk I/O when accessing or writing to storage pages
    - Modifies tree structure through node splitting operations
    - May cause recursive splitting of parent nodes when leaf nodes split

### `bplustree.tree.BPlusTree.batch_insert` · *method*

## Summary:
Inserts multiple key-value pairs into the B+ tree in a single operation, optimizing performance by reducing redundant tree searches and managing node splits efficiently.

## Description:
This method performs batch insertion of key-value pairs into the B+ tree structure. It processes the input iterable sequentially, maintaining a reference to the current leaf node to avoid repeated tree searches for each insertion. The method enforces that keys are inserted in strictly ascending order (each key must be greater than the largest key currently in the tree) and handles both normal-sized values and large values that require overflow page storage.

The method operates within a write transaction to ensure atomicity of the entire batch operation. It intelligently manages node splitting when leaf nodes reach capacity, creating new sibling nodes as needed to maintain the B+ tree structure. This approach provides significant performance benefits over individual insertions when inserting many records.

Known callers include any code that needs to bulk-insert data into the B+ tree, particularly during initialization or data loading operations. This method is preferred over individual insertions when processing multiple records because it reduces tree traversal overhead and optimizes memory operations.

## Args:
    iterable (Iterable): An iterable of key-value pairs where keys are integers and values are bytes objects. Keys must be provided in strictly ascending order, with each key being greater than all existing keys in the tree.

## Returns:
    None: This method does not return any value

## Raises:
    ValueError: Raised when keys in the iterable are not in strictly ascending order (i.e., when a key is less than or equal to the largest key currently in the tree)

## State Changes:
    Attributes READ: 
        - self._mem: Used for write transaction management and node persistence
        - self._root_node: Accessed during initial tree search
        - self._tree_conf.value_size: Used to determine if value fits in page
        - node.biggest_entry: Accessed to validate key ordering
        - node.can_add_entry: Used to determine if node needs splitting
        
    Attributes WRITTEN:
        - self._mem: Modified through set_node calls for updated nodes
        - node: Modified during entry insertion and splitting operations

## Constraints:
    Preconditions:
        - The tree must be open (self._is_open is True)
        - Keys in the iterable must be provided in strictly ascending order
        - Each key must be greater than all existing keys in the tree
        - Values must be bytes objects
        - The iterable must be properly ordered to maintain tree invariants
        
    Postconditions:
        - All key-value pairs from the iterable are successfully inserted into the tree
        - The tree structure remains valid and balanced
        - Node splitting occurs appropriately when leaf nodes become full
        - All modifications are persisted atomically within a single write transaction

## Side Effects:
    - Performs multiple memory writes through FileMemory operations
    - May trigger disk I/O when persisting updated nodes
    - Can cause recursive node splitting operations through _split_leaf calls
    - Modifies the tree structure by adding new nodes and updating references

### `bplustree.tree.BPlusTree.get` · *method*

## Summary:
Retrieves the byte value associated with a given key from the B+ tree, returning a default value if the key is not found.

## Description:
This method performs a lookup operation in the B+ tree structure to retrieve the byte value associated with the specified key. It traverses the tree structure using the internal search mechanism to locate the appropriate leaf node, then extracts the record containing the key-value pair. If the key does not exist in the tree, the method returns the provided default value instead of raising an exception.

The method is designed to be used as a safe lookup operation that gracefully handles missing keys by returning a configurable default value.

## Args:
    key (int): The key to search for in the B+ tree
    default (bytes, optional): The default value to return if the key is not found. Defaults to None

## Returns:
    bytes: The byte value associated with the key if found, otherwise the default value

## Raises:
    None explicitly raised by this method, though underlying operations may raise exceptions

## State Changes:
    Attributes READ: 
        - self._mem (FileMemory instance)
        - self._root_node (via property)
    
    Attributes WRITTEN: 
        - None

## Constraints:
    Preconditions:
        - The B+ tree must be open and accessible
        - The key must be comparable with existing keys in the tree
        - The tree structure must be valid
        
    Postconditions:
        - Returns bytes if key exists, otherwise returns the default value
        - The method does not modify the tree structure

## Side Effects:
    - Performs read transactions on the memory manager
    - May cause disk I/O when retrieving nodes from persistent storage during tree traversal
    - Calls internal methods that may perform memory page reads

### `bplustree.tree.BPlusTree.__contains__` · *method*

## Summary:
Checks whether a key exists in the B+ tree and returns a boolean indicating membership.

## Description:
Implements the Python `__contains__` magic method, enabling the use of the `in` operator with B+ tree instances. This method efficiently determines if a given key exists in the tree without retrieving the associated value.

## Args:
    item: The key to search for in the tree. Type is determined by the tree's key configuration.

## Returns:
    bool: True if the key exists in the tree, False otherwise.

## Raises:
    None explicitly raised, but may propagate exceptions from underlying storage operations.

## State Changes:
    Attributes READ: 
    - self._mem: Used to access the memory manager for read transactions
    - self._root_node: Accessed via _search_in_tree to traverse the tree structure

## Constraints:
    Preconditions:
    - The tree must be open (self._is_open must be True)
    - The tree must have valid metadata and root node setup
    
    Postconditions:
    - No modifications are made to the tree structure or data
    - The method returns immediately without side effects

## Side Effects:
    - Acquires a read transaction from self._mem
    - May perform disk I/O operations when accessing nodes from storage
    - Traverses the tree structure to find the key

### `bplustree.tree.BPlusTree.__setitem__` · *method*

*No documentation generated.*

### `bplustree.tree.BPlusTree.__getitem__` · *method*

## Summary:
Retrieves values from the B+ tree using dictionary-style key access or slice-based range queries.

## Description:
This special method enables dictionary-style access to the B+ tree, allowing users to retrieve values using `tree[key]` syntax. It supports both single key lookups and slice-based range queries. When a single key is provided, it returns the associated value or raises a KeyError if the key does not exist. When a slice is provided, it returns a dictionary mapping keys to values for all entries within the specified range.

## Args:
    item (Union[int, slice]): Either a single key (int) or a slice object defining a range of keys to retrieve.

## Returns:
    Union[bytes, dict]: For single key access, returns the bytes value associated with the key. For slice access, returns a dictionary mapping keys to their corresponding byte values.

## Raises:
    KeyError: When attempting to access a non-existent key using single-key access pattern.
    ValueError: When a slice with a custom step is provided, or when slice start is greater than or equal to stop.

## State Changes:
    Attributes READ: 
        - self._mem (FileMemory): Used for read transactions and accessing nodes
        - self._root_node: Accessed via property to find appropriate leaf nodes
        - self._left_record_node: Used when slice start is None to begin iteration

## Constraints:
    Preconditions:
        - The tree must be open (self._is_open must be True)
        - The key or slice parameters must be valid for the tree's configuration
    Postconditions:
        - For single key access: Returns bytes value or raises KeyError
        - For slice access: Returns a dictionary with all matching key-value pairs

## Side Effects:
    - Performs read operations on the underlying file memory
    - Uses read transactions to ensure thread safety
    - May access multiple pages in the file memory during range queries

### `bplustree.tree.BPlusTree.__len__` · *method*

## Summary:
Returns the total number of records stored in the B+ tree by traversing all leaf nodes.

## Description:
This method calculates the total count of records in the B+ tree by following the linked list of leaf nodes starting from the leftmost record node. It uses a read transaction to ensure consistency during the traversal operation.

## Args:
    None

## Returns:
    int: The total number of records stored in the tree.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
        - self._mem: Memory manager for accessing nodes
        - self._left_record_node: Starting node for traversal
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The tree must be properly initialized
        - self._left_record_node must be a valid node reference
        - self._mem must be a valid memory manager with read_transaction capability
    Postconditions:
        - The method returns an integer representing the total record count
        - The tree structure remains unchanged

## Side Effects:
    - Performs read operations on the underlying memory/storage system
    - Uses a read transaction to maintain consistency

### `bplustree.tree.BPlusTree.__length_hint__` · *method*

## Summary:
Estimates the number of records in the BPlusTree by calculating based on memory usage and node characteristics.

## Description:
This method provides a hint about the approximate length of the tree by estimating the number of records based on memory page utilization and node configuration. It's designed to be efficient and avoid full traversal of the tree structure. The method is typically called by Python's iterator protocol when working with the tree as an iterable.

The estimation algorithm works differently based on the root node type:
- For a LonelyRootNode, it returns half the maximum children capacity (node.max_children // 2)
- For regular trees, it estimates based on 70% of total pages, average records per leaf node, and node capacity

## Args:
    None

## Returns:
    int: An estimated count of records in the tree. This is a hint, not necessarily the exact count.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self._mem (FileMemory instance)
    - self._root_node (property accessing the root node)
    - self._mem.last_page (property accessing the last page number)
    - node.max_children (attribute of root node)
    - node.min_children (attribute of root node)
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The tree must be open (self._is_open should be True)
    - The memory system must be properly initialized
    - The root node must be accessible
    - The root node must be either a LonelyRootNode or a regular node with max_children and min_children attributes
    
    Postconditions:
    - Returns a non-negative integer representing an estimated record count
    - Does not modify the tree structure or state
    - The returned value is a hint and may differ from actual count

## Side Effects:
    - Acquires a read transaction from self._mem
    - Reads from memory pages via self._mem.get_node() and self._mem.last_page
    - Does not perform any I/O operations beyond memory access

### `bplustree.tree.BPlusTree.__iter__` · *method*

## Summary:
Returns an iterator over all keys in the B+ tree, optionally filtered by a slice range.

## Description:
This method provides iteration capability over the keys stored in the B+ tree. When called without arguments, it iterates over all keys in ascending order. When provided with a slice argument, it iterates over keys within the specified range. The method uses a read transaction to ensure consistency during iteration.

This method is implemented as a generator that yields keys from records in the tree, making it memory-efficient for large datasets. It leverages the internal `_iter_slice` method to handle the actual iteration logic and range filtering.

## Args:
    slice_ (Optional[slice], optional): A slice object defining the range of keys to iterate over. Defaults to None, which means iterate over all keys.

## Returns:
    Iterator: An iterator yielding the key values from the tree records in ascending order.

## Raises:
    ValueError: Raised by _iter_slice when a custom step is provided in the slice or when start >= stop in a slice.

## State Changes:
    Attributes READ: 
        - self._mem (FileMemory instance)
        - self._iter_slice (method)
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The B+ tree must be open (self._is_open must be True)
        - The slice parameters must be valid (no custom step, start < stop when both defined)
    Postconditions:
        - The method returns an iterator without modifying the tree structure
        - All keys are yielded in ascending order within the specified range

## Side Effects:
    - Acquires a read transaction from self._mem
    - Reads from disk/memory pages through self._mem.get_node() and self._mem.get_page()
    - May read multiple nodes from the tree structure sequentially

### `bplustree.tree.BPlusTree.items` · *method*

## Summary:
Returns an iterator over key-value pairs from the B+ tree, optionally filtered by a key range slice.

## Description:
Provides iteration over all key-value pairs stored in the B+ tree. When called without arguments, it iterates over all entries in the tree in key-sorted order. When provided with a slice argument, it iterates over entries within the specified key range (start inclusive, stop exclusive).

This method is designed as a separate utility to encapsulate the common pattern of retrieving both keys and values from the tree while maintaining proper transaction management and slice handling.

## Args:
    slice_ (Optional[slice], optional): A slice object defining the key range to iterate over. Defaults to None, which means iterate over all entries.

## Returns:
    Iterator[tuple]: An iterator yielding tuples of (key, value) where key is the record key and value is the associated byte value.

## Raises:
    ValueError: When the slice has a non-None step value or when start >= stop (backwards iteration).

## State Changes:
    Attributes READ: 
        - self._mem: Used for read transaction management
        - self._iter_slice: Called to get records within the slice range
        - self._get_value_from_record: Called to extract values from records
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The tree must be open (self._is_open is True)
        - The slice must have step=None and start <= stop when both are specified
    Postconditions:
        - Returns an iterator over (key, value) tuples in key-sorted order
        - Iterator stops when reaching the stop key (exclusive) or end of tree

## Side Effects:
    - Reads from disk/memory through self._mem.get_node() calls during iteration
    - May perform multiple memory lookups to traverse leaf nodes
    - Uses read transaction management for consistency

### `bplustree.tree.BPlusTree.values` · *method*

## Summary:
Returns an iterator over the byte values stored in the B+ tree, optionally filtered by a key range slice.

## Description:
This method provides iteration over all values stored in the B+ tree. When a slice is provided, it only returns values for keys within that range. The method operates within a read transaction to ensure consistency and uses the underlying tree traversal mechanisms to efficiently retrieve records.

The method is designed to work with the tree's existing slice-based iteration infrastructure, making it consistent with other methods like `keys()` and `items()` that operate on the same underlying data structure.

## Args:
    slice_ (Optional[slice], optional): A slice object defining the key range to iterate over. Defaults to None, which means iterate over all keys.

## Returns:
    Iterator[bytes]: An iterator yielding byte values stored in the tree, ordered by their keys.

## Raises:
    ValueError: When the slice has a non-None step value or when start >= stop (backwards iteration).

## State Changes:
    Attributes READ: 
        - self._mem: Used for read transaction and accessing nodes
        - self._iter_slice: Called to get records within the slice range
        - self._get_value_from_record: Called to extract values from records
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The tree must be open (self._is_open is True)
        - The slice must have step=None and start <= stop when both are specified
    Postconditions:
        - Returns an iterator over byte values in key-sorted order
        - Iterator stops when reaching the stop key (exclusive) or end of tree

## Side Effects:
    - Reads from disk/memory through self._mem.get_node() calls during iteration
    - May perform multiple memory lookups to traverse leaf nodes
    - Uses read transaction to ensure consistency

### `bplustree.tree.BPlusTree.__bool__` · *method*

## Summary:
Returns True if the BPlusTree contains at least one record, False otherwise.

## Description:
This special method implements the truthiness check for BPlusTree instances. It determines whether the tree is "empty" or not by performing a minimal scan of the tree's contents. When called, it acquires a read transaction and attempts to iterate over the tree using its iterator protocol (__iter__). If the iteration yields at least one item (i.e., there is at least one record in the tree), the method immediately returns True; otherwise it returns False.

This implementation is efficient because it stops as soon as the first record is found, avoiding unnecessary traversal of the entire tree structure.

## Args:
    None

## Returns:
    bool: True if the tree contains at least one record, False if the tree is empty.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self._mem: Used to acquire a read transaction
    - self: Used to iterate over the tree contents via __iter__

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The tree must be open (self._is_open should be True)
    - The tree's memory management system must be properly initialized
    
    Postconditions:
    - The method does not modify the tree's state
    - The read transaction is properly released after execution
    - The iteration does not consume or alter the tree's contents

## Side Effects:
    - Acquires and releases a read transaction from self._mem
    - Iterates over the tree's contents (via __iter__) to check for existence of records
    - May cause disk I/O when accessing nodes during iteration
    - Does not modify any tree data

### `bplustree.tree.BPlusTree.__repr__` · *method*

## Summary:
Returns a string representation of the BPlusTree instance showing its filename and configuration.

## Description:
This method provides a human-readable representation of the BPlusTree object for debugging and logging purposes. It displays the underlying filename and tree configuration details in a standardized format.

## Args:
    None

## Returns:
    str: A formatted string in the pattern '<BPlusTree: {filename} {tree_conf}>'

## Raises:
    None

## State Changes:
    Attributes READ: self._filename, self._tree_conf
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The BPlusTree instance must be properly initialized with _filename and _tree_conf attributes
    Postconditions: The returned string format is consistent and contains both filename and tree configuration information

## Side Effects:
    None

### `bplustree.tree.BPlusTree._initialize_empty_tree` · *method*

## Summary:
Initializes an empty B+ tree by creating a lonely root node and setting up initial metadata.

## Description:
This method establishes the foundational structure for a new, empty B+ tree. It assigns the next available memory page as the root node location, creates a lonely root node (which serves as the initial root for an empty tree), and stores the tree configuration metadata. This method is exclusively called during tree initialization when no existing tree structure is detected.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
        - self._mem (for next_available_page property)
        - self._tree_conf (for metadata storage)
    Attributes WRITTEN:
        - self._root_node_page (stores the page number of the newly created root node)
        - self._mem (through set_node and set_metadata calls)

## Constraints:
    Preconditions:
        - The tree must be in an uninitialized state (no existing metadata)
        - self._mem must be initialized and ready for write operations
        - self._tree_conf must be properly configured
    Postconditions:
        - self._root_node_page is set to the page number of the new lonely root node
        - A lonely root node is persisted in memory at the assigned page
        - Metadata containing the root page number and tree configuration is stored

## Side Effects:
    - Writes to persistent storage through FileMemory operations
    - Creates a new memory page allocation for the root node
    - Modifies the tree's metadata in persistent storage

### `bplustree.tree.BPlusTree._create_partials` · *method*

## Summary:
Creates partial functions for node and entry classes pre-bound with the tree configuration.

## Description:
This method initializes partial functions for various node and entry classes, pre-binding the tree configuration (`self._tree_conf`) to each constructor. This eliminates the need to repeatedly pass the tree configuration when instantiating these objects throughout the B+ tree implementation.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self._tree_conf
    Attributes WRITTEN: self.LonelyRootNode, self.RootNode, self.InternalNode, self.LeafNode, self.Record, self.Reference

## Constraints:
    Preconditions: The method assumes `self._tree_conf` is properly initialized (typically set during `__init__`)
    Postconditions: Six partial functions are created and assigned to instance attributes

## Side Effects:
    None

### `bplustree.tree.BPlusTree._root_node` · *method*

*No documentation generated.*

### `bplustree.tree.BPlusTree._left_record_node` · *method*

## Summary:
Returns the leftmost leaf node or lonely root node in the B+ tree structure for traversal operations.

## Description:
This method traverses the B+ tree from the root node toward the leftmost leaf node by following the smallest entry's "before" references. It is primarily used for iteration and length calculation operations where the tree needs to be traversed from the beginning. The method ensures that it stops at either a LeafNode or LonelyRootNode, which represent the terminal nodes in the tree structure.

## Args:
    None

## Returns:
    Union['LonelyRootNode', 'LeafNode']: The leftmost node in the tree structure, which contains the first records in the tree.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self._root_node
    - self._mem
    
    Attributes WRITTEN: 
    - None

## Constraints:
    Preconditions:
    - The tree must be initialized and opened
    - The root node must be accessible via self._root_node
    - The tree structure must be valid (no circular references in node chains)
    
    Postconditions:
    - Returns either a LeafNode or LonelyRootNode instance
    - The returned node is guaranteed to be the leftmost node in the tree

## Side Effects:
    - Accesses memory through self._mem.get_node() to retrieve nodes
    - May cause disk I/O if nodes are not cached in memory

### `bplustree.tree.BPlusTree._iter_slice` · *method*

## Summary:
Iterates over records in the B+ tree within a specified key range slice.

## Description:
This method provides iteration over records in the B+ tree according to a slice specification. It starts from either the leftmost record or a specified starting key, and continues until reaching the stop key (exclusive). The method handles both inclusive start and exclusive stop semantics for the slice.

## Args:
    slice_ (slice): A slice object specifying the key range to iterate over. The slice must have a step of None and cannot iterate backwards.

## Returns:
    Iterator[Record]: An iterator over Record objects whose keys fall within the specified slice range.

## Raises:
    ValueError: When the slice has a non-None step value or when start >= stop (backwards iteration).

## State Changes:
    Attributes READ: 
        - self._left_record_node: Used when slice.start is None
        - self._root_node: Passed to _search_in_tree when slice.start is not None
        - self._mem: Used to retrieve nodes via get_node method

## Constraints:
    Preconditions:
        - The tree must be open (self._is_open is True)
        - The slice must have step=None and start <= stop when both are specified
    Postconditions:
        - Returns an iterator over Record objects in key-sorted order
        - Iterator stops when reaching the stop key (exclusive) or end of tree

## Side Effects:
    - Reads from disk/memory through self._mem.get_node() calls
    - May perform multiple memory lookups to traverse leaf nodes

### `bplustree.tree.BPlusTree._search_in_tree` · *method*

## Summary:
Recursively searches for the leaf node containing the specified key by traversing the B+ tree structure from the given starting node.

## Description:
This private method implements the core tree traversal logic for B+ tree operations. It navigates through internal nodes to find the appropriate leaf node that would contain the given key. The method handles special cases for LonelyRootNode and LeafNode by returning them directly, and for InternalNodes by determining the correct child node to traverse to based on key comparisons.

The method is called during various tree operations such as insertion, retrieval, and iteration to locate the correct position for key operations.

## Args:
    key (int): The key value to search for in the tree
    node (Node): The current node in the tree traversal process

## Returns:
    Node: The leaf node or lonely root node that contains or should contain the specified key

## Raises:
    AssertionError: When no valid page reference can be determined during traversal (should never occur due to tree structure invariants)

## State Changes:
    Attributes READ: 
        - self._mem (FileMemory instance)
        - node.smallest_key
        - node.smallest_entry.before
        - node.biggest_key
        - node.biggest_entry.after
        - node.entries
    
    Attributes WRITTEN:
        - child_node.parent (set to the current node)

## Constraints:
    Preconditions:
        - The node parameter must be a valid node in the B+ tree structure
        - The key parameter must be comparable with node key values
        - The tree must maintain valid structural invariants
        
    Postconditions:
        - Returns either a LeafNode or LonelyRootNode (both of which can contain records)
        - The returned node contains or should contain the specified key

## Side Effects:
    - Performs memory reads to retrieve child nodes from storage
    - Modifies the parent attribute of child nodes during traversal
    - May cause disk I/O when retrieving nodes from persistent storage

### `bplustree.tree.BPlusTree._split_leaf` · *method*

## Summary:
Splits a leaf node when it becomes full and redistributes its entries between the old node and a newly created sibling node.

## Description:
This method handles the splitting of leaf nodes in the B+ tree structure when a node reaches its maximum capacity. It creates a new sibling leaf node, splits the entries from the original node, and updates the parent node accordingly. The method manages special cases for lonely root nodes and ensures proper tree restructuring by either inserting the new reference into the parent or recursively splitting the parent if it's also full. This method is called internally during insertion operations when a leaf node exceeds its capacity.

When splitting a leaf node, the method follows these steps:
1. Creates a new sibling leaf node with the second half of entries
2. Updates the old node to contain only the first half of entries
3. Inserts a reference to the new sibling in the parent node
4. Handles special cases for lonely root nodes by converting them to regular leaf nodes
5. Either inserts the reference directly into the parent or recursively splits the parent if it's full

## Args:
    old_node (Node): The leaf node that needs to be split. Must be a LeafNode or LonelyRootNode instance.

## Returns:
    None: This method does not return any value.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: 
        - self._mem: Used to access next_available_page and set_node operations
        - old_node.parent: Access to parent node reference
        - old_node.next_page: Used to set up the new node's next page reference
        - old_node.smallest_key: Used to create reference for parent node
        
    Attributes WRITTEN:
        - old_node.next_page: Updated to point to the new sibling node
        - self._mem: Modified through set_node calls for both old and new nodes
        - parent: Modified when inserting reference into parent node (when not root)

## Constraints:
    Preconditions:
        - The old_node parameter must be a valid Node instance (LeafNode or LonelyRootNode)
        - The tree must be in an open state (self._is_open is True)
        - Memory management must be properly initialized
        
    Postconditions:
        - The old_node is modified to contain half of the original entries
        - A new LeafNode is created with the remaining entries
        - The parent node is updated with a reference to the new sibling node
        - Both nodes are persisted to memory

## Side Effects:
    - Writes to disk via FileMemory operations (set_node calls)
    - Modifies node structure in memory
    - May trigger recursive splitting of parent nodes through _split_parent call
    - Updates tree structure to maintain B+ tree properties

### `bplustree.tree.BPlusTree._split_parent` · *method*

*No documentation generated.*

### `bplustree.tree.BPlusTree._create_new_root` · *method*

## Summary:
Creates a new root node for the B+ tree by initializing a RootNode with the next available page and inserting the provided reference.

## Description:
This method is responsible for creating a new root node when the existing root node becomes full and needs to be split. It's called during tree restructuring operations such as leaf node splitting or internal node splitting. The method constructs a new RootNode instance, inserts the provided reference into it, updates the tree's root node page reference, and persists the new root node to memory.

## Args:
    reference (Reference): A reference object containing key and page information to be inserted into the new root node.

## Returns:
    None: This method does not return any value.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: 
        - self._mem (FileMemory): Used to access next_available_page and set_metadata/set_node
        - self._tree_conf: Used in RootNode creation and set_metadata call
    
    Attributes WRITTEN:
        - self._root_node_page: Updated to point to the new root node's page
        - self._mem: Modified through set_metadata and set_node calls

## Constraints:
    Preconditions:
        - The B+ tree must be in an open state (self._is_open is True)
        - The reference parameter must be a valid Reference object
        - Memory management must be properly initialized
        
    Postconditions:
        - A new RootNode is created with the next available page
        - The root node page reference is updated to point to the new root
        - The new root node is persisted in memory
        - Metadata for the new root page is stored

## Side Effects:
    - Writes to disk via FileMemory operations
    - Modifies the tree's root node page reference
    - Updates metadata in the underlying storage
    - Persists the new root node to the memory manager

### `bplustree.tree.BPlusTree._create_overflow` · *method*

## Summary:
Creates a chain of overflow pages to store a large bytes value that exceeds single-page capacity.

## Description:
This method handles the creation of overflow pages for values that are too large to fit within a single page. It splits the input bytes into appropriately sized chunks and stores them across multiple pages, linking them together through page references. This method is called during record insertion when a value cannot fit in a leaf node's page, ensuring large values are properly distributed across multiple pages while maintaining a linked list structure for efficient retrieval.

The method is invoked when inserting records with large values into leaf nodes, specifically when the value size exceeds the calculated overflow_max_payload capacity.

## Args:
    value (bytes): The large bytes value to be stored across overflow pages

## Returns:
    int: The page number of the first overflow page in the chain, which serves as the entry point for retrieving the complete value

## Raises:
    None explicitly raised, but may raise exceptions from underlying memory operations such as page allocation failures

## State Changes:
    Attributes READ: 
        - self._tree_conf.page_size
        - self._mem.next_available_page
    
    Attributes WRITTEN:
        - Multiple pages in memory via self._mem.set_page calls

## Constraints:
    Preconditions:
        - The input value must be bytes
        - There must be sufficient available memory/pages for overflow storage
        - The tree configuration must define valid page size constants (PAGE_REFERENCE_BYTES, USED_PAGE_LENGTH_BYTES)
        
    Postconditions:
        - All overflow pages are properly formatted with correct headers containing:
          * Next page reference (PAGE_REFERENCE_BYTES)
          * Payload length (USED_PAGE_LENGTH_BYTES)
          * Actual data slice
          * Padding to fill the page
        - Page references are correctly linked in the overflow chain
        - The returned page number points to the first page in the chain

## Side Effects:
    - Modifies memory pages through self._mem.set_page calls
    - Consumes available pages from the memory manager
    - May cause page allocation in the underlying storage system

### `bplustree.tree.BPlusTree._read_from_overflow` · *method*

## Summary:
Reads a complete byte sequence from a chain of overflow pages starting from the given page reference.

## Description:
This method reconstructs a complete byte value that was split across multiple overflow pages. It follows the linked list of overflow pages by reading the next page reference at the beginning of each page, extracting the payload data, and concatenating all payloads until reaching the end of the chain (indicated by a next page reference of 0).

This method is called by `_get_value_from_record` when a record's value is too large to fit inline and has been stored in overflow pages. The method encapsulates the complexity of reading multi-page overflow data into a single coherent byte sequence.

## Args:
    first_overflow_page (int): The page number of the first overflow page in the chain

## Returns:
    bytes: The complete concatenated byte sequence from all overflow pages in the chain

## Raises:
    None explicitly raised, but may propagate exceptions from underlying memory operations such as:
    - KeyError or similar from self._mem.get_page() if page doesn't exist
    - ValueError from int.from_bytes() if data is malformed

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The first_overflow_page parameter must be a valid page number
    - All pages in the overflow chain must exist and be readable
    - The overflow page data must follow the expected format (next page reference, length, payload)
    Postconditions:
    - Returns a complete byte sequence reconstructed from all overflow pages
    - The returned bytes represent the original value that was too large for inline storage

## Side Effects:
    I/O operations: Performs multiple calls to self._mem.get_page() to read overflow page data from persistent storage

### `bplustree.tree.BPlusTree._get_value_from_record` · *method*

## Summary:
Retrieves the complete byte value from a record, handling both inline values and overflow page storage.

## Description:
This method extracts the full byte value from a Record object. If the record contains an inline value (record.value is not None), it returns that value directly. Otherwise, it reads the value from overflow pages using the overflow page reference stored in record.overflow_page.

This logic is separated into its own method to handle the complexity of value retrieval when values may be stored either inline or in overflow pages, providing a clean abstraction for accessing record values throughout the BPlusTree implementation.

## Args:
    record (Record): A record object containing either an inline value or a reference to overflow pages

## Returns:
    bytes: The complete byte value associated with the record

## Raises:
    None explicitly raised, but may propagate exceptions from _read_from_overflow

## State Changes:
    Attributes READ: record.value, record.overflow_page
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The record parameter must be a valid Record instance
    - If record.value is None, then record.overflow_page must be a valid page reference
    Postconditions:
    - Returns bytes representing the complete value stored in the record
    - The returned bytes are guaranteed to be the complete value, whether stored inline or in overflow pages

## Side Effects:
    I/O operations: Calls self._read_from_overflow which performs memory page reads

