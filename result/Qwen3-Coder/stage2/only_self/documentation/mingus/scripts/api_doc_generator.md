# `api_doc_generator.py`

## `scripts.api_doc_generator._is_class` · *function*

## Summary:
Filters objects to determine if they qualify as classes suitable for API documentation inclusion.

## Description:
This utility function serves as a classifier for determining whether a given object should be included in API documentation. It implements a two-part test: first verifying that the object is a legitimate class (by checking it's a subclass of object), and second ensuring it's not an excluded superclass type. This filtering mechanism helps exclude internal implementation details, abstract base classes, or other non-public constructs from appearing in generated documentation.

## Args:
    cls (type): The object to evaluate, expected to be a class or type.

## Returns:
    bool: True if the object is a class that should be documented (is subclass of object but not in _SKIPPED_CLASS_SUPERTYPES), False otherwise.

## Raises:
    None explicitly raised by this function, though invalid inputs may cause implicit TypeError.

## Constraints:
    Preconditions:
    - cls must be a valid Python class or type object
    - _SKIPPED_CLASS_SUPERTYPES must be defined in the module scope
    
    Postconditions:
    - Returns a boolean indicating whether the class should be included in documentation

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input cls] --> B{issubclass(cls, object)?}
    B -- Yes --> C{issubclass(cls, _SKIPPED_CLASS_SUPERTYPES)?}
    C -- No --> D[Return True]
    C -- Yes --> E[Return False]
    B -- No --> F[Return False]
```

## Examples:
    # Basic usage
    >>> _is_class(str)
    True
    >>> _is_class(int)
    True
    >>> _is_class(type)
    True
```

## `scripts.api_doc_generator._is_method` · *function*

## Summary:
Identifies whether an object is classified as a method type for API documentation generation purposes.

## Description:
This utility function determines if a given object is considered a method within the context of API documentation generation. It serves as a type classifier that checks if an object's type belongs to a predefined collection of method types (`_METHOD_TYPES`). This function is used during API documentation processing to distinguish between method objects and other types of attributes or functions.

The function abstracts away the specific type checking logic by relying on the global constant `_METHOD_TYPES`, which contains the set of Python types that are considered methods in this codebase's context.

## Args:
    obj (Any): The object to be checked for method type classification.

## Returns:
    bool: True if the object's type is contained within the `_METHOD_TYPES` collection, indicating it's classified as a method; False otherwise.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - The object being tested must be a valid Python object
    - The global variable `_METHOD_TYPES` must be properly initialized and contain appropriate type definitions
    
    Postconditions:
    - The function returns a boolean value indicating method type classification
    - No modifications are made to the input object or global state

## Side Effects:
    None - This function performs only type checking operations without any I/O or state mutations.

## Control Flow:
```mermaid
flowchart TD
    A[Start _is_method] --> B{type(obj) in _METHOD_TYPES?}
    B -- Yes --> C[Return True]
    B -- No --> D[Return False]
```

## Examples:
    # Example usage in API documentation generator
    method_obj = some_class.some_method
    if _is_method(method_obj):
        # Process as method for documentation
        # This would typically involve extracting method signature, docstring, etc.
        pass
        
    # Non-method object
    regular_var = "hello"
    if not _is_method(regular_var):
        # Handle as regular attribute or function
        pass
```

## `scripts.api_doc_generator.Documize` · *class*

## Summary:
A class for recursively generating reStructuredText API documentation for Python modules.

## Description:
The Documize class provides functionality to automatically generate comprehensive API documentation for Python modules in reStructuredText format. It recursively analyzes modules, classes, functions, and attributes, producing structured documentation suitable for wiki-style documentation systems. The class leverages Python's introspection capabilities to extract module contents and their associated metadata.

This class is particularly useful for generating automated documentation for libraries like mingus, where it can traverse module hierarchies and produce detailed documentation including function signatures, docstrings, and attribute information. It handles both top-level module elements and nested class contents through recursive processing.

The documentation generation process filters out private attributes (those starting with underscore) while preserving certain special methods defined in _ALLOWED_DUNDER_METHODS. It distinguishes between callable objects (functions/methods) and non-callable attributes, generating appropriate documentation directives for each type.

## State:
- functions: list[str] - Stores generated documentation strings for callable objects (functions/methods)
- classes: list[str] - Stores generated documentation strings for class definitions and their contents  
- attributes: list[str] - Stores generated documentation strings for non-callable attributes
- module_string: str - The string representation of the currently processed module
- module: object - The actual module object being processed
- _ALLOWED_DUNDER_METHODS: set[str] - Set of special methods that should be included in documentation despite starting with double underscores

## Lifecycle:
Creation: Instantiate with optional module_string parameter to specify which module to document. The module is loaded immediately upon instantiation via set_module().
Usage: Call output_wiki() method to generate complete documentation for the specified module. This triggers a complete recursive analysis of all elements in the module hierarchy.
Destruction: No explicit cleanup required; class state is reset between operations via the reset() method.

## Method Map:
```mermaid
flowchart TD
    A[Documize.__init__] --> B[set_module]
    B --> C[output_wiki]
    C --> D[generate_module_wikidocs]
    D --> E[process_element_recursively]
    E --> F{_filter_dunder_attributes}
    F --> G{callable?}
    G -- No --> H[generate_non_callable_docs]
    G -- Yes --> I[generate_callable_wikidocs]
    I --> J{_is_method?}
    J -- Yes --> K[generate_function_wikidocs]
    J -- No --> L{_is_class?}
    L -- Yes --> M[process_element_recursively]
    L -- No --> N[hasattr(__module__)?]
    N -- Yes --> M
    N -- No --> O[End]
```

## Raises:
- NameError: May be raised by eval() in set_module() if module_string refers to a non-existent module
- AttributeError: May be raised by various introspection operations if objects lack expected attributes
- Exception: May be raised by inspect.getargspec() or other introspection functions in edge cases

## Example:
```python
# Create documentation generator for a module
doc_gen = Documize('mingus.containers')

# Generate documentation
wiki_output = doc_gen.output_wiki()

# The result contains reStructuredText formatted documentation
print(wiki_output)
```

### `scripts.api_doc_generator.Documize.__init__` · *method*

## Summary:
Initializes the Documize object and configures it to document the specified Python module.

## Description:
The `__init__` method serves as the constructor for the Documize class. It initializes the object with an optional module string and delegates the module setting to the `set_module` method. This method is called during object instantiation to prepare the documentation generator for processing a specific Python module.

## Args:
    module_string (str): The string representation of the Python module to document. Defaults to an empty string.

## Returns:
    None: This method does not return a value.

## Raises:
    None explicitly raised: The method itself doesn't raise exceptions, though underlying operations in `set_module` might.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.module_string: Set to the provided module_string parameter
    - self.module: Set to the evaluated module object from module_string
    - self.functions: Reset to empty list (via reset() call)
    - self.classes: Reset to empty list (via reset() call)  
    - self.attributes: Reset to empty list (via reset() call)

## Constraints:
    Preconditions: 
    - The module_string should be a valid Python module identifier that can be evaluated
    - If module_string is not provided, the object will be initialized with an empty string
    
    Postconditions:
    - The object's module_string attribute will be set to the provided value
    - The object's module attribute will be set to the evaluated module
    - The object's functions, classes, and attributes lists will be reset to empty lists

## Side Effects:
    None: This method doesn't perform I/O operations or mutate external objects. However, it indirectly causes side effects through the `set_module` method which evaluates the module string and resets internal tracking lists.

### `scripts.api_doc_generator.Documize._filter_dunder_attributes` · *method*

*No documentation generated.*

### `scripts.api_doc_generator.Documize.process_element_recursively` · *method*

## Summary:
Recursively processes attributes of Python objects, generating documentation for callable and non-callable elements.

## Description:
Traverses the attributes of a given Python object and generates appropriate documentation for each attribute based on whether it is callable or not. This method serves as the core recursive processor in the API documentation generator, systematically examining all non-private attributes of an object and delegating documentation generation to specialized methods.

The method is invoked during the module documentation generation pipeline when processing the contents of modules, classes, or other objects. It filters out private attributes (those starting with underscore) while preserving special dunder methods defined in `_ALLOWED_DUNDER_METHODS`. For each attribute, it determines if it's callable and routes it to either `generate_non_callable_docs` or `generate_callable_wikidocs` for appropriate documentation formatting.

## Args:
    element_string (str): The dotted string representation of the object's module path
    element_evaled (Any): The actual Python object whose attributes are being processed
    is_class (bool, optional): Flag indicating if the parent context is a class. Defaults to False

## Returns:
    None: This method doesn't return a value but modifies instance attributes through delegated calls

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ:
    - self._filter_dunder_attributes: Called to filter attributes
    - self.generate_non_callable_docs: Called for non-callable elements
    - self.generate_callable_wikidocs: Called for callable elements
    
    Attributes WRITTEN:
    - Through delegated calls to generate_non_callable_docs and generate_callable_wikidocs, which modify:
      - self.attributes (when is_class=False)
      - self.classes (when is_class=True)
      - self.functions (when is_class=False)

## Constraints:
    Preconditions:
    - The `element_string` parameter must be a valid dotted module path string
    - The `element_evaled` parameter must be a valid Python object that can be inspected with `dir()`
    - The `element_evaled` object must support attribute access via `eval()` operations
    - The `_filter_dunder_attributes` method must properly filter attributes
    
    Postconditions:
    - All non-private attributes of `element_evaled` are processed
    - Non-callable attributes are documented via `generate_non_callable_docs`
    - Callable attributes are documented via `generate_callable_wikidocs`
    - The recursive processing continues for class objects through `generate_callable_wikidocs`

## Side Effects:
    - Uses `eval()` to access nested object attributes, which may pose security risks
    - Mutates instance state through delegated method calls
    - May trigger recursive calls to itself when processing class objects

### `scripts.api_doc_generator.Documize.generate_module_wikidocs` · *method*

## Summary:
Generates complete wiki-formatted documentation for a Python module including header, docstring, and all contained elements.

## Description:
This method serves as the main entry point for generating documentation for a Python module in wiki format. It orchestrates the entire documentation generation process by resetting internal state, creating proper module header formatting, processing all module elements recursively, sorting and organizing the results, and returning a complete formatted documentation string.

The method is called during the documentation generation pipeline when a complete module documentation page needs to be created. It leverages the recursive processing capabilities of the Documize class to discover and document all classes, functions, and attributes within the target module.

## Args:
    None - This is a method that operates on the instance state

## Returns:
    str: A formatted documentation string containing the complete module documentation with header, module docstring, classes, attributes, and functions in proper order

## Raises:
    None explicitly raised - However, underlying operations may raise exceptions from:
    - eval() calls in process_element_recursively
    - inspect.getargspec() operations
    - File I/O operations if the module loading fails

## State Changes:
    Attributes READ: 
    - self.module_string: Used for module identification and header creation
    - self.module: Used to access module docstring
    - self.classes: Used to append class documentation
    - self.attributes: Used to append attribute documentation  
    - self.functions: Used to append function documentation
    
    Attributes WRITTEN:
    - self.functions: Sorted and populated with function documentation
    - self.attributes: Sorted and populated with attribute documentation
    - self.classes: Populated with class documentation

## Constraints:
    Preconditions:
    - self.module_string must be properly set via set_module() method
    - self.module must be a valid Python module object
    - All internal lists (functions, classes, attributes) should be accessible
    
    Postconditions:
    - Internal state is reset before processing
    - All discovered elements are sorted alphabetically
    - Returned string follows proper wiki documentation format
    - Module header is properly formatted with underline

## Side Effects:
    None - This method is primarily a pure transformation function that doesn't cause external I/O or mutate external state beyond its own instance variables.

### `scripts.api_doc_generator.Documize.generate_non_callable_docs` · *method*

## Summary:
Formats and stores documentation for non-callable data attributes and constants from Python modules.

## Description:
Processes non-callable elements (such as data attributes, constants, and other non-function objects) from Python modules and generates reStructuredText documentation format for inclusion in API documentation. This method is specifically designed to handle data elements that are not functions or methods, ensuring they are properly documented with their types and values.

The method is invoked by `process_element_recursively` during the documentation generation pipeline when it encounters non-callable objects. It filters out private attributes (those beginning with underscore) and module objects, then formats the remaining elements into standardized documentation blocks that can be included in larger documentation files.

## Args:
    module_string (str): The dotted string representation of the module path where the element resides
    element_string (str): The name of the data attribute or constant being documented
    evaled (Any): The actual data value or object being documented
    is_class (bool, optional): Flag indicating if the parent context is a class. Defaults to False

## Returns:
    None: This method doesn't return a value but modifies instance attributes

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: 
    - None - This method only reads the input parameters and instance state for storage
    
    Attributes WRITTEN:
    - self.attributes: Appended with formatted documentation when is_class=False
    - self.classes: Appended with formatted documentation when is_class=True

## Constraints:
    Preconditions:
    - The `element_string` parameter must be a valid string identifier
    - The `evaled` parameter must be a valid Python object that is not a module type
    - The `element_string` must not start with underscore ('_') to avoid documenting private attributes
    - The `type(evaled)` must be a valid Python type object
    
    Postconditions:
    - The formatted documentation string is appended to either self.attributes or self.classes
    - The documentation follows reStructuredText format with proper directives
    - Private attributes (starting with '_') are filtered out and not documented
    - Module types are filtered out and not documented

## Side Effects:
    - Mutates instance state by appending formatted documentation strings to self.attributes or self.classes
    - Uses string manipulation and type introspection to format documentation
    - Relies on eval() indirectly through process_element_recursively for element access

### `scripts.api_doc_generator.Documize.generate_callable_wikidocs` · *method*

## Summary:
Processes callable objects (methods, classes, or other callables) and generates appropriate reStructuredText documentation for API documentation generation.

## Description:
This method serves as a dispatcher for handling different types of callable objects during API documentation generation. It determines the nature of the provided callable object and routes it to the appropriate documentation generation method. The method is part of the recursive documentation processing pipeline that traverses modules and their members to build comprehensive API documentation.

When called from `process_element_recursively`, this method analyzes the type of the callable object and decides how to document it:
1. If it's a method, it generates function documentation and appends to appropriate collection
2. If it's a class, it adds class directive and initiates recursive processing
3. If it's another callable with matching module, it treats it as a class and processes recursively

## Args:
    module_string (str): The dotted string representation of the module path where the element resides
    element_string (str): The name of the element being processed  
    evaled (Any): The actual object being documented
    is_class (bool, optional): Flag indicating if the parent context is a class. Defaults to False

## Returns:
    None: This method doesn't return a value but modifies instance attributes

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: 
    - self.functions (when appending method documentation)
    - self.classes (when appending class documentation)
    - self.module_string (used for constructing module paths)
    
    Attributes WRITTEN:
    - self.functions (appended with method documentation when is_class=False)
    - self.classes (appended with class documentation or method documentation when is_class=True)
    - When processing classes, recursively calls self.process_element_recursively

## Constraints:
    Preconditions:
    - The `evaled` parameter must be a valid Python object
    - The `module_string` parameter must be a valid dotted module path
    - The `_is_method` helper function must properly identify method objects
    - The `_is_class` helper function must properly identify class objects
    - The `generate_function_wikidocs` and `process_element_recursively` methods must be implemented
    
    Postconditions:
    - The appropriate documentation is appended to either self.functions or self.classes
    - For class objects, recursive processing continues via `process_element_recursively`
    - The method handles three distinct logical branches based on the type and properties of the evaled object

## Side Effects:
    - Appends documentation strings to self.functions or self.classes lists
    - May invoke recursive processing through `process_element_recursively`
    - Uses eval() internally to access nested module attributes (security consideration)

### `scripts.api_doc_generator.Documize.generate_function_wikidocs` · *method*

## Summary:
Generates Sphinx-style reStructuredText documentation for Python functions or methods, including parameter signatures and formatted docstrings.

## Description:
This method creates reStructuredText documentation directives for Python functions or methods, suitable for inclusion in Sphinx documentation. It handles function signatures with default parameter values and properly formats docstrings for better readability in documentation output. The method is designed to be part of a documentation generation system that converts Python code into documentation format.

## Args:
    func_string (str): The fully qualified name of the function or method (e.g., 'module.Class.method' or 'module.function')
    func (callable): The actual Python function or method object being documented
    is_class (bool): Flag indicating whether the documentation is for a class method (True) or regular function (False). Defaults to False

## Returns:
    str: A formatted reStructuredText string containing the documentation directive for the function or method

## Raises:
    None explicitly raised - though internal exceptions during argument processing may occur

## State Changes:
    Attributes READ: None - this method only reads parameters and does not modify instance state
    Attributes WRITTEN: None - this method does not modify instance state

## Constraints:
    Preconditions:
    - func_string must be a valid string representing the function's qualified name
    - func must be a callable Python object (function, method, etc.)
    - is_class must be a boolean value
    
    Postconditions:
    - Returns a properly formatted reStructuredText string
    - The returned string follows Sphinx documentation conventions
    - Function signature includes all parameters with appropriate default values
    - Docstring is cleaned and formatted with proper indentation

## Side Effects:
    None - this method is pure and does not perform I/O operations or mutate external state

### `scripts.api_doc_generator.Documize.reset` · *method*

## Summary:
Resets the internal tracking lists for functions, classes, and attributes to empty lists.

## Description:
This method clears all previously collected documentation elements by resetting the internal tracking lists. It is called at the beginning of the documentation generation process to ensure a clean slate for collecting new documentation elements.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.functions: Reset to empty list
    - self.classes: Reset to empty list  
    - self.attributes: Reset to empty list

## Constraints:
    Preconditions: None
    Postconditions: All three tracking lists (functions, classes, attributes) are empty lists

## Side Effects:
    None

### `scripts.api_doc_generator.Documize.set_module` · *method*

## Summary:
Sets the target Python module for documentation generation by evaluating the module string and resetting internal tracking lists.

## Description:
Configures the Documize instance to document a specific Python module by evaluating the provided module string and updating internal state. This method is called during object initialization and can be used later to switch documentation targets. The method evaluates the module string using Python's eval() function, stores both the string representation and the actual module object, and resets all internal tracking lists to prepare for new documentation collection.

This method serves as a central configuration point for the documentation generator, ensuring that all subsequent documentation processing operates on the correct module. It's designed to be called internally by the constructor and potentially by external code that wants to change the documentation target.

## Args:
    module_string (str): The string representation of a Python module to document. Must be a valid module identifier that can be evaluated with Python's eval() function.

## Returns:
    None: This method does not return any value.

## Raises:
    NameError: Raised when the module_string cannot be evaluated due to undefined names or invalid module identifiers.
    SyntaxError: Raised when the module_string contains invalid Python syntax.
    AttributeError: Raised when the evaluated module object doesn't exist or is inaccessible.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.module_string: Set to the provided module_string parameter
    - self.module: Set to the evaluated module object from module_string
    - self.functions: Reset to empty list (via reset() call)
    - self.classes: Reset to empty list (via reset() call)
    - self.attributes: Reset to empty list (via reset() call)

## Constraints:
    Preconditions:
    - The module_string must be a valid Python module identifier that can be successfully evaluated
    - If module_string is an empty string, no changes are made to the instance state
    
    Postconditions:
    - If module_string is not empty, the instance's module_string and module attributes are updated
    - All internal tracking lists (functions, classes, attributes) are reset to empty lists
    - The instance is ready to collect documentation for the newly specified module

## Side Effects:
    Indirect side effects through eval() call which may execute arbitrary code from the module string
    Calls to self.reset() which clears all previously collected documentation elements

### `scripts.api_doc_generator.Documize.output_wiki` · *method*

## Summary:
Delegates to the internal module wikidocs generator to produce wiki-formatted documentation.

## Description:
This method acts as a facade that forwards the documentation generation request to the internal `generate_module_wikidocs()` method. It provides a standardized interface for retrieving wiki documentation for the module being processed.

## Args:
    None

## Returns:
    The output from `generate_module_wikidocs()`, which contains the generated wiki documentation content.

## Raises:
    Exceptions that may be raised by the `generate_module_wikidocs()` method during execution.

## State Changes:
    Attributes READ: None explicitly accessed
    Attributes WRITTEN: None modified

## Constraints:
    Preconditions: The instance must have a valid `generate_module_wikidocs` method implemented.
    Postconditions: Returns documentation content suitable for wiki presentation.

## Side Effects:
    Depends on the implementation of `generate_module_wikidocs()`, which may involve file I/O, string processing, or other operations.

## `scripts.api_doc_generator.generate_package_wikidocs` · *function*

## Summary:
Generates wiki-formatted documentation files for all attributes of a specified Python package, with flawed filtering logic.

## Description:
Creates individual wiki documentation files for each attribute found in a given Python package. The function takes a package string, evaluates it to obtain the actual package object, and then iterates through all attributes of that package using Python's `dir()` function. For each attribute (excluding those starting with double underscores), it generates wiki documentation and writes it to a file in the specified directory.

This function was extracted to separate the documentation generation logic from the main program flow, allowing for reusable documentation generation across different packages. However, it contains a critical logical error in its filtering mechanism.

## Args:
    package_string (str): String representation of the Python package to document (e.g., 'mingus.containers'). This is evaluated to obtain the actual package object.
    file_prefix (str): Prefix to use for generated wiki filenames. Defaults to 'ref'.
    file_suffix (str): Suffix to use for generated wiki filenames. Defaults to '.wiki'.

## Returns:
    None: This function does not return any value.

## Raises:
    NameError: Raised when package_string cannot be evaluated due to undefined names or invalid module identifiers.
    AttributeError: Raised when accessing attributes of the package fails.
    Exception: Various exceptions may occur during file I/O operations or documentation generation.

## Constraints:
    Preconditions:
    - package_string must be a valid Python module identifier that can be evaluated
    - sys.argv[1] must contain a valid directory path for writing output files
    - The package specified by package_string must exist and be importable
    
    Postconditions:
    - Wiki documentation files are created in the directory specified by sys.argv[1]
    - Each file contains wiki-formatted documentation for an attribute of the package

## Side Effects:
    - Creates files in the directory specified by sys.argv[1]
    - Writes wiki-formatted documentation content to these files
    - Uses eval() to dynamically evaluate package strings (security risk)
    - Prints status messages to standard output during execution

## Control Flow:
```mermaid
flowchart TD
    A[Start generate_package_wikidocs] --> B[Create Documize instance]
    B --> C[Evaluate package_string to get package object]
    C --> D[Print documentation generation message]
    D --> E[Iterate through package attributes using dir()]
    E --> F{Element is callable?}
    F -- Yes --> G[Skip callable element (LOGICAL ERROR)]
    F -- No --> H{Element starts with '__'?}
    H -- Yes --> I[Skip private element]
    H -- No --> J[Build full element name]
    J --> K[Set Documize module to full element name]
    K --> L[Generate wiki filename]
    L --> M[Generate wiki documentation]
    M --> N[Try to open output file]
    N --> O{File opened successfully?}
    O -- No --> P[Print file opening error]
    O -- Yes --> Q[Write documentation to file]
    Q --> R{Write successful?}
    R -- No --> S[Print write error]
    R -- Yes --> T[Print OK status]
    T --> U[Continue to next element]
    P --> U
    S --> U
    G --> U
    I --> U
```

## Examples:
```python
# Generate documentation for mingus.containers package
generate_package_wikidocs('mingus.containers')

# Generate documentation with custom file naming
generate_package_wikidocs('mingus.core', file_prefix='api_', file_suffix='.md')
```

## Critical Implementation Issues:
1. **Logical Error**: The function incorrectly uses `callable(element)` where `element` is a string returned by `dir()`. Since strings are not callable, this condition always evaluates to False, causing ALL attributes to be processed regardless of whether they are callable or not.

2. **Security Risk**: Uses `eval()` to evaluate package strings, which can execute arbitrary code and poses serious security vulnerabilities.

3. **Inefficient Processing**: For each attribute, it performs redundant evaluations (`eval(fullname)` twice) and creates unnecessary intermediate variables.

4. **Poor Error Handling**: Generic exception handling prevents proper debugging of specific issues.

## `scripts.api_doc_generator.main` · *function*

## Summary:
Entry point for generating API documentation for mingus library packages.

## Description:
The main function serves as the command-line interface for the mingus API documentation generator. It prints version information, validates command-line arguments, and orchestrates the generation of documentation files for core mingus packages. This function was extracted to separate the argument validation and orchestration logic from the actual documentation generation process, making the code more modular and maintainable.

## Args:
    None: This function does not accept any explicit parameters.

## Returns:
    None: This function does not return any value.

## Raises:
    SystemExit: Exits with code 1 when no command-line argument is provided or when the provided argument is not a valid directory.

## Constraints:
    Preconditions:
    - Must be called from command line with exactly one argument (output directory path)
    - The output directory path must be a valid existing directory
    - The mingus library must be properly installed and importable
    
    Postconditions:
    - Documentation files are generated for mingus.core, mingus.midi, mingus.containers, and mingus.extra packages
    - Files are written to the specified output directory
    - Version information is printed to standard output

## Side Effects:
    - Prints version information and usage instructions to standard output
    - Exits the program with error code 1 if validation fails
    - Creates multiple documentation files in the specified output directory
    - Calls generate_package_wikidocs function multiple times

## Control Flow:
```mermaid
flowchart TD
    A[Start main function] --> B[Print version info]
    B --> C[Check if sys.argv length equals 1]
    C --> D{No arguments provided?}
    D -- Yes --> E[Print usage instructions]
    E --> F[Exit with code 1]
    D -- No --> G[Check if sys.argv[1] is valid directory]
    G --> H{Invalid directory?}
    H -- Yes --> I[Print error message]
    I --> J[Exit with code 1]
    H -- No --> K[Call generate_package_wikidocs for mingus.core]
    K --> L[Call generate_package_wikidocs for mingus.midi]
    L --> M[Call generate_package_wikidocs for mingus.containers]
    M --> N[Call generate_package_wikidocs for mingus.extra]
    N --> O[End]
```

## Examples:
```bash
# Generate documentation in the current directory
python api_doc_generator.py /tmp/docs

# This will generate documentation files for:
# - mingus.core
# - mingus.midi  
# - mingus.containers
# - mingus.extra
```

