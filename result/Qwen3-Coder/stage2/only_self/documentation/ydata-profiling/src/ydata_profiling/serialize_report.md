# `serialize_report.py`

## `src.ydata_profiling.serialize_report.SerializeReport` · *class*

## Summary:
Serializes and deserializes ProfileReport objects for persistent storage and loading.

## Description:
The SerializeReport class provides functionality to serialize ProfileReport objects into binary format for persistent storage and deserialize them back into memory. It handles the serialization of key components like DataFrame hash, configuration, description set, and report structure. This class acts as a bridge for saving and loading profiling results to/from disk, ensuring compatibility between different versions and preventing data corruption during transfer.

## State:
- df: Class attribute representing the DataFrame being profiled (currently None)
- config: Class attribute storing the Settings configuration object (currently None)
- _df_hash: Private attribute storing the DataFrame hash for validation (initially None)
- _report: Private attribute storing the report structure (Root object, initially None)
- _description_set: Private attribute storing the description set (BaseDescription object, initially None)

## Lifecycle:
- Creation: Instantiated without arguments; relies on external assignment of df, config, etc.
- Usage: Typically used by calling dump() to serialize to file or dumps() to serialize to bytes, followed by load() or loads() to deserialize
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[SerializeReport] --> B[dump()]
    A --> C[dumps()]
    A --> D[load()]
    A --> E[loads()]
    B --> F[File I/O]
    C --> G[Pickle serialization]
    D --> H[File I/O]
    E --> I[Pickle deserialization]
    F --> J[Write .pp file]
    G --> K[Serialize to bytes]
    H --> L[Read .pp file]
    I --> M[Deserialize from bytes]
```

## Raises:
- ValueError: When data fails to load due to corruption or version incompatibility
- ValueError: When DataFrame hash doesn't match during deserialization
- Exception: From pickle.loads() when deserialization fails

## Example:
```python
# Create a serializer instance
serializer = SerializeReport()

# Set up the report data (typically done by ProfileReport)
serializer.df = my_dataframe
serializer.config = settings
serializer._description_set = description_set
serializer._report = report_root

# Serialize to file
serializer.dump("my_report.pp")

# Load from file
serializer.load("my_report.pp")

# Or serialize to bytes
serialized_data = serializer.dumps()

# Deserialize from bytes
serializer.loads(serialized_data)
```

### `src.ydata_profiling.serialize_report.SerializeReport.df_hash` · *method*

## Summary:
Returns the cached hash of the DataFrame for serialization compatibility checking, or None if not yet computed.

## Description:
This property provides access to the hash of the DataFrame associated with this serializer. The hash is computed lazily upon first access and cached in the `_df_hash` attribute for subsequent accesses. When a DataFrame is present, this hash enables verification that the DataFrame has not changed between serialization and deserialization operations.

In the current implementation, this property returns None, indicating that the hash has not yet been computed. A complete implementation would compute and cache a hash of the DataFrame for comparison purposes.

## Args:
    None

## Returns:
    Optional[str]: The cached hash of the DataFrame if already computed, otherwise None.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.df, self._df_hash
    Attributes WRITTEN: self._df_hash (when first computed)

## Constraints:
    Preconditions: The instance should have a DataFrame assigned to self.df
    Postconditions: The hash is cached in self._df_hash for subsequent calls

## Side Effects:
    None

### `src.ydata_profiling.serialize_report.SerializeReport.dumps` · *method*

## Summary:
Serializes the core profiling report components into a pickled byte stream for storage or transmission.

## Description:
Converts the essential profiling report data (hash, configuration, description set, and report) into a compact binary representation using Python's pickle module. This method enables persistence of profiling results by creating a serialized snapshot that can be stored to disk or transmitted over networks.

This method is separated from inline serialization logic to provide a clean, reusable interface for serialization operations and to maintain consistency with the complementary `loads` method that handles deserialization.

## Args:
    None

## Returns:
    bytes: A pickled byte stream containing the serialized profiling report components in the order: [df_hash, config, _description_set, _report]

## Raises:
    None explicitly raised, though pickle.dumps may raise PicklingError or other serialization-related exceptions indirectly

## State Changes:
    - Attributes READ: self.df_hash, self.config, self._description_set, self._report

## Constraints:
    - Preconditions: All referenced attributes (df_hash, config, _description_set, _report) must be accessible and serializable
    - Postconditions: The returned bytes represent a complete serialization of the current profiling report state

## Side Effects:
    - Uses pickle module for serialization
    - Creates a potentially large byte array in memory

### `src.ydata_profiling.serialize_report.SerializeReport.loads` · *method*

## Summary:
Deserializes and loads profile report data from bytes into the current instance, validating compatibility and handling version mismatches.

## Description:
Loads serialized profile report data into the current SerializeReport instance. This method deserializes data using pickle and validates that the loaded data is compatible with the current instance. It handles cases where existing data might conflict with loaded data by issuing warnings and preserving existing state. The method ensures DataFrame hash consistency and checks for version compatibility between the loaded data and the current installation.

## Args:
    data (bytes): Serialized profile report data created by the dumps() method

## Returns:
    Union["ProfileReport", "SerializeReport"]: Returns self (the current instance) after loading the data

## Raises:
    ValueError: When data fails to deserialize, contains invalid types, or when DataFrame hash doesn't match

## State Changes:
    Attributes READ: self.df_hash, self.df, self._description_set, self._report
    Attributes WRITTEN: self._description_set, self._report, self.config, self._df_hash

## Constraints:
    Preconditions: 
    - Input data must be valid pickle serialization from dumps() method
    - Data structure must contain exactly 4 elements: (df_hash, loaded_config, loaded_description_set, loaded_report)
    - All elements must match expected types: df_hash (None or str), loaded_config (Settings), loaded_description_set (BaseDescription or None), loaded_report (Root or None)
    
    Postconditions:
    - If DataFrame hash matches or df is None, data is loaded into appropriate attributes
    - If existing attributes are not None, warnings are issued but existing data is preserved
    - Version mismatch warnings are issued when applicable

## Side Effects:
    - Issues warnings via the warnings module for conflicting data or version mismatches
    - Mutates instance attributes: _description_set, _report, config, _df_hash

### `src.ydata_profiling.serialize_report.SerializeReport.dump` · *method*

## Summary:
Serializes and writes the report data to a file with .pp extension.

## Description:
Writes the serialized representation of the report's core components to disk. This method is used to persist a ProfileReport or SerializeReport object to a file for later loading. The serialization includes metadata about the dataframe, configuration, description set, and report structure.

## Args:
    output_file (Union[Path, str]): Path to the output file. Can be a string or pathlib.Path object. The file extension will be automatically changed to '.pp'.

## Returns:
    None: This method does not return any value.

## Raises:
    None explicitly raised, but may propagate exceptions from:
    - Path operations (if output_file path is invalid)
    - File writing operations (if permissions are insufficient)
    - Pickle serialization (if serialization fails)

## State Changes:
    Attributes READ: 
    - self.df_hash
    - self.config  
    - self._description_set
    - self._report
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The object must have valid state with initialized attributes (config, _description_set, _report)
    - The output_file path must be writable
    
    Postconditions:
    - A file with .pp extension will exist at the specified location
    - The file contains pickled binary data representing the serialized report state

## Side Effects:
    - Writes binary data to the filesystem at the specified output_file path
    - May create intermediate directories if they don't exist (depending on Path behavior)

### `src.ydata_profiling.serialize_report.SerializeReport.load` · *method*

## Summary:
Loads serialized profiling report data from a file into the current instance.

## Description:
Reads binary data from the specified file and deserializes it into the current SerializeReport instance. This method enables loading previously saved profiling reports from disk storage. The method is designed to be part of a serialization workflow where data is loaded from persistent storage back into memory.

## Args:
    load_file (Union[Path, str]): Path to the serialized file containing profiling report data. Can be either a pathlib.Path object or a string representing the file path.

## Returns:
    Union["ProfileReport", "SerializeReport"]: Returns the current instance (self) after loading the data, allowing for method chaining.

## Raises:
    ValueError: If the loaded data is corrupted, incompatible with the current version, or if the DataFrame hash doesn't match the current instance.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._description_set: Updated with loaded description set if not already populated
    - self._report: Updated with loaded report if not already populated
    - self.config: Updated with loaded configuration
    - self._df_hash: Updated with loaded DataFrame hash

## Constraints:
    Preconditions:
    - The load_file must exist and be readable
    - The file must contain valid serialized data compatible with the current version
    - If the instance already has data (non-None _description_set or _report), the loaded data will not overwrite existing data (warnings will be issued)
    - The DataFrame hash in the loaded data must match the current instance's DataFrame hash or the instance must have no DataFrame assigned

    Postconditions:
    - The instance's internal state is updated with data from the serialized file
    - All loaded data is validated against expected types and versions
    - If successful, the instance contains the loaded profiling report data

## Side Effects:
    - Reads from the filesystem at the specified file path
    - May issue warnings if existing data would be overwritten
    - May issue warnings if version mismatch is detected between loaded data and current installation

