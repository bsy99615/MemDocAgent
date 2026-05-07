# `bundling.py`

## `src.exodus_bundler.bundling.bytes_to_int` · *function*

*No documentation generated.*

## `src.exodus_bundler.bundling.create_bundle` · *function*

*No documentation generated.*

## `src.exodus_bundler.bundling.create_unpackaged_bundle` · *function*

*No documentation generated.*

## `src.exodus_bundler.bundling.detect_elf_binary` · *function*

*No documentation generated.*

## `src.exodus_bundler.bundling.parse_dependencies_from_ldd_output` · *function*

*No documentation generated.*

## `src.exodus_bundler.bundling.resolve_binary` · *function*

*No documentation generated.*

## `src.exodus_bundler.bundling.resolve_file_path` · *function*

*No documentation generated.*

## `src.exodus_bundler.bundling.run_ldd` · *function*

*No documentation generated.*

## `src.exodus_bundler.bundling.stored_property` · *class*

*No documentation generated.*

### `src.exodus_bundler.bundling.stored_property.__init__` · *method*

## Summary:
Initializes a stored_property descriptor with a function to be cached.

## Description:
Constructs a stored_property descriptor that will cache the result of calling the provided function on an instance. This enables lazy evaluation and caching of computed properties.

## Args:
    function (callable): The function to be stored and executed when the property is accessed. This function should accept 'self' as its first argument and return a cached value.

## Returns:
    None: This method initializes the descriptor instance and does not return a value.

## Raises:
    None: This method does not raise any exceptions under normal circumstances.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.__doc__: Set to the docstring of the provided function
    - self.function: Set to the provided function object

## Constraints:
    Preconditions:
    - The function parameter must be callable
    - The function should accept an instance as its first argument (following descriptor protocol)
    
    Postconditions:
    - The descriptor instance will have its __doc__ attribute set to the function's docstring
    - The descriptor instance will store the function for later execution

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `src.exodus_bundler.bundling.stored_property.__get__` · *method*

*No documentation generated.*

## `src.exodus_bundler.bundling.Elf` · *class*

*No documentation generated.*

### `src.exodus_bundler.bundling.Elf.__init__` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.Elf.__eq__` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.Elf.__hash__` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.Elf.__repr__` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.Elf.find_direct_dependencies` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.Elf.dependencies` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.Elf.direct_dependencies` · *method*

*No documentation generated.*

## `src.exodus_bundler.bundling.File` · *class*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.__init__` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.__eq__` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.__hash__` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.__repr__` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.copy` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.create_entry_point` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.create_launcher` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.symlink` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.destination` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.executable` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.elf` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.hash` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.requires_launcher` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.source` · *method*

*No documentation generated.*

## `src.exodus_bundler.bundling.Bundle` · *class*

*No documentation generated.*

### `src.exodus_bundler.bundling.Bundle.__init__` · *method*

## Summary:
Initializes a Bundle instance with working directory, chroot configuration, and empty file collections.

## Description:
This constructor method sets up the initial state of a Bundle object. It handles the creation of a temporary working directory when requested, and initializes empty collections for tracking files and linker files that will be bundled. This method is responsible for setting up the basic infrastructure needed for bundling operations.

## Args:
    working_directory (str or bool, optional): Path to the working directory or True to create a temporary one. Defaults to None.
    chroot (str, optional): Path to the chroot environment. Defaults to None.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: working_directory parameter
    Attributes WRITTEN: 
    - self.working_directory: Set to the provided value or a temporary directory
    - self.chroot: Set to the provided value
    - self.files: Initialized as an empty set
    - self.linker_files: Initialized as an empty set

## Constraints:
    Preconditions:
    - working_directory can be None, a string path, or True
    - chroot can be None or a string path
    
    Postconditions:
    - self.working_directory is either None, a provided path, or a temporary directory
    - self.chroot is either None or the provided path
    - self.files is initialized as an empty set
    - self.linker_files is initialized as an empty set

## Side Effects:
    - Creates a temporary directory with specific permissions when working_directory=True
    - Sets file permissions on the temporary directory using umask manipulation

### `src.exodus_bundler.bundling.Bundle.add_file` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.Bundle.create_bundle` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.Bundle.delete_working_directory` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.Bundle.file_factory` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.Bundle.bundle_root` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.Bundle.hash` · *method*

*No documentation generated.*

