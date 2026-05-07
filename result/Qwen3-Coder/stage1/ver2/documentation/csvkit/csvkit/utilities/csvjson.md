# `csvjson.py`

## `csvkit.utilities.csvjson.CSVJSON` · *class*

*No documentation generated.*

### `csvkit.utilities.csvjson.CSVJSON.add_arguments` · *method*

## Summary:
Configures command-line interface for CSV to JSON conversion with formatting, GeoJSON, and parsing options.

## Description:
Adds comprehensive command-line arguments to the argument parser for configuring CSV to JSON conversion behavior. This method sets up options for JSON output formatting (indentation, key-based output), GeoJSON generation (latitude/longitude/type/geometry/crs support), streaming output modes, and CSV parsing controls (sniffing limits, type inference). The configured arguments enable flexible conversion of CSV data to various JSON formats including standard arrays, keyed objects, and GeoJSON features.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (populated with command-line argument definitions)

## Constraints:
    Preconditions: self.argparser must be initialized and accessible
    Postconditions: self.argparser contains definitions for all supported CLI options for CSV to JSON conversion

## Side Effects:
    None

### `csvkit.utilities.csvjson.CSVJSON.main` · *method*

## Summary:
Entry point for the csvjson command-line utility that processes CSV data and outputs JSON, with support for geoJSON formatting and streaming options.

## Description:
This method serves as the primary execution point for converting CSV data to JSON format. It performs argument validation for geographic coordinate parameters (--lat, --lon, --crs, --type, --geometry) and routing logic to determine whether to stream output or load all data into memory. The method handles both regular JSON output and GeoJSON-specific output formats based on the presence of geographic coordinates.

## Args:
    None (method operates on instance attributes via self)

## Returns:
    None (performs I/O operations directly)

## Raises:
    SystemExit: When argument validation fails, triggering argparse errors

## State Changes:
    Attributes READ: self.args, self.argparser, self.json_kwargs, self.additional_input_expected(), self.can_stream(), self.is_geo()
    Attributes WRITTEN: self.json_kwargs (initialized with indentation settings)

## Constraints:
    Preconditions: 
    - When --lat is specified, --lon must also be specified
    - When --lon is specified, --lat must also be specified  
    - When --crs is specified, --lat must also be specified
    - When --type is specified, --lat must also be specified
    - When --geometry is specified, --lat must also be specified
    - When --key and --stream are used together, both --lat and --lon must also be specified
    - Input data must be available when not using streaming mode
    
    Postconditions:
    - self.json_kwargs is initialized with indentation settings
    - Either streaming or batch processing methods are called appropriately

## Side Effects:
    - Writes to stderr when waiting for standard input in streaming mode
    - Calls various output methods (output_json, output_geojson, streaming_output_ndjson, streaming_output_ndgeojson)
    - May exit the program via argparser.error() when validation fails

### `csvkit.utilities.csvjson.CSVJSON.dump_json` · *method*

## Summary:
Serializes data to JSON format and writes it to the output file with optional newline termination.

## Description:
Writes serialized JSON data to the configured output file using Python's built-in json module. This method handles the final serialization step in CSV to JSON conversion processes, supporting custom JSON formatting options through inherited configuration.

## Args:
    data (Any): The data structure to serialize to JSON format. Can be any JSON-serializable Python object.
    newline (bool): If True, appends a newline character after the JSON output. Defaults to False.

## Returns:
    None: This method does not return a value.

## Raises:
    TypeError: When data contains objects that are not JSON serializable, or when the output file cannot be written to.

## State Changes:
    Attributes READ:
    - self.output_file: The file-like object where JSON data is written
    - self.json_kwargs: Dictionary of additional keyword arguments for json.dump()

    Attributes WRITTEN:
    - None: This method does not modify object state beyond writing to output_file

## Constraints:
    Preconditions:
    - self.output_file must be a valid file-like object opened for writing
    - data must be JSON serializable (or have a custom serializer via default parameter)
    - self.json_kwargs must be a dictionary of valid json.dump() keyword arguments

    Postconditions:
    - Data is written to self.output_file in JSON format
    - If newline=True, a newline character is appended to the output

## Side Effects:
    - Writes to the file referenced by self.output_file
    - May raise IOError if the output file is not writable

### `csvkit.utilities.csvjson.CSVJSON.can_stream` · *method*

## Summary:
Determines whether streaming output can be enabled based on current argument configuration.

## Description:
Evaluates whether the current argument configuration allows for streaming output mode in the CSVJSON utility. This method returns True only when all four specific conditions are met, enabling efficient processing of large CSV files by writing JSON output incrementally.

The method checks four specific argument conditions:
1. streamOutput flag is True
2. no_inference flag is True  
3. sniff_limit equals 0
4. skip_lines is falsy (None or not specified)

This logic is encapsulated in a separate method to cleanly separate the streaming decision logic from the main execution flow.

## Args:
    self: The CSVJSON instance containing argument configuration

## Returns:
    bool: True if all streaming conditions are met, False otherwise

## Raises:
    None

## State Changes:
    Attributes READ:
        - self.args.streamOutput: Boolean flag for streaming output
        - self.args.no_inference: Boolean flag to disable type inference
        - self.args.sniff_limit: Integer limit for row sampling
        - self.args.skip_lines: Value indicating lines to skip

## Constraints:
    Preconditions:
        - self.args must be populated with parsed command-line arguments
        - All referenced arguments must be defined in the argument parser
    Postconditions:
        - Returns a boolean value indicating streaming capability

## Side Effects:
    None

### `csvkit.utilities.csvjson.CSVJSON.is_geo` · *method*

*No documentation generated.*

### `csvkit.utilities.csvjson.CSVJSON.read_csv_to_table` · *method*

## Summary:
Converts CSV input data into an agate Table object with proper column type inference and configuration.

## Description:
This method reads CSV data from the input file and constructs an agate Table instance, applying various configuration options such as skip lines, column type inference, and CSV reader parameters. It serves as the core data loading mechanism for the CSVJSON utility, transforming raw CSV data into a structured table format suitable for JSON conversion.

The method is called during the execution lifecycle of the CSVJSON utility, typically after command-line arguments have been parsed and input/output files have been opened. It leverages the parent CSVKitUtility class's configuration and helper methods to ensure consistent CSV processing behavior.

This method encapsulates the complex process of reading CSV files with proper handling of various CSV formatting options, making it reusable across different CSV processing utilities in the csvkit toolkit. By centralizing CSV reading logic, it ensures consistent behavior and reduces code duplication.

## Args:
    None - This is a bound method that operates on self

## Returns:
    agate.Table: An agate Table instance containing the CSV data with properly inferred column types

## Raises:
    IOError: When the input file cannot be read
    UnicodeDecodeError: When the input file contains invalid encoding
    agate.exceptions.CastError: When column type casting fails during table construction

## State Changes:
    Attributes READ:
    - self.args.sniff_limit
    - self.args.skip_lines
    - self.input_file
    - self.reader_kwargs
    - self.get_column_types() result
    Attributes WRITTEN:
    - None - This method returns a value but doesn't modify self's attributes

## Constraints:
    Preconditions:
    - self.input_file must be a valid file-like object opened for reading
    - self.args must contain the expected attributes (sniff_limit, skip_lines)
    - self.reader_kwargs must be a dictionary of valid CSV reader keyword arguments
    - self.get_column_types() must return a valid agate.TypeTester instance
    
    Postconditions:
    - Returns a properly constructed agate.Table instance
    - The returned table contains all CSV data with appropriate column types

## Side Effects:
    - Reads from self.input_file (I/O operation)
    - May perform file decompression if input is compressed (.gz, .bz2, .xz)
    - Calls self.get_column_types() which may involve type inference operations
    - Uses agate.Table.from_csv internally which may perform additional processing

### `csvkit.utilities.csvjson.CSVJSON.output_json` · *method*

## Summary:
Converts CSV data to JSON format and writes it to the output file with configurable formatting options.

## Description:
This method reads CSV data from the input file using the standard CSV processing pipeline and converts it to JSON format. It's part of the normal JSON conversion workflow and is called when neither GeoJSON processing nor streaming output is enabled. The method leverages the agate library's Table.to_json() method to perform the actual JSON serialization with support for various formatting options.

## Args:
    None - This is a method that operates on the instance state

## Returns:
    None - This method performs I/O operations and doesn't return a value

## Raises:
    None - Exceptions from underlying operations are propagated up

## State Changes:
    Attributes READ:
    - self.args.key: Column identifier for keying the JSON output
    - self.args.streamOutput: Flag indicating if output should be streamed as newline-separated objects
    - self.args.indent: Indentation level for formatted JSON output
    - self.input_file: Input file handle containing CSV data
    - self.output_file: Output file handle for JSON data

    Attributes WRITTEN:
    - None - This method doesn't modify instance attributes

## Constraints:
    Preconditions:
    - self.input_file must be properly opened and readable
    - self.output_file must be properly opened and writable
    - The CSV data must be valid and parseable by agate.Table.from_csv()
    - The method should only be called when not in GeoJSON mode (self.is_geo() returns False)
    - The method should only be called when not in streaming mode (self.can_stream() returns False)

    Postconditions:
    - The output file contains valid JSON data in the configured format
    - The JSON output follows the specified indentation, keying, and streaming options

## Side Effects:
    - Writes JSON data to self.output_file
    - Reads CSV data from self.input_file
    - May raise exceptions from agate.Table.from_csv() or JSON serialization if data is malformed

### `csvkit.utilities.csvjson.CSVJSON.output_geojson` · *method*

## Summary:
Converts CSV data to GeoJSON format, either as a streaming output of individual features or as a complete FeatureCollection.

## Description:
Processes CSV data into GeoJSON format by reading the input CSV into a table structure and using a GeoJsonGenerator to transform rows into GeoJSON features. This method supports two output modes: streaming individual GeoJSON features (when --stream is specified) or generating a complete GeoJSON FeatureCollection (the default). The method is called during the main execution flow when geographic data (latitude/longitude columns) is detected.

This logic is separated into its own method rather than being inlined because it encapsulates the complete workflow for GeoJSON conversion, including table reading, generator instantiation, and conditional output handling. It provides a clean interface for the CSV to GeoJSON conversion process while maintaining flexibility for different output formats.

## Args:
    None: This method does not accept any explicit arguments beyond the implicit self parameter.

## Returns:
    None: This method does not return a value.

## Raises:
    None explicitly raised: However, exceptions from underlying operations (table reading, JSON serialization, geometry processing) may propagate.

## State Changes:
    Attributes READ:
    - self.args: Command-line arguments controlling output format and geographic processing
    - self.input_file: Input file handle containing CSV data
    - self.output_file: Output file handle for writing JSON results
    - self.reader_kwargs: CSV reader configuration parameters
    - self.json_kwargs: JSON serialization configuration parameters

    Attributes WRITTEN:
    - None: This method does not modify object state beyond writing to output_file

## Constraints:
    Preconditions:
    - self.args must contain lat and lon arguments for geographic processing
    - self.input_file must be a valid file-like object opened for reading
    - self.output_file must be a valid file-like object opened for writing
    - The CSV data must contain columns corresponding to the geographic identifiers specified in args

    Postconditions:
    - GeoJSON output is written to self.output_file in the appropriate format
    - When streaming, each row is converted to a GeoJSON feature and written separately
    - When not streaming, a complete GeoJSON FeatureCollection is generated and written

## Side Effects:
    - Reads from the file referenced by self.input_file
    - Writes to the file referenced by self.output_file
    - May raise IOError if input file cannot be read or output file cannot be written
    - Calls external methods (read_csv_to_table, dump_json, GeoJsonGenerator) that may have their own side effects

### `csvkit.utilities.csvjson.CSVJSON.streaming_output_ndjson` · *method*

## Summary:
Converts CSV rows to newline-delimited JSON format, processing input incrementally to handle large files efficiently.

## Description:
This method reads CSV data from the input file and converts each row into a JSON object with column names as keys. It processes the data in a streaming fashion, making it suitable for large CSV files that might not fit in memory. The method reads the first row as column headers and then processes subsequent rows, mapping each column to its corresponding header name.

This logic is separated into its own method to enable reuse across different output formats and to maintain clean separation of concerns between data processing and output formatting. The streaming approach allows for efficient memory usage when converting large datasets.

## Args:
    None

## Returns:
    None

## Raises:
    IndexError: When a row has fewer columns than the header row, causing an IndexError when accessing row[i]. This is caught internally and handled by setting missing columns to None.

## State Changes:
    Attributes READ: self.input_file, self.reader_kwargs
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.input_file must be a readable file-like object containing valid CSV data
    - self.reader_kwargs must contain valid keyword arguments for agate.csv.reader
    - The first row of input data must contain column headers
    - All rows must be processable by agate.csv.reader with the provided reader_kwargs
    
    Postconditions:
    - Each CSV row is converted to a JSON object with proper column name mapping
    - Missing columns in rows are handled gracefully by setting them to None
    - Each JSON object is written to the output file as a separate line (NDJSON format)

## Side Effects:
    - Reads from self.input_file (CSV input stream)
    - Writes to self.output_file (JSON output stream via self.dump_json call)
    - Internally calls self.dump_json() which serializes the data to JSON and writes it to output

### `csvkit.utilities.csvjson.CSVJSON.streaming_output_ndgeojson` · *method*

## Summary:
Processes CSV data and outputs newline-delimited GeoJSON features for geographic data.

## Description:
This method converts CSV rows containing geographic data into newline-delimited GeoJSON features. It's specifically designed for streaming output when geographic coordinates (latitude/longitude) are present in the CSV. The method reads the CSV file incrementally, processes each row to create GeoJSON features, and outputs them as separate JSON objects, each terminated by a newline character.

This method is called during the streaming output phase when the CSV contains geographic data (--lat and --lon flags are specified) and the --stream flag is used. It provides efficient processing for large datasets by avoiding loading the entire dataset into memory.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.input_file, self.reader_kwargs, self.args, self.output_file, self.json_kwargs
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The CSV file must contain geographic data with latitude and longitude columns
    - The --stream flag must be enabled via command line arguments
    - The --lat and --lon arguments must specify valid column identifiers
    - The input file must be readable
    
    Postconditions:
    - Each row in the CSV is converted to a GeoJSON Feature object
    - Output is written to self.output_file as newline-delimited JSON
    - Features are properly formatted with geometry and properties

## Side Effects:
    - Reads from self.input_file (CSV data)
    - Writes to self.output_file (newline-delimited GeoJSON)
    - Calls self.dump_json() for each processed row

## `csvkit.utilities.csvjson.GeoJsonGenerator` · *class*

## Summary:
Generates GeoJSON FeatureCollection objects from CSV data by mapping geographic coordinates and other fields to GeoJSON features with appropriate geometry.

## Description:
The GeoJsonGenerator class transforms tabular CSV data into GeoJSON format, specifically creating FeatureCollection objects. It handles various ways of specifying geographic information including separate latitude/longitude columns, a geometry column containing JSON-encoded geometries, or a combination of both. The class supports optional bounding box calculation and coordinate reference system specification.

This class is typically instantiated by command-line utilities that process CSV files and convert them to GeoJSON format. It serves as the core conversion engine for geographic data transformation.

## State:
- args: Object containing command-line arguments for the conversion process
- column_names: List of column names from the CSV data
- lat_column: Integer index of the latitude column, or None if not specified
- lon_column: Integer index of the longitude column, or None if not specified
- type_column: Integer index of the feature type column, or None if not specified
- geometry_column: Integer index of the geometry column, or None if not specified
- id_column: Integer index of the ID column, or None if not specified

## Lifecycle:
Creation: Instantiate with args object and column_names list. The args object must contain lat, lon, type, geometry, key, no_bbox, and crs attributes.
Usage: Call generate_feature_collection() with an agate Table object to get the complete GeoJSON FeatureCollection.
Destruction: No explicit cleanup required; uses standard Python garbage collection.

## Method Map:
```mermaid
graph TD
    A[generate_feature_collection] --> B[feature_for_row]
    A --> C[GeoJsonBounds.add_feature]
    B --> D[geometry_for_row]
    D --> E[json.loads]
    D --> F[float conversion]
    B --> G[feature['geometry']]
    A --> H[OrderedDict construction]
    C --> I[update_coordinates]
    I --> J[update_lon]
    I --> K[update_lat]
```

## Raises:
- None explicitly raised by __init__
- ValueError may be raised internally during float conversion in geometry_for_row

## Example:
```python
# Assuming args contains lat, lon, and other configuration
generator = GeoJsonGenerator(args, ['name', 'lat', 'lon', 'population'])
feature_collection = generator.generate_feature_collection(table)
# Returns OrderedDict with type='FeatureCollection' and features array
```

### `csvkit.utilities.csvjson.GeoJsonGenerator.__init__` · *method*

## Summary:
Initializes a GeoJsonGenerator instance by setting up column identifier mappings from command-line arguments and column names.

## Description:
Configures column references for geographic data extraction by resolving column identifiers (names or 1-based indices) into 0-based integer indices. This method prepares the generator for creating GeoJSON features by identifying which columns contain latitude, longitude, geometry, type, and ID information.

The method processes command-line arguments to determine which CSV columns correspond to geographic coordinates, feature types, geometry data, and unique identifiers, converting user-specified column references into internal 0-based indices for efficient data access.

## Args:
    args (argparse.Namespace): Command-line arguments containing geo-related options (lat, lon, type, geometry, key, zero_based)
    column_names (list[str]): List of column names from the input CSV data

## Returns:
    None: This method initializes instance attributes and does not return a value

## Raises:
    ColumnIdentifierError: When column identifiers specified in args are invalid (non-existent column names or out-of-bounds indices)

## State Changes:
    Attributes READ: 
    - self.args.lat, self.args.lon, self.args.type, self.args.geometry, self.args.key, self.args.zero_based
    Attributes WRITTEN:
    - self.args
    - self.column_names
    - self.lat_column
    - self.lon_column
    - self.type_column
    - self.geometry_column
    - self.id_column

## Constraints:
    Preconditions:
    - args must contain lat and lon attributes for basic geographic processing
    - column_names must be a list of strings representing available CSV columns
    - args.zero_based should be a boolean indicating 0-based vs 1-based column indexing
    
    Postconditions:
    - All column identifier attributes (lat_column, lon_column, etc.) are set to either 0-based integer indices or None
    - The lat_column and lon_column attributes are guaranteed to be set (though potentially None if not specified)
    - All column attributes are properly resolved through match_column_identifier

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only processes internal state and performs column resolution calculations.

### `csvkit.utilities.csvjson.GeoJsonGenerator.generate_feature_collection` · *method*

## Summary:
Generates a GeoJSON FeatureCollection from a table by converting each row into a GeoJSON feature and optionally calculating bounding box coordinates.

## Description:
This method transforms tabular data into a GeoJSON FeatureCollection structure. It processes each row in the input table to create individual GeoJSON features using the helper method `feature_for_row`. When bounding box calculation is enabled via the `no_bbox` argument, it tracks feature coordinates to compute the overall bounding box. If a coordinate reference system is specified via the `crs` argument, it includes CRS information in the output.

## Args:
    table (agate.Table): The input table containing geographic data to convert to GeoJSON

## Returns:
    OrderedDict: A GeoJSON FeatureCollection structure with keys 'type', 'features', and optionally 'bbox' and 'crs'. The 'type' is always 'FeatureCollection', 'features' contains the list of converted features, 'bbox' is included when no_bbox=False, and 'crs' is included when crs argument is specified.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.args.no_bbox, self.args.crs
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - Input table must be a valid agate.Table instance
    - self.args must be properly initialized with relevant arguments
    - Helper methods feature_for_row and GeoJsonBounds must be available
    
    Postconditions:
    - Returns a properly formatted GeoJSON FeatureCollection OrderedDict
    - Bounding box is calculated only when self.args.no_bbox is False
    - CRS information is included only when self.args.crs is specified

## Side Effects:
    None

### `csvkit.utilities.csvjson.GeoJsonGenerator.feature_for_row` · *method*

## Summary:
Converts a CSV row into a GeoJSON Feature object with properties, ID, and geometry.

## Description:
Transforms a single row from a CSV dataset into a GeoJSON Feature structure. This method processes each cell in the row, assigning appropriate values to the feature's properties, ID, and geometry sections while excluding special columns designated for geometry metadata.

The method is called during the generation of GeoJSON FeatureCollections from CSV data, specifically within the `generate_feature_collection` method of the GeoJsonGenerator class. It serves as a key component in the conversion pipeline that maps tabular data to GeoJSON format.

## Args:
    row (list): A single row from a CSV dataset, represented as a list of values

## Returns:
    OrderedDict: A GeoJSON Feature object containing:
        - 'type': Always 'Feature'
        - 'properties': OrderedDict of non-special column values
        - 'id': Optional feature ID if an ID column is specified
        - 'geometry': Geometry object generated by `geometry_for_row` method

## Raises:
    None explicitly raised - however, underlying exceptions from `geometry_for_row` may propagate

## State Changes:
    Attributes READ: 
    - self.type_column
    - self.lat_column  
    - self.lon_column
    - self.geometry_column
    - self.id_column
    - self.column_names

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The row parameter must be a list with length matching the number of columns in the CSV
    - All column identifiers (lat_column, lon_column, etc.) must be properly initialized via match_column_identifier
    - The geometry_for_row method must be callable and return valid GeoJSON geometry

    Postconditions:
    - Returns a valid GeoJSON Feature structure with proper keys and values
    - The returned feature contains all non-special column data in properties
    - Geometry field is always present, though may be null/empty

## Side Effects:
    - Calls self.geometry_for_row(row) which may involve JSON parsing or coordinate conversion
    - Uses global functions like match_column_identifier for column resolution
    - May raise exceptions from underlying geometry processing operations

### `csvkit.utilities.csvjson.GeoJsonGenerator.geometry_for_row` · *method*

## Summary:
Generates a GeoJSON geometry object from a CSV row based on configured geometry columns or latitude/longitude columns.

## Description:
Creates a GeoJSON geometry object for a given CSV row. This method supports two primary approaches for geometry generation: parsing pre-formatted GeoJSON from a designated geometry column, or constructing a Point geometry from separate latitude and longitude columns. The method is called by `feature_for_row` during the GeoJSON feature generation process.

## Args:
    row (agate.Row): A single row from the CSV dataset being processed

## Returns:
    OrderedDict or None: A GeoJSON geometry object as an OrderedDict with 'type' and 'coordinates' keys for Point geometries, or the parsed JSON geometry from a geometry column. Returns None when no valid geometry can be constructed.

## Raises:
    None explicitly raised, though ValueError may be raised internally during float conversion

## State Changes:
    Attributes READ: self.geometry_column, self.lat_column, self.lon_column
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The row parameter must be a valid agate.Row object containing CSV data
    - The GeoJsonGenerator instance must have been properly initialized with column mappings
    
    Postconditions:
    - Returns a valid GeoJSON geometry structure or None
    - Does not modify any instance state

## Side Effects:
    None

## `csvkit.utilities.csvjson.GeoJsonBounds` · *class*

*No documentation generated.*

### `csvkit.utilities.csvjson.GeoJsonBounds.__init__` · *method*

*No documentation generated.*

### `csvkit.utilities.csvjson.GeoJsonBounds.bbox` · *method*

## Summary:
Returns the current geographic bounding box coordinates in GeoJSON format.

## Description:
Retrieves the minimum and maximum longitude and latitude values tracked by this GeoJsonBounds instance and returns them as a list in the standard GeoJSON bounding box format [min_lon, min_lat, max_lon, max_lat]. This method is typically called after processing a set of GeoJSON features to obtain the complete bounding box encompassing all features.

## Args:
    None: This method takes no arguments.

## Returns:
    list[float]: A list containing four numeric values representing the bounding box coordinates in the order [min_longitude, min_latitude, max_longitude, max_latitude]. Returns [None, None, None, None] if no coordinates have been processed yet.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: self.min_lon, self.min_lat, self.max_lon, self.max_lat
    Attributes WRITTEN: None: This method does not modify any instance attributes.

## Constraints:
    Preconditions: The GeoJsonBounds instance has been initialized (attributes exist).
    Postconditions: The returned list contains the current bounding box coordinates in the correct order.

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only accesses existing instance attributes.

### `csvkit.utilities.csvjson.GeoJsonBounds.add_feature` · *method*

## Summary:
Updates the bounding box coordinates by processing GeoJSON feature coordinates.

## Description:
Processes a GeoJSON feature to extract and update the minimum and maximum longitude and latitude values. This method is designed to be called iteratively for each feature in a GeoJSON dataset to build a complete bounding box that encompasses all features. It specifically handles the case where a feature contains geometry coordinates and updates the instance's bounding box tracking attributes accordingly.

## Args:
    feature (dict): A GeoJSON feature object containing geometry information with coordinates.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: self.min_lon, self.min_lat, self.max_lon, self.max_lat
    Attributes WRITTEN: self.min_lon, self.min_lat, self.max_lon, self.max_lat

## Constraints:
    Preconditions: The feature parameter must be a dictionary that contains a 'geometry' key with a 'coordinates' key.
    Postconditions: The instance's min_lon, min_lat, max_lon, and max_lat attributes are updated to reflect the bounding box that includes the provided feature's coordinates.

## Side Effects:
    Mutates the instance's min_lon, min_lat, max_lon, and max_lat attributes to track the bounding box coordinates.

### `csvkit.utilities.csvjson.GeoJsonBounds.update_lat` · *method*

## Summary:
Updates the minimum and maximum latitude values tracked by the bounding box instance.

## Description:
This method compares the provided latitude value against the currently stored minimum and maximum latitude values, updating them if the new value extends the bounding box coverage. It is called internally by the update_coordinates method when processing GeoJSON coordinate data to maintain accurate latitude bounds. This method follows the same pattern as update_lon and is part of the GeoJsonBounds class that tracks geographic bounding boxes for spatial data processing.

## Args:
    lat (float): The latitude value to compare and potentially update the bounding box with.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: self.min_lat, self.max_lat
    Attributes WRITTEN: self.min_lat, self.max_lat

## Constraints:
    Preconditions: The lat parameter should be a numeric value representing a latitude coordinate.
    Postconditions: The instance's min_lat and max_lat attributes are updated to reflect the new latitude value if it extends the current bounding box.

## Side Effects:
    Mutates the instance's min_lat and max_lat attributes to track the bounding box coordinates.

### `csvkit.utilities.csvjson.GeoJsonBounds.update_lon` · *method*

## Summary:
Updates the minimum and maximum longitude bounds with a new longitude value.

## Description:
This method maintains running minimum and maximum longitude values by comparing the provided longitude against existing bounds. It is designed to track geographic longitude bounds for GeoJSON coordinate processing. The method updates the instance's min_lon and max_lon attributes when the provided longitude value is outside the current bounds.

## Args:
    lon (float): The longitude value to compare and potentially update bounds with.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: self.min_lon, self.max_lon
    Attributes WRITTEN: self.min_lon, self.max_lon

## Constraints:
    Preconditions: The method assumes self.min_lon and self.max_lon are either None or numeric values that support comparison operations.
    Postconditions: After execution, self.min_lon contains the smaller of the previous minimum or the provided longitude, and self.max_lon contains the larger of the previous maximum or the provided longitude.

## Side Effects:
    None: This method only modifies the object's internal state attributes.

### `csvkit.utilities.csvjson.GeoJsonBounds.update_coordinates` · *method*

## Summary:
Updates the bounding box coordinates by processing GeoJSON coordinate arrays and tracking minimum/maximum longitude and latitude values.

## Description:
This method recursively processes GeoJSON coordinate data to update the bounding box coordinates tracked by the GeoJsonBounds instance. It handles both simple coordinate pairs (for Point geometries) and nested coordinate arrays (for LineString, Polygon, and Multi-geometry types). The method is called internally by the add_feature method when processing GeoJSON features to build a complete bounding box encompassing all geometries.

## Args:
    coordinates (list): A list of coordinate values that can be either:
        - A simple list of 2-3 numeric values [longitude, latitude, altitude] for Point geometries
        - A nested list structure containing multiple coordinate sets for LineString, Polygon, or Multi-geometry types

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying type checking may cause errors if invalid data is passed.

## State Changes:
    Attributes READ: self.min_lon, self.min_lat, self.max_lon, self.max_lat
    Attributes WRITTEN: self.min_lon, self.min_lat, self.max_lon, self.max_lat

## Constraints:
    Preconditions: The coordinates parameter must be a list-like object with appropriate numeric values for longitude and latitude.
    Postconditions: The instance's bounding box attributes (min_lon, min_lat, max_lon, max_lat) are updated to reflect the new coordinate values.

## Side Effects:
    Mutates the instance's min_lon, min_lat, max_lon, and max_lat attributes to track the bounding box coordinates.

## `csvkit.utilities.csvjson.launch_new_instance` · *function*

## Summary:
Launches a new instance of the CSVJSON command-line utility to convert CSV data into JSON or GeoJSON format.

## Description:
This function serves as the primary entry point for executing the csvjson command-line utility. It creates a new instance of the CSVJSON class and invokes its run method to process CSV input according to command-line arguments. This follows the standard pattern used by all csvkit utilities for launching command-line tools.

The function is typically called by the csvkit command-line framework when the csvjson utility is invoked, allowing for proper setup of argument parsing, file handling, and CSV processing before executing the conversion logic. This pattern enables clean separation between utility instantiation and execution, making the code more modular and testable.

## Args:
    None

## Returns:
    None (The function does not return any meaningful value. Execution continues through the CSVJSON utility's run method which handles the actual processing and output.)

## Raises:
    SystemExit: Raised by the underlying CSVKitUtility.run() method when command-line arguments are invalid or when processing completes successfully
    IOError: Raised by file I/O operations when reading input files or writing output files fails
    csv.Error: Raised by CSV parsing when malformed CSV data is encountered
    MemoryError: Raised when insufficient memory is available for processing large CSV files

## Constraints:
    Preconditions:
    - Command-line arguments must be available in sys.argv for parsing
    - Input files must be readable and output directories must be writable
    - Environment must support file system operations
    
    Postconditions:
    - A CSVJSON utility instance is created and executed
    - Command-line arguments are parsed and processed
    - CSV data is converted to JSON or GeoJSON format according to specifications
    - Results are written to the configured output destination

## Side Effects:
    - Parses command-line arguments from sys.argv
    - Reads input CSV files from disk or stdin
    - Writes processed JSON or GeoJSON data to stdout or specified output file
    - May read from stdin if no input files are provided
    - May write to stderr when prompting for standard input or displaying error messages

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance called] --> B[Create CSVJSON instance]
    B --> C[Call utility.run()]
    C --> D{Argument parsing complete}
    D --> E{Stream output requested?}
    E -->|Yes| F{GeoJSON mode?}
    F -->|Yes| G[streaming_output_ndgeojson()]
    F -->|No| H[streaming_output_ndjson()]
    E -->|No| I{GeoJSON mode?}
    I -->|Yes| J[output_geojson()]
    I -->|No| K[output_json()]
    G --> L[End]
    H --> L
    J --> L
    K --> L
```

## Examples:
```python
# Typical command-line usage (which internally calls this function):
# csvjson input.csv

# Convert to GeoJSON with latitude and longitude columns:
# csvjson -l lat_col -o lon_col input.csv

# Output with indentation:
# csvjson -i 2 input.csv

# Output as newline-delimited JSON:
# csvjson --stream input.csv

# Using with piped input:
# echo "a,b,c\n1,2,3" | csvjson
```

