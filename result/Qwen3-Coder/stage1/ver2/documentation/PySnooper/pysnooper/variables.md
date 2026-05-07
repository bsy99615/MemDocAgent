# `variables.py`

## `pysnooper.variables.needs_parentheses` · *function*

*No documentation generated.*

## `pysnooper.variables.BaseVariable` · *class*

*No documentation generated.*

### `pysnooper.variables.BaseVariable.__init__` · *method*

## Summary:
Initializes a BaseVariable instance by storing the source code, compiling it, and determining appropriate formatting for unambiguous representation.

## Description:
The BaseVariable constructor prepares a variable tracking object by processing the source code expression, compiling it for execution, and determining whether parentheses are needed to prevent parsing ambiguities. This method is called during the instantiation of variable tracking objects in the pysnooper debugging tool.

## Args:
    source (str): The source code expression to be tracked and evaluated
    exclude (tuple, optional): Tuple of variable names to exclude from tracking. Defaults to empty tuple.

## Returns:
    None: This method initializes instance attributes but does not return a value.

## Raises:
    SyntaxError: If the source code cannot be compiled into valid Python bytecode

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.source: Stores the original source code string
    - self.exclude: Stores the normalized exclude tuple
    - self.code: Stores the compiled bytecode of the source
    - self.unambiguous_source: Stores the source with surrounding parentheses if needed

## Constraints:
    Preconditions:
    - source must be a valid Python expression string
    - exclude must be convertible to a tuple of strings
    
    Postconditions:
    - All instance attributes are properly initialized
    - self.code contains valid compiled bytecode
    - self.unambiguous_source preserves the original semantics while ensuring clarity

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes internal state.

### `pysnooper.variables.BaseVariable.items` · *method*

## Summary:
Evaluates a variable expression in a given frame context and extracts its items for debugging inspection.

## Description:
This method executes the variable's source code expression within the provided frame's local and global scope to obtain the variable's value. It then delegates to the abstract `_items` method to extract and format the variable's contents for debugging purposes. The method provides graceful error handling by returning an empty tuple when evaluation fails.

The `items` method is part of the pysnooper debugging framework and is called during variable inspection when tracing function execution. It serves as the bridge between variable expression evaluation and item extraction for display in debug output.

## Args:
    frame (FrameType): The execution frame in which to evaluate the variable expression
    normalize (bool): Flag indicating whether to normalize the extracted items for consistent representation (default: False)

## Returns:
    tuple: A tuple containing the items extracted from the evaluated variable value, or an empty tuple if evaluation fails

## Raises:
    None: This method catches all exceptions during evaluation and returns an empty tuple

## State Changes:
    Attributes READ: 
    - self.code: The compiled bytecode of the variable source expression
    - self.source: The original source code string of the variable
    - self.exclude: The tuple of excluded variable names
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The frame parameter must be a valid Python frame object
    - The variable's source code must be compilable and evaluatable in the frame context
    - The method should only be called from within the tracing system
    
    Postconditions:
    - If evaluation succeeds, returns results from the subclass's _items implementation
    - If evaluation fails, returns an empty tuple
    - The returned tuple is suitable for further processing by the tracing system

## Side Effects:
    I/O: May involve reading from frame's local/global namespaces during evaluation
    External service calls: None
    Mutations to objects outside self: None

### `pysnooper.variables.BaseVariable._items` · *method*

## Summary:
Returns iterable items from a variable's evaluated value for debugging inspection.

## Description:
This abstract method is responsible for extracting and formatting items from a variable's evaluated value when debugging with pysnooper. It's called internally by the `items` method after successfully evaluating a variable in a given frame context. The method must be implemented by subclasses to handle different types of variable values appropriately.

## Args:
    key (any): The evaluated value of the variable being inspected
    normalize (bool): Flag indicating whether to normalize the items for consistent representation

## Returns:
    iterable: An iterable collection of items extracted from the evaluated variable value

## Raises:
    NotImplementedError: Always raised by the base implementation, must be overridden by subclasses

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - Must be called from within the `items` method after successful variable evaluation
    - The `key` parameter contains the evaluated value of a variable
    - The `normalize` parameter indicates normalization preference
    
    Postconditions:
    - Must return an iterable of items that can be processed by the caller
    - Implementation must be consistent with the variable type being inspected

## Side Effects:
    None

### `pysnooper.variables.BaseVariable._fingerprint` · *method*

## Summary:
Returns a tuple that uniquely identifies this variable by its type, source code, and exclusion configuration for use in equality and hashing operations.

## Description:
This property generates a fingerprint tuple containing three elements that uniquely identify a BaseVariable instance: the class type, the source code string, and the exclusion parameters. The fingerprint is used internally by the `__hash__` and `__eq__` methods to enable BaseVariable instances to function correctly in hash-based collections like sets and dictionaries. This method exists as a separate property to avoid code duplication and ensure consistency between hashing and equality operations.

## Args:
    None

## Returns:
    tuple: A 3-element tuple containing:
        - type(self): The class type of this variable instance
        - self.source: The source code string used to evaluate this variable
        - self.exclude: The exclusion parameters configured for this variable

## Raises:
    None

## State Changes:
    Attributes READ: 
    - self.source: Read to include in the fingerprint tuple
    - self.exclude: Read to include in the fingerprint tuple

## Constraints:
    Preconditions:
    - The instance must have been initialized with valid source and exclude parameters
    - All elements in the returned tuple must be hashable (which they are by design)
    
    Postconditions:
    - The returned tuple remains consistent for the lifetime of the object
    - Equal objects will have equal fingerprints
    - Objects with equal fingerprints will compare as equal

## Side Effects:
    None

### `pysnooper.variables.BaseVariable.__hash__` · *method*

## Summary:
Computes and returns the hash value of this variable based on its fingerprint for use in hash-based collections.

## Description:
This method implements Python's magic `__hash__` protocol, enabling BaseVariable instances to be used as dictionary keys or set elements. The hash is computed from the variable's fingerprint, which uniquely identifies it by combining its type, source code, and exclusion configuration.

## Args:
    None

## Returns:
    int: The hash value of the variable's fingerprint, suitable for use in hash tables and sets.

## Raises:
    TypeError: If the fingerprint contains unhashable elements, though this is prevented by the design of _fingerprint.

## State Changes:
    Attributes READ: 
    - self._fingerprint: Used to compute the hash value

## Constraints:
    Preconditions:
    - The `_fingerprint` property must return hashable elements
    - The `__eq__` method must be consistent with this hash implementation
    
    Postconditions:
    - The returned hash value remains constant for the lifetime of the object
    - Objects that compare equal must have equal hash values

## Side Effects:
    None

### `pysnooper.variables.BaseVariable.__eq__` · *method*

## Summary:
Compares two BaseVariable instances for equality based on their type, source code, and exclusion parameters.

## Description:
This method implements equality comparison for BaseVariable objects. Two BaseVariable instances are considered equal if they are instances of the same class (or subclass) and have identical source code and exclusion parameters. This method is part of the standard Python object protocol and enables using BaseVariable instances in contexts requiring equality comparisons, such as set operations or dictionary keys.

## Args:
    other (object): Another object to compare with this BaseVariable instance.

## Returns:
    bool: True if the other object is a BaseVariable instance with the same fingerprint (type, source, and exclude parameters); False otherwise.

## Raises:
    None

## State Changes:
    Attributes READ: 
    - self._fingerprint: Used to compare the identity of this variable with another
    - other._fingerprint: Used to compare the identity of this variable with another (accessed via isinstance check)

## Constraints:
    Preconditions:
    - The method can be called on any BaseVariable instance
    - The other object can be of any type
    
    Postconditions:
    - Returns a boolean value indicating equality status
    - If True, both instances share the same type, source, and exclude parameters

## Side Effects:
    None

## `pysnooper.variables.CommonVariable` · *class*

*No documentation generated.*

### `pysnooper.variables.CommonVariable._items` · *method*

## Summary:
Returns a list of key-value pairs representing the inspected variable's contents for debugging display.

## Description:
Constructs a structured representation of a variable's contents by pairing keys with their formatted values. This method is used internally by the pysnooper debugging tool to generate human-readable variable inspection output. It processes the main value object by extracting its keys through `_safe_keys()`, retrieving individual values via `_get_value()`, and formatting keys appropriately using `_format_key()`. The resulting list contains tuples of (key_representation, value_representation) suitable for display in debugging output.

## Args:
    main_value (Any): The variable value to inspect and convert to key-value pairs
    normalize (bool): Whether to apply normalization to value representations to remove memory addresses and other unstable identifiers

## Returns:
    list[tuple[str, str]]: A list of (key, value) tuples where each key is formatted using `unambiguous_source` prefix and `self._format_key()`, and each value is represented using `utils.get_shortish_repr()`. The first element is always the main variable itself, followed by its contents.

## Raises:
    None: This method does not raise exceptions directly; it catches and ignores all exceptions during key retrieval and value extraction.

## State Changes:
    Attributes READ: 
    - self.source: Used for the initial key-value pair
    - self.unambiguous_source: Used to prefix formatted keys
    - self.exclude: Used to filter out excluded keys
    - self._safe_keys: Called to iterate over available keys
    - self._get_value: Called to retrieve individual values
    - self._format_key: Called to format individual keys
    - utils.get_shortish_repr: Called to format values

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - main_value must be a valid object that can be processed by the underlying key and value extraction methods
    - self._safe_keys(), self._get_value(), and self._format_key() must be properly implemented by subclasses
    - self.exclude must be iterable and contain elements compatible with the 'in' operator for key checking

    Postconditions:
    - Returns a list of tuples where each tuple contains a formatted key string and a formatted value string
    - The first tuple always represents the main variable itself
    - All subsequent tuples represent the variable's contents with proper key formatting

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only processes objects and generates string representations.

### `pysnooper.variables.CommonVariable._safe_keys` · *method*

## Summary:
Safely yields keys from a main value while suppressing all exceptions during key extraction.

## Description:
Provides a fault-tolerant mechanism for extracting keys from variable values during debugging inspection. This method wraps the `_keys()` method call with exception handling to prevent crashes when inspecting objects that may not support key-based access or whose key extraction might fail. It is primarily used by the `_items()` method to enumerate variable contents for debugging output.

The method is called during variable inspection in the pysnooper debugging tool, where it iterates through available keys using `self._keys(main_value)` and yields each key. When any exception occurs during key iteration, it is caught and suppressed, ensuring that variable inspection continues even for problematic objects.

## Args:
    main_value (Any): The variable value from which to extract keys. This parameter is passed to the underlying `_keys()` implementation.

## Returns:
    Generator[str]: A generator yielding keys from the main_value. Returns an empty generator if no keys are available or if an exception occurs during key extraction.

## Raises:
    None: Exceptions during key extraction are caught and suppressed internally.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The `main_value` parameter should be a valid object that can be processed by the underlying `_keys()` implementation
    - The `_keys()` method should be implemented by subclasses to provide appropriate key extraction logic

    Postconditions:
    - Always returns a generator (even if empty)
    - Does not modify any instance state
    - Exception handling ensures robustness during debugging inspection

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only iterates over keys from the input value.

### `pysnooper.variables.CommonVariable._keys` · *method*

## Summary:
Returns an empty tuple indicating that this variable type has no iterable keys for inspection.

## Description:
This method serves as a placeholder implementation for variables that do not support key-based iteration. It is called by `_safe_keys()` to retrieve keys for variable inspection in the pysnooper debugging tool. The base implementation returns an empty tuple, which signals that no additional keys exist for this variable type. Subclasses should override this method to provide appropriate key sequences for their specific variable types (e.g., dictionaries, lists, tuples).

## Args:
    main_value (Any): The variable value being inspected for key extraction. This parameter is not used in the base implementation but is passed for consistency with subclass implementations.

## Returns:
    tuple: An empty tuple, indicating no keys are available for iteration. This is the default behavior for variable types that don't support key-based access.

## Raises:
    None: This method does not raise exceptions directly. Any exceptions during key iteration are handled by the calling `_safe_keys()` method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - This method should only be called from within the `_safe_keys()` method
    - The `main_value` parameter should be a valid object that can be processed by the calling context

    Postconditions:
    - Always returns an empty tuple
    - Does not modify any instance state

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only returns a static empty tuple.

### `pysnooper.variables.CommonVariable._format_key` · *method*

## Summary:
Formats a key for display in variable inspection output by prepending a context-appropriate prefix.

## Description:
This abstract method is responsible for formatting keys when displaying variable contents. It is called by the `_items` method to create a properly formatted representation of keys in variable inspection output. The method must be implemented by subclasses to provide appropriate formatting based on the variable type being inspected.

## Args:
    key (Any): The key to be formatted, typically representing an attribute name, dictionary key, or index.

## Returns:
    str: A formatted key string that provides context-appropriate representation for display purposes.

## Raises:
    NotImplementedError: This method is abstract and must be implemented by subclasses.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: This method must be implemented by subclasses before being called.
    Postconditions: The returned string provides a context-appropriate formatted representation of the key.

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only performs string manipulation based on the key parameter.

### `pysnooper.variables.CommonVariable._get_value` · *method*

## Summary:
Extracts a value from a main value object using a specified key for variable inspection.

## Description:
This abstract method is responsible for retrieving a specific value from a main value object using a given key. It is called by the `_items` method during variable inspection to access nested values for display purposes. The method must be implemented by subclasses to handle different variable types appropriately.

## Args:
    main_value (Any): The main value object from which to extract a value (e.g., a dictionary, list, or object instance).
    key (Any): The key used to identify which specific value to extract from the main value (e.g., a dictionary key, list index, or attribute name).

## Returns:
    Any: The extracted value from the main_value using the provided key.

## Raises:
    NotImplementedError: This method is abstract and must be implemented by subclasses.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: This method must be implemented by subclasses before being called.
    Postconditions: The method should return the value associated with the key in the main_value, or raise an appropriate exception if the key is invalid.

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only accesses values within the main_value object.

## `pysnooper.variables.Attrs` · *class*

*No documentation generated.*

### `pysnooper.variables.Attrs._keys` · *method*

## Summary:
Returns an iterator over attribute names from an object's `__dict__` and `__slots__` attributes.

## Description:
Extracts attribute keys from the given object by combining its `__dict__` and `__slots__` attributes. This method is used by the pysnooper debugging tool to enumerate all accessible attributes of an object for inspection and display purposes. It's specifically designed for the `Attrs` class which handles regular object attribute inspection.

The method is called by `_safe_keys` in the parent `CommonVariable` class, which provides exception handling around the key extraction process. This separation allows the system to gracefully handle objects that may not have `__dict__` or `__slots__` attributes.

## Args:
    main_value (Any): The object whose attributes are to be enumerated. This can be any Python object that may have `__dict__` or `__slots__` attributes.

## Returns:
    Iterator[str]: An iterator over attribute names found in either the object's `__dict__` or `__slots__`. Returns an empty iterator if neither attribute exists or is inaccessible.

## Raises:
    None explicitly raised - exceptions are handled by the caller `_safe_keys` method.

## State Changes:
    Attributes READ: None - this method only reads from the input parameter
    Attributes WRITTEN: None - this method doesn't modify any instance attributes

## Constraints:
    Preconditions: 
    - `main_value` should be a valid Python object that can be inspected for attributes
    - The object should have either `__dict__` or `__slots__` attributes or both
    
    Postconditions:
    - The returned iterator will contain all attribute names from `__dict__` and `__slots__` if they exist
    - The method will not raise exceptions directly, though it may return empty iterators

## Side Effects:
    None - this method performs no I/O operations or external service calls. It only accesses object attributes.

### `pysnooper.variables.Attrs._format_key` · *method*

## Summary:
Formats a key by prepending a dot character to create attribute-style key representation.

## Description:
This method is responsible for formatting keys in attribute-based variable inspection. It prepends a dot ('.') to the provided key string to indicate that the key represents an attribute access pattern. This method is part of the CommonVariable hierarchy and is overridden in different subclasses to provide appropriate key formatting for their respective variable types.

## Args:
    key (str): The key to be formatted, typically representing an attribute name.

## Returns:
    str: A formatted key string with a leading dot character (e.g., ".attribute_name").

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The key parameter must be a string.
    Postconditions: The returned string will always have a leading dot followed by the original key content.

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only performs string manipulation.

### `pysnooper.variables.Attrs._get_value` · *method*

## Summary:
Retrieves an attribute value from an object using the getattr builtin function.

## Description:
This method implements the abstract `_get_value` interface defined in `CommonVariable` to extract attribute values from objects. It is used during variable inspection to access object attributes for debugging purposes. The method is called by `CommonVariable._items()` when processing attributes of objects to be inspected.

## Args:
    main_value (object): The object from which to retrieve the attribute
    key (str): The name of the attribute to retrieve

## Returns:
    Any: The value of the specified attribute from the main_value object

## Raises:
    AttributeError: When the specified key does not exist as an attribute on the main_value object

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - main_value must be an object that supports attribute access via getattr
    - key must be a string representing a valid attribute name on main_value
    
    Postconditions:
    - Returns the value of the attribute specified by key from main_value
    - Raises AttributeError if the attribute doesn't exist

## Side Effects:
    None

## `pysnooper.variables.Keys` · *class*

*No documentation generated.*

### `pysnooper.variables.Keys._keys` · *method*

*No documentation generated.*

### `pysnooper.variables.Keys._format_key` · *method*

## Summary:
Formats a dictionary or list key for display by wrapping it in square brackets with a shortened representation.

## Description:
Formats a key value for debugging output by creating a short representation of the key using `utils.get_shortish_repr` and wrapping it in square brackets. This method is part of the `Keys` class that handles inspection of dictionary-like objects in the pysnooper debugging library.

This method is called during the variable inspection process when displaying the contents of dictionary-like objects. It ensures that keys are displayed in a consistent, readable format that clearly distinguishes them from values in the debugging output.

## Args:
    key (Any): The key value to format, can be of any type that can be represented as a string

## Returns:
    str: A formatted string representation of the key wrapped in square brackets, e.g., "[key_value]"

## Raises:
    None explicitly raised - however, if the underlying `utils.get_shortish_repr` function encounters issues, it will return 'REPR FAILED'

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The key parameter must be a valid object that can be processed by `utils.get_shortish_repr`
    Postconditions: The returned string will always be in the format "[formatted_key]" where formatted_key is the result of `utils.get_shortish_repr(key)`

## Side Effects:
    None - this method is pure and has no side effects beyond the standard string formatting operations

### `pysnooper.variables.Keys._get_value` · *method*

*No documentation generated.*

## `pysnooper.variables.Indices` · *class*

*No documentation generated.*

### `pysnooper.variables.Indices._keys` · *method*

## Summary:
Returns a sliced range of indices for sequence-like objects based on the internal slice configuration.

## Description:
This method implements the `_keys` interface for the Indices class, which specializes in handling sequence-type variables (lists, tuples, strings, etc.). It generates a range of valid indices for the given main_value and applies the internal slice configuration (`self._slice`) to return only the desired subset of indices.

This method is called by the `_safe_keys` method in the parent CommonVariable class during variable inspection to safely iterate over valid indices of sequence variables. The Indices class is designed to work with indexed sequences, unlike the base Keys class which handles dictionary-like objects.

## Args:
    main_value (Sequence): A sequence-like object (list, tuple, string, etc.) whose indices are to be returned. Must support len() and indexing operations.

## Returns:
    range: A range object containing indices from the sequence, sliced according to self._slice. The range represents valid indices that can be used to access elements in main_value.

## Raises:
    TypeError: If main_value does not support len() operation or indexing.
    AttributeError: If main_value does not have a __len__ method.

## State Changes:
    Attributes READ: self._slice
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - main_value must be a sequence-like object that supports len() and indexing operations
    - main_value must be compatible with the slice configuration in self._slice
    
    Postconditions:
    - Returns a range object that can be iterated over to access valid indices
    - The returned range respects the slice configuration stored in self._slice
    - The range contains valid indices for accessing elements in main_value

## Side Effects:
    None

### `pysnooper.variables.Indices.__getitem__` · *method*

## Summary:
Creates a new Indices instance with an updated slice specification, enabling fluent slice chaining operations.

## Description:
Implements the slice indexing protocol for the Indices class, allowing users to create new instances with different slice specifications. This method enables fluent interface patterns where slice operations can be chained together. The method is called when using bracket notation with slice objects (e.g., `indices[1:5:2]`).

This logic is separated into its own method rather than being inlined because it implements the fundamental slicing behavior of the class, providing a clean way to create modified copies of Indices objects with new slice parameters. This approach supports immutable operations while maintaining the ability to build complex slicing expressions.

## Args:
    item (slice): A slice object specifying the index range to select. Must be a slice instance.

## Returns:
    Indices: A new Indices instance with the same properties as self but with the _slice attribute updated to the provided slice.

## Raises:
    AssertionError: When item is not an instance of slice type.

## State Changes:
    Attributes READ: 
    - self._slice: Used to determine the current slice specification
    Attributes WRITTEN:
    - result._slice: Set to the provided slice item in the returned copy

## Constraints:
    Preconditions:
    - item must be an instance of slice type
    - self must be a valid Indices instance
    
    Postconditions:
    - Returns a new Indices instance with identical properties except for _slice
    - The returned instance is independent of the original (deep copy)

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only creates and returns a new object instance.

## `pysnooper.variables.Exploding` · *class*

## Summary:
A variable inspection dispatcher that selects appropriate inspection classes based on the data type of the main value being inspected.

## Description:
The Exploding class serves as a type-dispatching mechanism for variable inspection within the pysnooper debugging library. When inspecting variables during debugging sessions, this class determines the most appropriate inspection strategy based on the type of the variable's value. It dynamically selects between specialized inspection classes (Keys, Indices, or Attrs) to handle different data structures appropriately.

This class is part of the variable inspection system that enables pysnooper to provide detailed information about variable contents during function execution tracing. It ensures that different data types (mappings, sequences, and objects) are inspected using type-appropriate methods.

## State:
- Inherits from BaseVariable, so has `source` (str) and `exclude` (tuple) attributes
- The `source` attribute contains the variable expression being inspected
- The `exclude` attribute contains a tuple of keys/attributes to exclude from inspection
- Uses the parent class's `code` property for evaluating the source expression

## Lifecycle:
- Creation: Instantiated with a source string and optional exclude tuple
- Usage: Called internally by BaseVariable.items() method during debugging trace processing
- Destruction: No special cleanup required, relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[BaseVariable.items()] --> B[Exploding._items()]
    B --> C{Type of main_value}
    C -->|Mapping| D[Keys._items()]
    C -->|Sequence| E[Indices._items()]
    C -->|Other| F[Attrs._items()]
    D --> G[Return items]
    E --> G
    F --> G
```

## Raises:
- No explicit exceptions raised by _items method itself
- Exceptions may be raised by the delegated classes (Keys, Indices, Attrs) during item extraction
- May raise exceptions during evaluation of the source expression in BaseVariable.items()

## Example:
```python
# Typically used internally by pysnooper
# When inspecting a dictionary:
exploding = Exploding("my_dict", exclude=())
# Would dispatch to Keys class for item extraction

# When inspecting a list:
exploding = Exploding("my_list", exclude=())  
# Would dispatch to Indices class for item extraction

# When inspecting an object:
exploding = Exploding("my_obj", exclude=())
# Would dispatch to Attrs class for item extraction
```

### `pysnooper.variables.Exploding._items` · *method*

## Summary:
Determines the appropriate variable inspection class based on the type of main_value and delegates to that class for extracting variable items.

## Description:
This method acts as a factory dispatcher that selects the appropriate variable inspection class (Keys, Indices, or Attrs) based on the type of the main_value parameter. It then delegates the actual item extraction to the selected class's _items method. This approach allows for type-specific handling of different container types during variable inspection.

The method is called internally by the BaseVariable.items() method during the debugging tracing process when inspecting variables. It enables polymorphic behavior for different data structures while maintaining a clean separation of concerns between type detection and item extraction logic.

## Args:
    main_value: The value of the variable being inspected, which can be a Mapping, Sequence, or other object type
    normalize (bool): Flag indicating whether to normalize the extracted items for consistent representation (default: False)

## Returns:
    tuple: A tuple containing the items extracted from the main_value, formatted according to the selected inspection class's logic

## Raises:
    None: This method delegates to other classes' methods which may raise exceptions, but this method itself does not raise exceptions

## State Changes:
    Attributes READ: 
    - self.source: The original source code string of the variable being inspected
    - self.exclude: The tuple of excluded variable names
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The main_value parameter should be a valid Python object that can be inspected
    - The self.source and self.exclude attributes must be properly initialized
    
    Postconditions:
    - Returns a tuple of formatted items representing the variable's contents
    - The returned tuple follows the expected format for debugging output

## Side Effects:
    I/O: None
    External service calls: None
    Mutations to objects outside self: None

