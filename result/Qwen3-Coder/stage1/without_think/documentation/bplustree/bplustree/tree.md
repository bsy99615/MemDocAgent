# `tree.py`

## `bplustree.tree.BPlusTree` · *class*

*No documentation generated.*

### `bplustree.tree.BPlusTree.__init__` · *method*

## Summary:
Initializes a B+ tree instance with specified configuration parameters and loads or creates the tree structure from persistent storage.

## Description:
The constructor initializes a B+ tree data structure by setting up configuration parameters, memory management, and loading or creating the tree's initial state. This method orchestrates the setup of the entire B+ tree system, including configuration management, memory allocation, and metadata handling.

The method is called during object instantiation and handles two main scenarios: loading an existing tree from persistent storage or initializing a completely new empty tree. It ensures that all internal state is properly configured before the tree becomes usable.

## Args:
    filename (str): Path to the file where the tree data will be persisted
    page_size (int): Size of each page in bytes, defaults to 4096
    order (int): Maximum number of children for internal nodes, defaults to 100
    key_size (int): Size of keys in bytes, defaults to 8
    value_size (int): Size of values in bytes, defaults to 32
    cache_size (int): Number of pages to cache in memory, defaults to 64
    serializer (Optional[Serializer]): Serializer for key/value data, defaults to IntSerializer()

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - None directly read
    
    Attributes WRITTEN:
    - self._filename: Set to the provided filename
    - self._tree_conf: Initialized with configuration parameters
    - self._mem: Initialized with FileMemory instance
    - self._root_node_page: Set from loaded metadata or newly allocated page
    - self._is_open: Set to True indicating the tree is ready for use

## Constraints:
    Preconditions:
    - The filename parameter must be a valid string path
    - All numeric parameters (page_size, order, key_size, value_size, cache_size) must be positive integers
    - The serializer parameter, if provided, must be a valid Serializer instance
    
    Postconditions:
    - The B+ tree instance is fully configured with all internal state initialized
    - Either existing tree metadata is loaded or a new empty tree is initialized
    - The tree is marked as open and ready for operations

## Side Effects:
    - Opens file for persistent storage access
    - May perform I/O operations to read existing metadata or write new tree structure
    - Initializes memory caching system
    - Potentially allocates new pages in storage when creating a new tree

### `bplustree.tree.BPlusTree.close` · *method*

## Summary:
Closes the B+ tree and releases associated file resources.

## Description:
This method safely closes the B+ tree by ending any active write transactions, closing the underlying memory manager, and marking the tree as closed. It ensures proper resource cleanup and prevents further operations on the tree.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._mem, self._is_open
    Attributes WRITTEN: self._is_open

## Constraints:
    Preconditions: The method can be called regardless of the current state, but will be a no-op if the tree is already closed.
    Postconditions: The tree's `_is_open` flag will be set to False, and the underlying memory manager will be closed.

## Side Effects:
    I/O operations: Closes the underlying file-based memory manager.
    Resource cleanup: Releases file handles and other system resources associated with the tree.

### `bplustree.tree.BPlusTree.__enter__` · *method*

## Summary:
Returns the BPlusTree instance itself to enable context manager usage with the `with` statement.

## Description:
This method implements Python's context manager protocol, allowing BPlusTree instances to be used in `with` statements. When entered, the method returns `self`, making the tree object available within the context block. This enables automatic resource management where the `__exit__` method will be called upon exiting the context, ensuring proper cleanup via the `close()` method.

## Args:
    None

## Returns:
    BPlusTree: The BPlusTree instance itself, enabling access to the tree within the context block.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The BPlusTree instance must be properly initialized and not already closed.
    Postconditions: The BPlusTree instance remains in its current state, ready for use within the context.

## Side Effects:
    None

### `bplustree.tree.BPlusTree.__exit__` · *method*

## Summary:
Closes the B+ tree database connection when exiting a context manager block.

## Description:
Implements Python's context manager protocol's `__exit__` method, automatically closing the tree's underlying file connection when exiting a `with` statement. This ensures proper resource cleanup even if exceptions occur within the context block.

## Args:
    exc_type (type): Exception type, or None if no exception occurred.
    exc_val (Exception): Exception value, or None if no exception occurred.
    exc_tb (traceback): Exception traceback, or None if no exception occurred.

## Returns:
    None: Always returns None, allowing normal exception propagation.

## Raises:
    None: This method does not raise exceptions directly, though underlying operations may raise.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._is_open: Set to False to indicate the tree is closed
        - self._mem: Closed via self._mem.close() call

## Constraints:
    Preconditions: The BPlusTree instance must be properly initialized and opened.
    Postconditions: The tree's underlying file connection is closed and the instance is marked as closed.

## Side Effects:
    I/O: Writes to disk via the underlying FileMemory's close operation.
    Resource cleanup: Releases file handles and other system resources associated with the tree.

### `bplustree.tree.BPlusTree.checkpoint` · *method*

## Summary:
Executes a memory checkpoint operation within a write transaction context.

## Description:
This method performs a checkpoint operation on the B+Tree's underlying memory manager by entering a write transaction and calling the memory manager's perform_checkpoint method with reopen_wal=True. It serves as a thin wrapper around the memory manager's checkpoint functionality to ensure proper transactional context.

## Args:
    None

## Returns:
    None

## Raises:
    Exception: May raise exceptions from the underlying memory manager's checkpoint operation or write transaction handling.

## State Changes:
    Attributes READ: 
        - self._mem: The underlying FileMemory instance used for storage management
    Attributes WRITTEN:
        - The internal state of self._mem is modified through the checkpoint operation

## Constraints:
    Preconditions:
        - The B+Tree must be open (self._is_open must be True)
        - The underlying memory manager must be initialized and accessible
    Postconditions:
        - The checkpoint operation is executed within a write transaction
        - The memory manager's perform_checkpoint method is called with reopen_wal=True

## Side Effects:
    - Invokes the memory manager's checkpoint mechanism
    - Manages write transaction context

### `bplustree.tree.BPlusTree.insert` · *method*

## Summary:
Inserts a key-value pair into the B+ tree, updating existing entries when replace=True or creating new entries otherwise.

## Description:
This method implements the core insertion logic for a B+ tree, handling both new key-value pair insertion and replacement of existing keys. It manages the complexity of storing large values that exceed the configured value size by creating overflow pages, and ensures tree balance by splitting nodes when capacity limits are exceeded. The method operates within a write transaction to ensure atomicity of the operation.

## Args:
    key (any): The key to insert or update in the tree
    value (bytes): The value to associate with the key, must be a bytes object
    replace (bool): If True, replaces existing values for the key; if False, raises ValueError if key already exists

## Returns:
    None: This method does not return a value

## Raises:
    ValueError: When replace=False and the key already exists in the tree, or when value is not a bytes object

## State Changes:
    Attributes READ: 
        - self._mem
        - self._root_node
        - self._tree_conf.value_size
    
    Attributes WRITTEN:
        - self._mem (through set_node calls)
        - node.entries (modified through insert_entry operations)
        - node.next_page (updated during leaf splitting)
        - self._root_node_page (updated when creating new root)

## Constraints:
    Preconditions:
        - The tree must be open and accessible
        - The value parameter must be a bytes object
        - The key must be comparable with existing keys in the tree
        
    Postconditions:
        - The key-value pair is stored in the tree structure
        - If value exceeds configured size, overflow pages are created and referenced
        - Tree remains balanced through node splitting when necessary
        - Existing entries are updated when replace=True

## Side Effects:
    - Modifies tree structure through node insertion and splitting operations
    - Creates overflow pages for large values through _create_overflow method
    - May create new root node when splitting the original root
    - Writes to disk via memory manager operations
    - Updates node linkage through next_page pointers

### `bplustree.tree.BPlusTree.batch_insert` · *method*

*No documentation generated.*

### `bplustree.tree.BPlusTree.get` · *method*

## Summary:
Retrieves the value associated with a given key from the B+ tree, returning a default value if the key is not found.

## Description:
This method performs a lookup operation in the B+ tree structure to retrieve the value associated with the specified key. It uses a read transaction to safely access the tree data structure, traverses the tree to find the appropriate leaf node, and then extracts the value from the matching record. If the key does not exist in the tree, it returns the provided default value instead of raising an exception.

The method is designed as a separate utility function to encapsulate the complete tree lookup logic, making it reusable and maintaining clean separation of concerns within the B+ tree implementation.

## Args:
    key (any): The key to search for in the B+ tree. Must be comparable with existing keys in the tree.
    default (bytes, optional): The default value to return if the key is not found. Defaults to None.

## Returns:
    bytes: The value associated with the key if found, or the default value if not found.

## Raises:
    None explicitly raised - ValueError from node.get_entry is caught and handled by returning the default value.

## State Changes:
    Attributes READ: 
        - self._mem
        - self._root_node
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The B+ tree must be properly initialized and opened
        - The key must be comparable with existing keys in the tree
        - The tree structure must be valid (no corrupted nodes)
        
    Postconditions:
        - Returns bytes representing the value if key exists, or the default value if not found
        - The tree structure remains unchanged
        - No modifications are made to the tree during this operation

## Side Effects:
    - Reads from memory using self._mem.read_transaction to access tree nodes
    - May perform I/O operations when accessing overflow pages via _get_value_from_record

### `bplustree.tree.BPlusTree.__contains__` · *method*

## Summary:
Checks if a key exists in the BPlusTree and returns a boolean indicating membership.

## Description:
Implements the Python magic method `__contains__` to support the `in` operator for BPlusTree instances. This method determines whether a given key exists in the tree without retrieving the associated value. It uses a read transaction to ensure thread safety and employs a sentinel object technique to distinguish between keys that don't exist versus keys that exist with a None value.

This method is separate from inline logic because it provides a clean interface for the `in` operator while leveraging the existing tree traversal and retrieval logic in the `get` method. It encapsulates the complexity of handling the distinction between missing keys and keys with None values.

## Args:
    item: The key to search for in the tree. Type is dependent on the tree's key configuration.

## Returns:
    bool: True if the key exists in the tree, False otherwise.

## Raises:
    None explicitly raised, but may propagate exceptions from underlying operations like memory access or tree traversal.

## State Changes:
    Attributes READ: 
    - self._mem (for read_transaction)
    - self._root_node (via _search_in_tree call)
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The tree must be open (self._is_open must be True)
    - The key type must be compatible with the tree's configured key type
    
    Postconditions:
    - The tree remains unchanged
    - The method returns immediately without modifying any tree state

## Side Effects:
    - Acquires a read transaction from self._mem
    - May perform memory reads to traverse the tree structure
    - No external service calls or I/O beyond memory operations

### `bplustree.tree.BPlusTree.__setitem__` · *method*

## Summary:
Sets a key-value pair in the B+ tree, replacing any existing value for the key.

## Description:
This method provides dictionary-style assignment functionality for the B+ tree, allowing users to store key-value pairs where the key is stored in the tree and the value is associated with that key. When a key already exists, the existing value is replaced with the new value. This method internally calls the `insert` method with `replace=True`.

## Args:
    key: The key to set in the tree. Type depends on the tree's configuration.
    value (bytes): The value to associate with the key. Must be a bytes object.

## Returns:
    None: This method does not return a value.

## Raises:
    ValueError: If the value is not a bytes object. The method delegates to insert() which may raise ValueError if the key already exists and replace=False, though this case is prevented by the replace=True parameter.

## State Changes:
    Attributes READ: 
        - self._mem (FileMemory instance)
        - self._root_node_page
    Attributes WRITTEN:
        - self._mem (through write transaction)
        - self._root_node_page (potentially updated during tree restructuring)

## Constraints:
    Preconditions:
        - The B+ tree must be open (self._is_open must be True)
        - The value parameter must be a bytes object
        - The tree must be properly initialized
    Postconditions:
        - The key-value pair is stored in the tree
        - If the key existed previously, it is replaced with the new value
        - The tree structure remains valid

## Side Effects:
    - Modifies the underlying storage through FileMemory operations
    - May trigger tree restructuring operations (node splitting) if the leaf node becomes full
    - Acquires write locks through the write_transaction context manager

### `bplustree.tree.BPlusTree.__getitem__` · *method*

## Summary:
Retrieves values from the BPlusTree using dictionary-style key access or slice-based range queries.

## Description:
This method implements the `__getitem__` magic method, enabling dictionary-style access to the BPlusTree. It supports two access patterns: single key lookup and slice-based range queries. For single keys, it returns the associated value as bytes or raises a KeyError if the key is not found. For slices, it returns a dictionary mapping keys to values for records within the specified range.

## Args:
    item (Union[int, slice]): Either a single key (int) or a slice object defining a range of keys to retrieve.

## Returns:
    Union[bytes, dict]: For single keys, returns the associated value as bytes. For slices, returns a dictionary mapping integer keys to bytes values.

## Raises:
    KeyError: When attempting to access a non-existent key with single-key access.
    ValueError: When using a slice with a custom step or when the start of a slice is greater than or equal to its stop.

## State Changes:
    Attributes READ: 
        - self._mem (FileMemory): Used for read transactions and node access
        - self._root_node: Accessed via property to find nodes during search
        - self._left_record_node: Used when slice start is None to begin iteration

## Constraints:
    Preconditions:
        - The tree must be open (self._is_open must be True)
        - The key or slice parameters must be valid for the tree's configuration
    Postconditions:
        - For single key access: Returns bytes value or raises KeyError
        - For slice access: Returns a dictionary with all matching records

## Side Effects:
    - Performs read operations on the underlying storage through self._mem
    - Uses read transactions to ensure data consistency
    - May access multiple nodes in the tree structure during search operations

### `bplustree.tree.BPlusTree.__len__` · *method*

## Summary:
Returns the total number of records stored in the B+ tree by traversing all leaf nodes from the leftmost record node.

## Description:
Calculates the total count of records in the B+ tree by performing a sequential traversal of all leaf nodes starting from the leftmost record node. This method implements the Python `__len__` protocol and is optimized for read operations using a memory transaction.

## Args:
    None

## Returns:
    int: The total number of records stored in the tree.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self._mem (for read_transaction and get_node)
    - self._left_record_node (to start traversal)
    - node.next_page (to traverse to next node)
    - node.entries (to count entries in each node)

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The tree must be open (self._is_open = True)
    - The tree's memory system must be properly initialized
    - All nodes in the linked list of leaf nodes must be accessible
    
    Postconditions:
    - The method returns an integer representing the total record count
    - The tree structure remains unchanged
    - No modifications are made to any tree nodes or metadata

## Side Effects:
    - Acquires a read transaction from self._mem
    - Reads from disk/memory pages via self._mem.get_node() calls
    - May cause page faults or disk I/O during node retrieval

### `bplustree.tree.BPlusTree.__length_hint__` · *method*

## Summary:
Returns an estimated length hint for the number of records in the B+ tree, used by Python's iterator protocol.

## Description:
This method provides an estimated count of records in the B+ tree to support efficient iteration operations. It's designed to give a reasonable approximation of the tree size without having to traverse the entire structure. The estimation accounts for different tree configurations, particularly handling the special case of a lonely root node.

The method is typically called by Python's iterator protocol when working with BPlusTree instances. It's part of the standard iterator protocol and helps optimize iteration performance by providing a hint about the expected number of items.

## Args:
    None

## Returns:
    int: An estimated number of records in the tree. For a lonely root node, returns max_children // 2. For regular trees, returns an estimated count based on memory usage and node capacity.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self._mem (FileMemory instance)
    - self._root_node (property accessing the root node)
    - self._mem.last_page (property accessing last page number)
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The tree must be open (self._is_open should be True)
    - The method must be called within a read transaction context
    - The root node must be accessible and properly initialized
    
    Postconditions:
    - The method returns a non-negative integer representing an estimated count
    - The returned value is an approximation, not necessarily the exact count
    - The estimation algorithm handles both regular and special root node cases

## Side Effects:
    - Accesses memory pages through self._mem.read_transaction
    - Reads from disk/memory-backed storage via FileMemory interface
    - No modifications to persistent state

### `bplustree.tree.BPlusTree.__iter__` · *method*

## Summary:
Returns an iterator over the keys stored in the B+ tree in ascending order.

## Description:
Provides a generator interface for iterating through all keys in the B+ tree. When called without arguments, it iterates through all keys in ascending order. When provided with a slice, it iterates through keys within the specified range. This method is designed to be efficient and safe for concurrent access through read transactions.

## Args:
    slice_ (Optional[slice]): An optional slice object defining a range of keys to iterate over. If None, iterates through all keys. Defaults to None.

## Returns:
    Iterator[Union[int, bytes]]: An iterator yielding keys from the B+ tree in ascending order. The exact type depends on the serializer used during tree creation.

## Raises:
    ValueError: If the slice has a non-None step value or if start >= stop in a slice.
    StopIteration: Raised internally when reaching the end of the iteration range.

## State Changes:
    Attributes READ: 
        - self._mem (FileMemory instance)
        - self._iter_slice (method)
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The B+ tree must be open (self._is_open must be True)
        - The tree must have valid metadata and root node
    Postconditions:
        - The method returns an iterator that yields keys in ascending order
        - No modifications are made to the tree structure

## Side Effects:
    - Acquires a read transaction from self._mem
    - Reads from disk/memory pages through self._mem.get_node() and self._mem.get_page()
    - May perform multiple memory/page reads during iteration

### `bplustree.tree.BPlusTree.items` · *method*

## Summary:
Returns an iterator over key-value pairs stored in the B+ tree, optionally filtered by a key range slice.

## Description:
Provides iteration over all key-value pairs in the B+ tree. When called without arguments, it iterates over all entries in the tree in key-sorted order. When provided with a slice argument, it iterates over entries within the specified key range. This method is designed to be efficient for large datasets by using lazy evaluation through iterators.

## Args:
    slice_ (Optional[slice], optional): A slice object defining the key range to iterate over. The slice can specify start and stop keys but not a step. If None, iterates over all entries in the tree. Defaults to None.

## Returns:
    Iterator[tuple]: An iterator yielding tuples of (key, value) where key is the record key and value is the associated bytes value.

## Raises:
    ValueError: When the slice has a non-None step value (custom step iteration is not supported) or when start >= stop (backwards iteration is not supported).

## State Changes:
    Attributes READ: 
        - self._mem
        - self._iter_slice
        - self._get_value_from_record
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The B+ tree must be open (self._is_open is True)
        - The slice_ argument must be a valid slice object with appropriate start/stop values
        - The tree must have valid node structure and metadata
    
    Postconditions:
        - The method returns an iterator that yields (key, value) tuples in key-sorted order
        - The iterator stops when reaching the slice.stop boundary or end of the tree
        - All returned key-value pairs have keys within [slice_.start, slice_.stop) range

## Side Effects:
    - Reads from disk/memory through self._mem.read_transaction and self._mem.get_node() calls
    - May perform multiple memory/file operations during node traversal
    - No modifications to persistent storage during iteration (only read operations)

### `bplustree.tree.BPlusTree.values` · *method*

## Summary:
Returns an iterator of byte values from records in the B+ tree, optionally filtered by a key range.

## Description:
Provides access to all value bytes stored in the B+ tree. When called without arguments, it returns all values in key-sorted order. When provided with a slice argument, it returns values within the specified key range. This method is designed for efficient range-based iteration over tree values without loading all data into memory simultaneously.

## Args:
    slice_ (Optional[slice], optional): A slice object defining the key range to iterate over. Defaults to None, which means iterate over all keys.

## Returns:
    Iterator[bytes]: An iterator yielding byte sequences representing the values stored in the tree records.

## Raises:
    ValueError: When the slice has a non-None step value (custom step iteration is not supported) or when start >= stop (backwards iteration is not supported).

## State Changes:
    Attributes READ: 
        - self._mem
        - self._iter_slice
        - self._get_value_from_record
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The B+ tree must be open (self._is_open is True)
        - The slice_ argument must be a valid slice object with appropriate start/stop values
        - The tree must have valid node structure and metadata
    
    Postconditions:
        - The method returns an iterator that yields bytes in key-sorted order
        - The iterator stops when reaching the slice.stop boundary or end of the tree
        - All returned values correspond to records with keys within [slice_.start, slice_.stop) range

## Side Effects:
    - Reads from disk/memory through self._mem.read_transaction and self._mem.get_node() calls
    - May perform multiple memory/file operations during node traversal
    - No modifications to persistent storage during iteration (only read operations)

### `bplustree.tree.BPlusTree.__bool__` · *method*

## Summary:
Returns True if the BPlusTree contains at least one record, False otherwise.

## Description:
Implements the Python special method `__bool__` to determine the truthiness of the BPlusTree instance. This method efficiently checks whether the tree has any data by iterating through the tree's records and returning True on the first record found, or False if no records exist. The iteration is performed within a read transaction to ensure thread safety.

## Args:
    None

## Returns:
    bool: True if the tree contains at least one record, False if the tree is empty.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self._mem (FileMemory instance for tree storage)
    - self (used to invoke __iter__ method)

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The tree must be open (self._is_open should be True)
    - The tree's memory manager (_mem) must be properly initialized
    
    Postconditions:
    - The method does not modify the tree's state
    - The method returns a boolean value indicating tree emptiness

## Side Effects:
    - Acquires a read transaction from self._mem
    - Reads from disk/storage through the memory manager
    - May trigger node loading from storage during iteration

### `bplustree.tree.BPlusTree.__repr__` · *method*

## Summary:
Returns a string representation of the BPlusTree object showing its filename and configuration.

## Description:
This method provides a human-readable representation of the BPlusTree instance, displaying the underlying filename and tree configuration. It is called automatically when the built-in repr() function is used on a BPlusTree instance, and can also be invoked directly.

## Args:
    None

## Returns:
    str: A formatted string in the pattern '<BPlusTree: {filename} {tree_conf}>', where filename is the file path and tree_conf represents the tree configuration.

## Raises:
    None

## State Changes:
    Attributes READ: 
    - self._filename: String containing the file path
    - self._tree_conf: TreeConf object containing tree configuration parameters

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self._filename must be a string
    - self._tree_conf must be a TreeConf object
    
    Postconditions:
    - The returned string follows the format '<BPlusTree: {filename} {tree_conf}>'
    - The method does not modify any object state

## Side Effects:
    None

### `bplustree.tree.BPlusTree._initialize_empty_tree` · *method*

## Summary:
Initializes an empty B+ tree structure by creating a lonely root node and setting up initial metadata.

## Description:
This private method is responsible for setting up the foundational structure of a new, empty B+ tree. It is called during the initialization process when no existing metadata is found in the storage. The method creates a lonely root node (which represents the initial state of an empty tree) and stores both the node and tree configuration metadata.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self._mem (FileMemory instance)
    - self.LonelyRootNode (partial class constructor)
    - self._tree_conf (TreeConf instance)
    
    Attributes WRITTEN:
    - self._root_node_page (int): Set to the next available page number from memory
    - self._mem (FileMemory instance): Modified through set_node() and set_metadata() calls

## Constraints:
    Preconditions:
    - The B+ tree instance must be properly initialized with a FileMemory instance
    - The tree must be in an uninitialized state (no existing metadata)
    - The FileMemory instance must be capable of providing next available pages
    
    Postconditions:
    - A lonely root node is created and stored in memory
    - Metadata containing the root node page and tree configuration is stored
    - The _root_node_page attribute is set to the newly allocated page number

## Side Effects:
    - Writes to persistent storage via FileMemory operations
    - Creates a new page allocation in the underlying storage
    - Modifies the tree's metadata in persistent storage

### `bplustree.tree.BPlusTree._create_partials` · *method*

## Summary:
Creates partially applied constructor functions for node and entry classes bound with the tree configuration.

## Description:
Initializes specialized constructor functions for various node and entry classes by pre-binding the tree configuration. This method is called during object initialization to set up factory functions that can create instances of these classes with the appropriate configuration already applied.

The method is invoked during BPlusTree.__init__ as part of the object setup process, ensuring that all node and entry creation operations have access to the configured tree parameters without requiring explicit passing of the configuration each time.

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
    Preconditions: The method assumes self._tree_conf has been initialized before calling
    Postconditions: All partial constructor functions (LonelyRootNode, RootNode, InternalNode, LeafNode, Record, Reference) are available as instance attributes

## Side Effects:
    None

### `bplustree.tree.BPlusTree._root_node` · *method*

## Summary:
Provides access to the root node of the B+ tree, which can be either a LonelyRootNode or RootNode instance.

## Description:
This property retrieves and returns the root node of the B+ tree structure. It accesses the root node from memory using the stored root node page reference and ensures it's of the correct type through an assertion. This abstraction centralizes access to the tree's root node, providing a consistent interface for all tree operations.

The root node serves as the starting point for all tree traversals and operations. It can be either a LonelyRootNode (representing an empty tree or initial state) or a RootNode (representing a fully initialized tree with entries). This property ensures that all tree operations begin from a properly typed root node.

Common usage contexts:
- Search operations (find records by key)
- Insertion operations (add new records)
- Iteration operations (traverse all records)
- Size calculation operations (count total records)
- Tree structure maintenance operations

## Args:
None

## Returns:
Union['LonelyRootNode', 'RootNode']: The root node of the B+ tree, which can be either a LonelyRootNode (initial state) or RootNode (after tree has been modified).

## Raises:
AssertionError: When the retrieved node from memory is not an instance of either LonelyRootNode or RootNode, indicating a potential corruption or initialization error.

## State Changes:
Attributes READ: 
- self._mem (FileMemory instance for accessing nodes)
- self._root_node_page (page number of the root node)

Attributes WRITTEN: None

## Constraints:
Preconditions:
- The tree must be initialized and opened (self._is_open must be True)
- The root node page reference must be valid
- The memory system must be functioning properly
- The node at the root node page must exist and be readable

Postconditions:
- Returns a valid node instance of type LonelyRootNode or RootNode
- The returned node is properly loaded from memory
- The node is guaranteed to be one of the two expected types due to assertion

## Side Effects:
- Memory access via self._mem.get_node() call
- Potential page loading from disk if not cached
- Assertion failure if node type is incorrect (not a side effect in normal operation)

### `bplustree.tree.BPlusTree._left_record_node` · *method*

## Summary:
Returns the leftmost leaf node or lonely root node in the B+ tree by traversing from the root node.

## Description:
This method performs a leftward traversal of the B+ tree structure, starting from the root node and following the smallest entry's before reference until reaching either a leaf node or a lonely root node. This traversal is commonly used to find the first record in the tree for iteration purposes.

## Args:
    None

## Returns:
    Union[LonelyRootNode, LeafNode]: The leftmost node in the tree structure, which will be either a leaf node containing records or a lonely root node.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._root_node, self._mem
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self._root_node must be initialized
    - self._mem must be a valid memory manager with get_node method
    - The tree structure must be valid (no cycles in node references)
    
    Postconditions:
    - Returns either a LeafNode or LonelyRootNode instance
    - The returned node is guaranteed to be the leftmost node in the tree

## Side Effects:
    - Calls self._mem.get_node() which likely performs memory or disk I/O operations
    - May trigger page loading from storage if nodes are not cached

### `bplustree.tree.BPlusTree._iter_slice` · *method*

## Summary:
Returns an iterator over records in the B+ tree within a specified key range.

## Description:
This method implements range-based iteration over the records stored in the B+ tree. It allows retrieving records within a specified key slice, supporting start and stop bounds but not custom steps. The method traverses the tree structure efficiently, starting from either the leftmost leaf node or a specific key location, and continues through linked leaf nodes until reaching the end of the range or the end of the tree.

## Args:
    slice_ (slice): A slice object specifying the key range to iterate over. The slice can have start and stop values but must not have a step. Start and stop values represent key boundaries for the iteration.

## Returns:
    Iterator[Record]: An iterator yielding Record objects whose keys fall within the specified slice range.

## Raises:
    ValueError: When the slice has a non-None step value (custom step iteration is not supported) or when start >= stop (backwards iteration is not supported).

## State Changes:
    Attributes READ: 
        - self._left_record_node
        - self._root_node
        - self._mem
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The B+ tree must be open (self._is_open is True)
        - The slice_ argument must be a valid slice object with appropriate start/stop values
        - The tree must have valid node structure and metadata
    
    Postconditions:
        - The method returns an iterator that yields Record objects in key-sorted order
        - The iterator stops when reaching the slice.stop boundary or end of the tree
        - All returned records have keys within [slice_.start, slice_.stop) range

## Side Effects:
    - Reads from disk/memory through self._mem.get_node() calls
    - May perform multiple memory/file operations during node traversal
    - No modifications to persistent storage during iteration (only read operations)

### `bplustree.tree.BPlusTree._search_in_tree` · *method*

## Summary:
Recursively traverses a B+ tree to find the leaf node containing the specified key.

## Description:
This private method implements the core tree traversal logic for searching keys in a B+ tree structure. It navigates from the root node down to the appropriate leaf node by comparing the search key against node boundary values and following the correct child pointers. The method handles special cases for root nodes and performs recursive descent through internal nodes until reaching a leaf or lonely root node.

## Args:
    key (any): The search key to locate in the tree
    node (Node): The current node being examined during traversal

## Returns:
    Node: The leaf node or lonely root node containing the key, or the node itself if it's already a leaf/lone root

## Raises:
    AssertionError: When no valid page reference can be determined during traversal (should not occur with valid tree structure)

## State Changes:
    Attributes READ: 
        - node.smallest_key
        - node.biggest_key  
        - node.entries
        - node.smallest_entry.before
        - node.biggest_entry.after
        - node.entries[i].key
        - node.entries[i].after
    
    Attributes WRITTEN:
        - child_node.parent (set to current node)

## Constraints:
    Preconditions:
        - The tree must be properly structured with valid node references
        - The key must be comparable with node key values
        - The node parameter must be a valid node in the tree structure
        
    Postconditions:
        - Returns either a LeafNode or LonelyRootNode (terminal nodes)
        - The returned node contains the key or would contain it if inserted
        - All intermediate nodes in the traversal path have their parent pointers set correctly

## Side Effects:
    - Reads from memory using self._mem.get_node() to fetch child nodes
    - Modifies child node's parent attribute during traversal

### `bplustree.tree.BPlusTree._split_leaf` · *method*

## Summary:
Splits a leaf node into two nodes when it exceeds capacity, managing parent references and handling special root node cases.

## Description:
This method implements the leaf node splitting mechanism for a B+ tree during insertion operations when a leaf node becomes full. It divides the entries of the original node into two separate leaf nodes, updates parent references, and maintains proper sequential linkage between nodes.

The method distinguishes between two main scenarios:
1. When the node being split is a LonelyRootNode (the only node in the tree)
2. When the node being split is a regular leaf node with a parent

In the first case, the lonely root is converted to a regular leaf node and a new root is created. In the second case, the parent node is updated with a reference to the new node, potentially triggering further splitting if the parent is also full.

## Args:
    old_node (Node): The leaf node that needs to be split. Must be a LeafNode or LonelyRootNode instance.

## Returns:
    None: This method does not return a value.

## Raises:
    None explicitly raised: This method does not raise exceptions directly, though underlying operations may raise exceptions from memory management or node operations.

## State Changes:
    Attributes READ: 
        - self._mem (FileMemory): Used to access next available page and manage node persistence
        - old_node.parent: Parent node reference for updating parent structure
        - old_node.next_page: Next page reference for linking nodes
        - old_node.page: Page identifier for node references
        - old_node.smallest_key: Key value for reference creation
        - old_node.entries: Entries contained in the node being split
        
    Attributes WRITTEN:
        - old_node.next_page: Updated to point to the new node's page
        - self._mem: Modified through set_node() calls to persist updated nodes

## Constraints:
    Preconditions:
        - The old_node parameter must be a valid Node instance (LeafNode or LonelyRootNode)
        - The tree must be in a valid state for node splitting operations
        - Memory system must be able to allocate a new page for the new node
        
    Postconditions:
        - A new leaf node is created with half of the original node's entries
        - The parent node is updated with a reference to the new node
        - The old node's next_page pointer is updated to link to the new node
        - Both nodes are persisted to memory
        - If the old node was a LonelyRootNode, it's converted to a regular leaf node and a new root is created
        - If the parent cannot accommodate the new reference, parent splitting occurs recursively

## Side Effects:
    - Writes to disk through the FileMemory system
    - Modifies node structure in memory
    - May trigger additional node splitting operations if parent cannot accommodate new entry
    - Updates node linkage through next_page pointers
    - May create a new root node if splitting the original root

### `bplustree.tree.BPlusTree._split_parent` · *method*

## Summary:
Splits an internal node and updates its parent node when the internal node becomes full, potentially creating a new root if needed.

## Description:
This method handles the splitting of internal nodes in a B+ tree when a node exceeds its capacity. It creates a new sibling node with half of the original node's entries, updates the parent node with a reference to the new node, and manages the tree structure accordingly. The method handles special cases for root nodes and recursively splits parent nodes when necessary.

The method is called during tree operations when internal nodes become full, similar to how `_split_leaf` handles leaf node splitting. It ensures the tree maintains its B+ tree properties by properly redistributing entries and updating parent-child relationships.

Known callers:
- `_split_leaf`: Called when a leaf node split causes the parent node to exceed capacity
- `_split_parent`: Called recursively when a parent node also needs splitting due to the addition of a new reference

## Args:
    old_node (Node): The internal node that needs to be split. Must be an InternalNode or RootNode instance.

## Returns:
    None: This method does not return a value.

## Raises:
    None explicitly raised: This method does not raise exceptions directly, though underlying operations may raise exceptions from memory management or node operations.

## State Changes:
    Attributes READ: 
        - self._mem (FileMemory): Used to access next available page and manage node persistence
        - old_node.parent: Parent node reference for updating parent structure
        - old_node.page: Page identifier for node references
        - old_node.entries: Entries contained in the node being split
        
    Attributes WRITTEN:
        - self._mem: Modified through set_node() calls to persist updated nodes
        - old_node.page: Updated to reflect the new node's page after splitting
        - old_node.parent: Updated to reference the new parent structure

## Constraints:
    Preconditions:
        - The old_node parameter must be a valid Node instance (InternalNode or RootNode)
        - The tree must be in a valid state for node splitting operations
        - Memory system must be able to allocate a new page for the new node
        
    Postconditions:
        - A new internal node is created with half of the original node's entries
        - The parent node is updated with a reference to the new node
        - Both nodes are persisted to memory
        - If the old node was a RootNode, it's converted to an InternalNode and a new root is created
        - If the parent cannot accommodate the new reference, parent splitting occurs recursively

## Side Effects:
    - Writes to disk through the FileMemory system
    - Modifies node structure in memory
    - May trigger additional node splitting operations if parent cannot accommodate new entry
    - May create a new root node if splitting the original root
    - Recursively calls itself when parent nodes also need splitting

### `bplustree.tree.BPlusTree._create_new_root` · *method*

## Summary:
Creates a new root node for the B+ tree by initializing a root node with a reference and updating the tree's metadata.

## Description:
This method is responsible for creating a new root node when the existing root node needs to be split. It is called during tree operations when a node becomes too large to fit in a single page, specifically when splitting leaf nodes or internal nodes. The method constructs a new root node using the provided reference, updates the tree's root node page reference, and persists the new root node to memory.

Known callers:
- `_split_leaf`: Called when splitting a leaf node that was previously a lonely root
- `_split_parent`: Called when splitting an internal node that was previously the root

## Args:
    reference (Reference): A reference object containing key and page information to initialize the new root node.

## Returns:
    None: This method does not return a value.

## Raises:
    None explicitly raised: This method does not raise any exceptions directly, though underlying memory operations may raise exceptions.

## State Changes:
    Attributes READ: 
        - self._mem (FileMemory): Used to access next available page and set metadata/node
        - self._tree_conf (TreeConf): Used to set metadata
    
    Attributes WRITTEN:
        - self._root_node_page: Updated to point to the new root node's page
        - self._mem: Modified through set_metadata() and set_node() calls

## Constraints:
    Preconditions:
        - The tree must be open (self._is_open is True)
        - The reference parameter must be a valid Reference object
        - Memory system must be able to allocate a new page
        
    Postconditions:
        - A new root node is created with the provided reference
        - The tree's root node page reference is updated
        - The new root node is persisted in memory
        - Tree metadata is updated with the new root page and configuration

## Side Effects:
    - Writes to disk through the FileMemory system
    - Modifies the tree's metadata on disk
    - Persists a new node to disk
    - Updates internal state variables

### `bplustree.tree.BPlusTree._create_overflow` · *method*

## Summary:
Creates overflow pages for large byte values that exceed the page size limit.

## Description:
This method handles the creation of overflow pages when a value exceeds the maximum payload that can fit in a single page. It splits the large value into appropriately sized chunks, creates linked pages with proper metadata, and returns the page number of the first overflow page. This method is called internally by the tree's insertion logic when values are too large to store directly in leaf nodes.

## Args:
    value (bytes): The large byte string that needs to be stored across multiple pages.

## Returns:
    int: The page number of the first overflow page created.

## Raises:
    None explicitly raised, but may raise exceptions from underlying memory operations.

## State Changes:
    Attributes READ: 
        - self._tree_conf.page_size
        - self._tree_conf.value_size
        - self._mem.next_available_page
    
    Attributes WRITTEN:
        - self._mem (through set_page calls)

## Constraints:
    Preconditions:
        - The value parameter must be a bytes object
        - The tree must be open and accessible
        - The value must exceed the configured value_size limit
        
    Postconditions:
        - All overflow pages are properly initialized with correct page references
        - The returned page number points to the first page in the overflow chain
        - Memory is updated with the overflow page data

## Side Effects:
    - Writes to disk via memory manager operations
    - Modifies the page allocation state through `next_available_page` consumption

### `bplustree.tree.BPlusTree._read_from_overflow` · *method*

## Summary:
Reconstructs a complete byte value from a chain of overflow pages in the B+ tree structure.

## Description:
This private method reads data that has been split across multiple overflow pages when a value exceeds the maximum payload size that can fit in a single page. It traverses the linked list of overflow pages starting from the first page reference, extracting the payload data from each page and concatenating it into a complete byte sequence. This method is called internally by `_get_value_from_record` when a record contains an overflow page reference instead of inline data.

## Args:
    first_overflow_page (int): The page number of the first overflow page in the chain

## Returns:
    bytes: The complete reconstructed byte value from all overflow pages

## Raises:
    None explicitly raised, but may propagate exceptions from underlying memory operations (e.g., if pages cannot be read from storage)

## State Changes:
    Attributes READ: self._mem
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The first_overflow_page parameter must be a valid page number in the tree's memory space
        - All overflow pages in the chain must be readable from memory
        - The overflow page data must follow the expected format with page reference, length, and payload sections
        
    Postconditions:
        - Returns a complete byte sequence matching the original value that was split across overflow pages
        - The method will traverse the entire overflow chain until reaching the termination marker (page reference of 0)

## Side Effects:
    I/O operations: Reads from memory pages via self._mem.get_page() to reconstruct the overflow data

### `bplustree.tree.BPlusTree._get_value_from_record` · *method*

## Summary:
Retrieves the complete value bytes from a record, handling both inline values and overflow page chains in the B+ tree structure.

## Description:
This private method extracts the full value associated with a record by checking if the value is stored inline or needs to be reconstructed from overflow pages. When a record's value field is None, it follows the overflow page chain to reconstruct the complete value by reading sequential overflow pages until reaching the end marker (page reference of 0).

## Args:
    record (Record): A record object containing either an inline value or overflow page reference

## Returns:
    bytes: The complete value bytes stored in the record, whether inline (when record.value is not None) or reconstructed from overflow pages

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._mem, record.value, record.overflow_page
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The record parameter must be a valid Record instance with proper value and overflow_page attributes; overflow pages must be readable from memory
    Postconditions: Returns bytes representing the complete value, or raises an exception if overflow pages cannot be read

## Side Effects:
    I/O operations: Reads from memory pages via self._mem.get_page() when handling overflow pages

