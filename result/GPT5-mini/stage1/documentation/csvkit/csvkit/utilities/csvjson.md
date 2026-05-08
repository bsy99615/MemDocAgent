# `csvjson.py`

## `csvkit.utilities.csvjson.CSVJSON` · *class*

*No documentation generated.*

### `csvkit.utilities.csvjson.CSVJSON.add_arguments` · *method*

## Summary:
Registers all command-line options for the csvjson utility by adding argument definitions to the instance's argument parser (self.argparser), mutating the parser state so subsequent parsing will produce the corresponding attributes.

## Description:
This method declares the csvjson CLI options by calling self.argparser.add_argument repeatedly. It is intended to be executed during CLI setup/initialization (before parsing arguments) so that the parser knows about the options used by the csvjson utility.

Why this is a separate method:
- Encapsulates all CLI option definitions for csvjson in one place for readability and easy extension/override.
- Keeps argument registration separate from parsing and business logic.

Known callers / invocation context:
- There are no explicit callers in this file. In typical use, the CSVKit framework or the csvjson command-line entrypoint calls into the utility initialization lifecycle to build the parser; that lifecycle invokes this method to register options prior to parsing. This method is not responsible for parsing or validating cross-option constraints.

The method does not perform validation of option relationships (for example, it does not enforce that --lat requires --lon); it only registers options and their metadata (dest, type, action, help, defaults).

The following option definitions are added (each line corresponds to a call to self.argparser.add_argument in the source):

- Flags: -i, --indent
  - dest: indent
  - type: int
  - default: not set by this method (parser will supply None if not provided)
  - action: (none)
  - help: Indent the output JSON this many spaces. Disabled by default.

- Flags: -k, --key
  - dest: key
  - type: str
  - default: None
  - action: (none)
  - help: Output JSON as an object keyed by a given column, KEY, rather than as an array. All column values must be unique. If --lat and --lon are specified, this column is used as the GeoJSON Feature ID.

- Flags: --lat
  - dest: lat
  - type: str
  - default: None
  - action: (none)
  - help: A column index or name containing a latitude. Output will be GeoJSON instead of JSON. Requires --lon.

- Flags: --lon
  - dest: lon
  - type: str
  - default: None
  - action: (none)
  - help: A column index or name containing a longitude. Output will be GeoJSON instead of JSON. Requires --lat.

- Flags: --type
  - dest: type
  - type: str
  - default: None
  - action: (none)
  - help: A column index or name containing a GeoJSON type. Output will be GeoJSON instead of JSON. Requires --lat and --lon.
  - Note: dest name 'type' deliberately matches the source; it shadows the builtin name but is an argparse destination only.

- Flags: --geometry
  - dest: geometry
  - type: str
  - default: None
  - action: (none)
  - help: A column index or name containing a GeoJSON geometry. Output will be GeoJSON instead of JSON. Requires --lat and --lon.

- Flags: --crs
  - dest: crs
  - type: str
  - default: None
  - action: (none)
  - help: A coordinate reference system string to be included with GeoJSON output. Requires --lat and --lon.

- Flags: --no-bbox
  - dest: no_bbox
  - action: store_true
  - type: bool (resulting value)
  - default: False (when option absent)
  - help: Disable the calculation of a bounding box.

- Flags: --stream
  - dest: streamOutput
  - action: store_true
  - type: bool (resulting value)
  - default: False (when option absent)
  - help: Output JSON as a stream of newline-separated objects, rather than as an array.

- Flags: -y, --snifflimit
  - dest: sniff_limit
  - type: int
  - default: 1024
  - action: (none)
  - help: Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely, or "-1" to sniff the entire file.

- Flags: -I, --no-inference
  - dest: no_inference
  - action: store_true
  - type: bool (resulting value)
  - default: False (when option absent)
  - help: Disable type inference (and --locale, --date-format, --datetime-format) when parsing CSV input.

## Args:
    None

## Returns:
    None

## Raises:
    This method does not explicitly raise exceptions in its body.
    - If self.argparser is None or does not provide an add_argument attribute, a Python AttributeError will be raised when attempting to call add_argument.
    - Any exceptions raised by the underlying argument parser (e.g., argparse raising ValueError for an invalid option configuration) will propagate from the parser's add_argument calls.

## State Changes:
Attributes READ:
    - self.argparser (the method calls add_argument on it and reads its reference)

Attributes WRITTEN:
    - No attributes on self are reassigned by this method.
    - The method mutates the state of the external parser object referenced by self.argparser (the parser gains new option definitions and will subsequently populate parsed argument attributes such as indent, key, sniff_limit, etc.).

## Constraints:
Preconditions:
    - self.argparser must be assigned to an object that implements argparse-like add_argument(name/flags..., **kwargs).
    - The method must be called before argument parsing with self.argparser.parse_args().

Postconditions:
    - After the call, self.argparser is configured with the options documented above. Parsing arguments with that parser will populate the corresponding destinations (args.indent, args.key, args.lat, args.lon, args.type, args.geometry, args.crs, args.no_bbox, args.streamOutput, args.sniff_limit, args.no_inference).
    - The method itself does not enforce semantic constraints among options (for example, it does not validate that --lat and --lon are supplied together); such validation must be performed by later logic that runs after parsing.

## Side Effects:
    - Mutates self.argparser by registering argument definitions (calls add_argument on it).
    - No direct I/O, file, network, or external service interactions occur in this method.

### `csvkit.utilities.csvjson.CSVJSON.main` · *method*

## Summary:
Validate interdependent CLI arguments for geographic and streaming options, set the instance JSON formatting options, and dispatch to the appropriate streaming or batch JSON/GeoJSON output routine; results are produced via side effects (output, stderr, or argparser errors).

## Description:
This method is the top-level execution step for the CSV-to-JSON utility: it performs argument validation, configures JSON serialization options on the instance, and chooses which output routine to invoke.

Known/expected callers and lifecycle stage:
- Typically invoked by the CLI runner or command dispatch logic after the utility instance has been created and CLI arguments parsed. This is the orchestration step that runs when the command is executed.
- The logic is isolated in this method to centralize validation and dispatch (so downstream output routines can assume valid, normalized argument/state and focus on serialization/IO).

Why this is a separate method:
- Consolidates all inter-argument validation rules in one place.
- Establishes instance-level JSON options (self.json_kwargs) for use by output routines.
- Selects between streaming vs. batch and geo vs. non-geo output using small helper predicates (can_stream, is_geo), improving readability and testability.

## Args:
This method accepts no parameters; it operates on instance state:
- self.args (required): an object with attributes used below.

## Returns:
None. The function does not return a value; its observable behavior is through side effects (writing output, emitting errors, or writing to stderr).

## Raises:
This method does not directly raise Python exceptions; instead it calls self.argparser.error(...) to report CLI validation failures. Specifically, self.argparser.error(...) is called with the exact messages below under these conditions:
- If --lat is provided but --lon is not:
    - Error message: '--lon is required whenever --lat is specified.'
- If --lon is provided but --lat is not:
    - Error message: '--lat is required whenever --lon is specified.'
- If --crs is provided but --lat (and therefore --lon) are not:
    - Error message: '--crs is only allowed when --lat and --lon are also specified.'
- If --type is provided but --lat/--lon are not:
    - Error message: '--type is only allowed when --lat and --lon are also specified.'
- If --geometry is provided but --lat/--lon are not:
    - Error message: '--geometry is only allowed when --lat and --lon are also specified.'
- If --key is provided together with stream output (self.args.streamOutput is truthy) but lat/lon are not both provided:
    - Error message: '--key is only allowed with --stream when --lat and --lon are also specified.'
- If not in streaming mode and additional input is expected (additional_input_expected() returns true):
    - Error message: 'You must provide an input file or piped data.'

Note: The observable effect of self.argparser.error(...) (exit behavior, exception type, or printed output) is determined by the argument parser implementation; this method delegates error handling to it.

## State Changes:
Attributes READ:
- self.args and the following attributes on it:
    - lat
    - lon
    - crs
    - type
    - geometry
    - key
    - streamOutput
    - indent
- self.argparser (used to report errors)
- The following instance methods are called (their return values are read):
    - self.can_stream()
    - self.additional_input_expected()
    - self.is_geo()

Attributes WRITTEN:
- self.json_kwargs: set to a dict containing exactly {'indent': self.args.indent}

## Constraints:
Preconditions:
- self.args must exist and expose the attributes listed above.
- self.argparser must exist and implement an error(message: str) method.
- The methods self.can_stream(), self.additional_input_expected(), and self.is_geo() must be implemented and return truthy/falsey values.
- The output methods invoked (streaming_output_ndgeojson, streaming_output_ndjson, output_geojson, output_json) must be defined on the instance; this method assumes they perform the actual output side effects.

Postconditions:
- After successful execution (no argparser.error called), self.json_kwargs will be assigned {'indent': self.args.indent}.
- Exactly one downstream output method will be called:
    - If can_stream() is true:
        - If additional_input_expected() is true: may write a waiting message to stderr, then call either streaming_output_ndgeojson() or streaming_output_ndjson() depending on is_geo().
        - Otherwise: call streaming_output_ndgeojson() if is_geo() else streaming_output_ndjson().
    - If can_stream() is false:
        - If additional_input_expected() is true: self.argparser.error(...) will be invoked (see Raises).
        - Otherwise: call output_geojson() if is_geo() else output_json().

## Side Effects:
- Calls self.argparser.error(...) with one of the messages listed above when validation fails (this typically results in program termination or an error exit, depending on the parser).
- If streaming is enabled and input is expected, writes the exact message 'No input file or piped data provided. Waiting for standard input:\n' to standard error via sys.stderr.write(...).
- Calls one of the output routines (streaming_output_ndgeojson, streaming_output_ndjson, output_geojson, output_json) which perform JSON/GeoJSON serialization and write to stdout or streaming output. These downstream routines may perform I/O (file/stdout), and/or raise their own exceptions.
- No return value; caller should rely on side effects for results.

### `csvkit.utilities.csvjson.CSVJSON.dump_json` · *method*

## Summary:
Serialize the given Python object as JSON to the configured output stream, using the repository's serializer fallback and JSON options; optionally append a newline.

## Description:
This helper centralizes JSON output for CSVJSON's various output paths. It is invoked during the output-generation stage of the utility, both for streaming (newline-delimited) and non-streaming outputs.

Known callers and contexts:
- CSVJSON.output_geojson: Used for both streaming and non-streaming GeoJSON output.
  - In streaming mode: called once per input row to write an individual GeoJSON Feature (newline=True).
  - In non-streaming mode: called once to write the full FeatureCollection object (newline=False).
- CSVJSON.streaming_output_ndjson: Called once per input row to write an OrderedDict representing the row as a JSON object (newline=True).
- CSVJSON.streaming_output_ndgeojson: Called once per input row to write a GeoJSON Feature derived from a row (newline=True).

Why this is a separate method:
- Ensures consistent json.dump configuration (default serializer, ensure_ascii behavior, and passed json_kwargs) across multiple output code paths.
- Encapsulates the newline behavior for streaming outputs so callers need only provide the data and whether a trailing newline is required.
- Avoids duplicating error/encoding handling and keeps callers focused on data construction.

## Args:
    data (any): The Python object to serialize (typically an OrderedDict, dict, list, or other JSON-serializable structure).
        - Expected contents: basic JSON types (dict/list/str/int/float/bool/None) and optionally date/datetime/decimal.Decimal values which are handled by the default serializer (default_str_decimal).
        - If the object contains types not serializable by the json module and not handled by default_str_decimal, json.dump will raise TypeError.
    newline (bool, optional): Whether to append a single newline character after the JSON payload. Defaults to False.

## Returns:
    None
    - The method does not return a value; its observable effect is writing to self.output_file.
    - Edge cases:
        * If the serialization fails, an exception is raised and nothing is returned.
        * If newline is True, a single "\n" is written after the JSON text.

## Raises:
    TypeError: If json.dump encounters an object it cannot serialize and the fallback (default_str_decimal) does not support that type. This is raised by the JSON encoder (propagated).
    OSError / IOError (or subclasses, e.g., BrokenPipeError): If writing to self.output_file fails (e.g., disk full, closed pipe). These are raised by the underlying file.write or json.dump and are propagated.
    ValueError: Unlikely from json.dump in normal use, but any exceptions raised by the default serializer (default_str_decimal) are propagated; those include TypeError for unsupported types.

## State Changes:
    Attributes READ:
        - self.output_file: the file-like object to which JSON text is written (expected to implement write(str)).
        - self.json_kwargs: dict of keyword arguments forwarded to json.dump (e.g., {'indent': int|None}).
    Attributes WRITTEN:
        - None of the object's attributes are modified by this method.

## Constraints:
    Preconditions:
        - self.output_file must be an open, writable text-mode file-like object with a write(str) method (commonly sys.stdout or an open text file).
        - self.json_kwargs must be a mapping of parameters valid for json.dump (e.g., may contain 'indent': int or None).
        - default_str_decimal must be available in the module namespace to handle date/datetime/Decimal fallback serialization.
    Postconditions:
        - If no exception is raised, the serialized JSON representation of data is appended to self.output_file using the options in self.json_kwargs and ensure_ascii=False.
        - If newline is True, a single trailing newline character ("\n") is appended after the JSON text.
        - No attributes on self are mutated by this call.

## Side Effects:
    - I/O: Writes text to self.output_file. This can be stdout, a file on disk, or any other file-like stream; it may result in disk writes or terminal output.
    - The output uses ensure_ascii=False so non-ASCII characters are written directly (not escaped) according to the output stream's encoding.
    - Exceptions from serialization or from writing to the stream will propagate to callers (no internal swallowing).
    - No network or external service calls are made.

### `csvkit.utilities.csvjson.CSVJSON.can_stream` · *method*

## Summary:
Return True when conditions allow safe, row-by-row streaming JSON output; does not modify object state.

## Description:
This method evaluates the runtime argument flags to decide whether CSV-to-JSON conversion can be performed as a streaming operation (emitting JSON per row) instead of performing inference/aggregation before output.

Known callers and context:
- Typically invoked by the CSVJSON command implementation during the execution phase (e.g., just before converting or writing rows) to select the output strategy: streaming versus non-streaming. It is used at the decision point in the conversion pipeline where the utility chooses whether to emit JSON incrementally or to perform full inference/collection first.

Why this is a separate method:
- Encapsulates a single boolean predicate composed of multiple argument checks so the same decision logic can be reused and tested in one place rather than duplicated inline at call sites. It keeps high-level control flow readable and isolates the conditions that enable streaming.

## Args:
None.

## Returns:
bool
- True: all of the following are satisfied and streaming output is allowed:
    - streamOutput flag is enabled
    - inference is disabled (no_inference)
    - sniff_limit is exactly 0 (no sniffing/peeking of rows)
    - skip_lines is falsy (no lines are skipped before processing)
- False: if any of the above conditions is not met. There are no other return values.

## Raises:
None. The method performs attribute access only; it does not explicitly raise exceptions. If expected attributes are missing on self.args, an AttributeError may be raised by Python attribute lookup.

## State Changes:
Attributes READ:
- self.args.streamOutput
- self.args.no_inference
- self.args.sniff_limit
- self.args.skip_lines

Attributes WRITTEN:
- None

## Constraints:
Preconditions:
- self.args must exist and provide the attributes streamOutput, no_inference, sniff_limit, and skip_lines.
- streamOutput and no_inference are expected to be truthy/falsy values (typically booleans).
- sniff_limit is expected to be an integer or numeric type that can be compared to 0.
- skip_lines is expected to be a truthy/falsy value (often an int or None).

Postconditions:
- No mutation of self or external state occurs.
- The return value deterministically reflects the logical conjunction of the four checked conditions described above.

## Side Effects:
- None. The method only reads attributes and returns a boolean; it performs no I/O and does not call external services or mutate objects outside of self.

### `csvkit.utilities.csvjson.CSVJSON.is_geo` · *method*

## Summary:
Return whether both latitude and longitude arguments are present (truthy) on the object's parsed arguments.

## Description:
This method evaluates whether both self.args.lat and self.args.lon are present (i.e., evaluate to truthy values) and returns the result of that conjunction. It encapsulates the small decision logic used to determine whether geographic coordinates were supplied.

Known callers and context:
- The provided source snippet does not include callers. In typical usage within a CSV-to-JSON conversion utility, this check would be invoked where output formatting or validation needs to know if both coordinate arguments were supplied.

Why this is a separate method:
- Encapsulates a single logical check in one place for clarity and reuse (so callers can ask a semantic question "are we in geo-mode?" instead of repeating the attribute checks inline).

## Args:
None.

## Returns:
- type: Any (truthy/falsy) — specifically, returns the result of the Python expression self.args.lat and self.args.lon.
- possible values:
    - If self.args.lat is falsy (for example None, False, empty string, 0), the method returns that falsy value.
    - If self.args.lat is truthy, the method returns self.args.lon (which may be truthy or falsy).
- Edge cases:
    - The return value is not coerced to a boolean; callers that require a strict boolean should wrap the call with bool(...) to obtain True/False.
    - If both attributes are present and truthy, the method will return the value of self.args.lon (not necessarily the boolean True).

## Raises:
- No exceptions are raised by this method itself.
- AttributeError will be raised if self.args does not exist or does not have attributes lat and/or lon; this method does not guard against a missing or malformed self.args.

## State Changes:
- Attributes READ:
    - self.args.lat
    - self.args.lon
- Attributes WRITTEN:
    - None (this method does not modify object state)

## Constraints:
- Preconditions:
    - self must have an attribute args.
    - self.args must expose attributes lat and lon (attributes may be of any type).
- Postconditions:
    - No mutation of self or self.args occurs.
    - The return value correctly reflects the Python logical AND of self.args.lat and self.args.lon (see Returns for exact behavior).

## Side Effects:
- None. The method performs no I/O, external calls, or mutations outside the object.

### `csvkit.utilities.csvjson.CSVJSON.read_csv_to_table` · *method*

## Summary:
Reads CSV input into an agate Table using the command's configured parsing options and type inference, returning a fully-constructed Table without mutating the command object's persistent state.

## Description:
Known callers and context:
- output_json: called when converting the entire CSV to JSON (non-streaming path).
- output_geojson: called when converting the entire CSV to GeoJSON (non-streaming path).
Lifecycle stage:
- Invoked after CLI argument parsing and validation, when the utility needs a materialized in-memory table for full (non-streaming) conversion or generation of derived outputs.

Why this logic is a separate method:
- Encapsulates the one place where CSV parsing, skip-line handling, sniff-limit translation, column type injection, and reader kwargs are combined to produce an agate.Table.
- Keeps consumer methods (output_json, output_geojson) concise and avoids duplicating from_csv call semantics across different outputs.
- Makes it easy to override or test CSV-to-Table behavior in subclasses.

## Args:
- None (method is invoked on self and relies on attributes described below).

## Returns:
- agate.Table
    - A newly created agate.Table instance produced by agate.Table.from_csv.
    - On success the returned Table contains columns and rows parsed from self.input_file using:
        - skip_lines = self.args.skip_lines
        - sniff_limit = None if self.args.sniff_limit == -1 else self.args.sniff_limit
        - column_types = result of self.get_column_types()
        - any additional keyword arguments supplied via self.reader_kwargs
    - There is no alternative "null" return; failures raise exceptions.

## Raises:
- Propagates any exceptions raised by agate.Table.from_csv or by called helpers:
    - Examples (not exhaustive): file I/O errors (OSError/FileNotFoundError) if input_file refers to an unreadable path; CSV parsing errors from the agate/csv parser; exceptions raised by self.get_column_types (e.g., AttributeError or TypeError if self.args are malformed).
- AttributeError: if required attributes on self (see Preconditions) are missing.
- TypeError: if self.reader_kwargs is not a mapping or if self.get_column_types() returns an invalid value for column_types; such type errors may originate here or from agate internals.

## State Changes:
- Attributes READ:
    - self.args.sniff_limit
    - self.args.skip_lines
    - self.input_file
    - self.reader_kwargs
    - the return value of self.get_column_types() (i.e., calls/reads that helper)
- Attributes WRITTEN:
    - None. The method does not assign to any self.<attr>.

## Constraints:
Preconditions:
- self must have:
    - args with attributes sniff_limit (int) and skip_lines (int or falsy), and other args used indirectly by get_column_types (see CSVKitUtility.get_column_types).
    - input_file: a readable file-like object or a path acceptable to agate.Table.from_csv.
    - reader_kwargs: a dict (or mapping) of keyword arguments acceptable to agate.Table.from_csv / underlying CSV reader.
    - get_column_types(): a callable on self that returns a value acceptable as the column_types parameter accepted by agate.Table.from_csv (typically an agate.TypeTester, a mapping, or sequence per agate API expectations).
- If self.args.sniff_limit is -1, the method converts it to None; other integer values (including 0) are forwarded as-is.

Postconditions:
- On successful return, an agate.Table has been constructed and returned; no attributes on self have been mutated by this method.
- If input_file is a file-like object, its read position is advanced by the Table.from_csv call (i.e., the stream has been consumed up to the end of the parsed content).

## Side Effects:
- Performs I/O: reading from self.input_file. This will advance the file/stream position and may block if input is stdin and data is not yet available.
- Delegates to agate.Table.from_csv which performs CSV parsing and type inference (which may be CPU- or memory-intensive for large inputs).
- May cause exceptions originating from file I/O or agate's parsing/inference to be raised to the caller.

### `csvkit.utilities.csvjson.CSVJSON.output_json` · *method*

## Summary:
Invoke the table-to-JSON exporter: read CSV input into an agate Table and write its JSON representation to the configured output file-like object. This produces the final JSON output for the non-streaming, non-GeoJSON path and advances/writes to self.output_file.

## Description:
This method is the non-streaming JSON output path for CSVJSON. It performs two steps:
1. Calls self.read_csv_to_table() to parse the input CSV and produce an agate.Table.
2. Calls the agate.Table.to_json(...) method to serialize that table as JSON into self.output_file according to current CLI arguments.

Known callers and lifecycle stage:
- CSVJSON.main() — when can_stream() is False and is_geo() is False, main() calls this method to produce output for the standard (non-GeoJSON), non-streaming case. In the typical command-line lifecycle this is the last step once input parsing and validation have completed.

Why this is a separate method:
- Separates the concerns of JSON vs GeoJSON output and streaming vs non-streaming logic, keeping main() compact and testable.
- Encapsulates the non-streaming serialization step so it can be overridden or unit-tested independently of CSV parsing or GeoJSON generation.

## Args:
None (method uses instance attributes and helper methods; no parameters).

## Returns:
None (implicitly returns None). The observable result is the side effect of writing serialized JSON to self.output_file.

## Raises:
This method does not catch exceptions. It will propagate any exceptions raised by:
- self.read_csv_to_table() (for example, CSV parsing/IO errors raised by agate.Table.from_csv or file I/O)
- agate.Table.to_json(...) (for example, serialization errors raised by agate or underlying file write failures)
No additional exception handling is performed here.

## State Changes:
Attributes READ:
- self.output_file (file-like object passed to to_json; used for writing)
- self.args.key (value passed as to_json key parameter)
- self.args.streamOutput (passed as newline parameter to to_json)
- self.args.indent (passed as indent parameter to to_json)
- Indirectly via read_csv_to_table():
  - self.input_file (source CSV read by read_csv_to_table)
  - self.args.sniff_limit, self.args.skip_lines (used by read_csv_to_table)
  - self.reader_kwargs (forwarded to agate.Table.from_csv)
  - Any state accessed by self.get_column_types()

Attributes WRITTEN / MUTATED:
- No instance attributes are reassigned by this method.
- External mutation: self.output_file is written to (the file pointer/stream is advanced and bytes/text are written).

## Constraints:
Preconditions:
- self.output_file must be a writable file-like object (supporting .write()) and open when called.
- self.input_file (used by read_csv_to_table) must be readable and positioned appropriately.
- self.args must have attributes key, streamOutput, and indent (populated by argument parsing).
- Any state or methods required by read_csv_to_table (e.g., get_column_types, reader_kwargs) must be available and correct.

Postconditions:
- The JSON serialization of the input CSV (as produced by agate.Table.to_json with the supplied key/newline/indent arguments) has been written to self.output_file.
- The method returns None.
- No instance attributes are modified by this method (aside from the external side-effect on the output file object).

## Side Effects:
- I/O: writes JSON text to self.output_file using agate.Table.to_json. This is the primary side effect and includes advancing the file/stream pointer and performing write operations.
- May propagate I/O-related exceptions (e.g., write errors, broken pipe) or parsing/serialization errors from agate without handling them.
- No network or external service calls are made.

### `csvkit.utilities.csvjson.CSVJSON.output_geojson` · *method*

## Summary:
Reads the input CSV into an agate.Table and writes GeoJSON output to the utility's output stream — either a newline-delimited stream of GeoJSON Feature objects (one per row) when streaming is enabled, or a single GeoJSON FeatureCollection containing all features.

## Description:
Known callers and lifecycle:
- Called from CSVJSON.main when the utility has determined it should produce GeoJSON (i.e., --lat and --lon were provided) and the non-streaming code path is taken. In the main pipeline this is the final serialization stage that consumes parsed CSV data and emits GeoJSON to the configured output file/stream.
- There is a separate streaming code path implemented by streaming_output_ndgeojson which produces newline-delimited features without building an agate.Table first; output_geojson is the non-streaming (table-based) counterpart.

Why this logic is a separate method:
- The method encapsulates the non-stream GeoJSON output flow (read table, instantiate generator, and emit features) so that streaming and non-streaming behaviors are implemented separately and share the GeoJsonGenerator logic without duplicating table-building or serialization details.

## Args:
- None (method uses attributes on self; callers provide configuration via self.args).

## Returns:
- None (the method returns implicitly). Its observable result is that GeoJSON data has been serialized to self.output_file via self.dump_json:
  - If self.args.streamOutput is truthy: writes one JSON Feature per table row, each terminated by a newline.
  - Otherwise: writes a single JSON FeatureCollection representing all rows.

## Raises:
- Propagates any exception raised by:
  - self.read_csv_to_table(): e.g., IO or parsing errors from agate.Table.from_csv.
  - GeoJsonGenerator(...) constructor: exceptions raised while resolving column identifiers (match_column_identifier) if provided column identifiers are invalid.
  - geojson generation routines invoked on the generator:
    - geojson_generator.feature_for_row(row): may propagate IndexError/TypeError if rows are not indexable or have mismatched length.
    - geojson_generator.generate_feature_collection(table): may propagate errors coming from feature_for_row or GeoJsonBounds.
    - geojson_generator.geometry_for_row may propagate json.loads exceptions (json.JSONDecodeError) if a geometry column contains invalid JSON.
  - self.dump_json(...) / json.dump: TypeError or other JSON serialization errors if the generated structures contain non-serializable objects.
- The method does not catch these exceptions; they will propagate to the caller.

## State Changes:
Attributes READ:
- self.args — used to determine streaming mode and passed into the GeoJsonGenerator for column resolution and other options (e.g., args.streamOutput, args.no_bbox, args.crs).
- self.output_file — implicitly read/written by self.dump_json when serializing output.
- (Indirectly) the reader configuration used by self.read_csv_to_table — read by that method (e.g., self.args.sniff_limit, self.reader_kwargs) but not directly referenced in this method.

Attributes WRITTEN:
- None of the CSVJSON instance attributes are modified by this method. All work is performed by creating local variables (table, geojson_generator) and by writing to the external output stream via self.dump_json.

## Constraints:
Preconditions:
- The CSV input must be available and readable by read_csv_to_table (otherwise read_csv_to_table will raise).
- The GeoJSON semantics expected by callers assume that self.args contains valid column identifier values when geo output is desired (typically ensured earlier in CLI argument validation). In particular, arguments referenced by the generator (lat, lon, optional geometry/type/key, and zero_based) should be present and meaningful for the table's column_names.
- table.column_names must correspond to the columns present in table.rows (the GeoJsonGenerator resolves indices based on column_names and later indexes into rows by those indices).

Postconditions:
- After successful return:
  - If streaming (self.args.streamOutput is truthy): one JSON Feature has been written for each row in table.rows; each call used newline=True when invoking dump_json.
  - If non-streaming: one JSON object representing a FeatureCollection (an OrderedDict returned by GeoJsonGenerator.generate_feature_collection) has been written.
  - No CSVJSON instance attributes are changed.

## Side Effects:
- Writes to the configured output stream (self.output_file) via self.dump_json / json.dump.
- May write newline characters to the output when streaming.
- No network or external services are contacted by this method itself, but called routines may raise due to file I/O or JSON decoding.

### `csvkit.utilities.csvjson.CSVJSON.streaming_output_ndjson` · *method*

## Summary:
Stream the input CSV as newline-delimited JSON records by reading the header row as keys and emitting one JSON object per subsequent CSV row; missing fields are emitted as null.

## Description:
This method implements the streaming NDJSON (newline-delimited JSON) output mode for the CSV-to-JSON conversion utility. It reads CSV data from the object's input file stream, interprets the first CSV row as the list of column names, then iterates the remaining rows and emits one ordered JSON record per CSV row by delegating serialization/output to the object's dump_json method.

Known callers and context:
- Intended to be invoked by the CSV-to-JSON execution flow when NDJSON output is required; typical usage is during the main run/execute stage of the utility where one of several streaming output methods is selected based on command-line options or configuration.
- This method is part of the streaming/output stage of the utility pipeline: it consumes CSV input and produces a sequence of JSON outputs.

Why this is a separate method:
- The logic is a discrete, reusable streaming mode that reads headers and produces one output record at a time; separating it keeps the run/execution logic cleaner and allows reuse or direct testing of the NDJSON streaming behavior without inlining I/O or header-handling details in higher-level control flow.

## Args:
This method is an instance method and takes no explicit parameters. It reads the following attributes from self:
- self.input_file (file-like object): Required. A readable file-like object positioned to the start of CSV content (text mode with newline handling suitable for CSV parsing). It is passed to agate.csv.reader.
- self.reader_kwargs (dict): Optional. Keyword arguments forwarded to agate.csv.reader to control CSV parsing (e.g., delimiter, quotechar). Must be a mapping acceptable by agate.csv.reader.

## Returns:
- None
- Primary observable result: the method produces side-effect output by calling self.dump_json repeatedly; it does not return a value.

## Raises:
- StopIteration: If the CSV input contains no rows (i.e., agate.csv.reader yields nothing), the call to next(rows) will raise StopIteration. This indicates an empty input stream (no header row).
- Any exception raised by agate.csv.reader (e.g., CSV parsing errors) will propagate.
- Any exception raised by self.dump_json will propagate. The method does not catch exceptions from dump_json.
- The method handles IndexError internally for missing fields in a data row (see behavior below) and therefore does not raise IndexError for rows shorter than the header.

## Behavior and edge cases:
- Header handling: The first row produced by agate.csv.reader is consumed as the header row and used as the ordered list of column names.
- Missing fields: If a data row is shorter than the header (i.e., a column index is out of range), the corresponding key is set to None (which serializes to JSON null).
- Extra fields: If a data row has more fields than there are column names, those extra fields are ignored because the code enumerates over the header columns only.
- Record ordering: Each emitted JSON object preserves the order of column names using an OrderedDict, ensuring predictable key order in output if the serializer respects insertion order.
- Output newline: dump_json is invoked with newline=True so each JSON object is expected to be followed by a newline (producing NDJSON). The exact formatting (spacing, separators) depends on the implementation of dump_json.

## State Changes:
Attributes READ:
- self.input_file
- self.reader_kwargs
- self.dump_json (method reference invoked; treated as read)

Attributes WRITTEN:
- None: this method does not set or mutate attributes on self.

## Constraints:
Preconditions:
- self.input_file must be a readable file-like object containing CSV-formatted data.
- The CSV input must contain at least one row to serve as the header, otherwise StopIteration will be raised.
- self.reader_kwargs (if present) must be valid arguments for agate.csv.reader.

Postconditions:
- All rows from the input iterator (after the header) will have been consumed (or until an exception occurs).
- For every consumed data row, dump_json will have been called exactly once with an OrderedDict mapping header names to field values (or None for missing fields) and newline=True.

## Side Effects:
- I/O: The method reads from self.input_file via agate.csv.reader.
- Output: Calls self.dump_json(data, newline=True) for each record; dump_json is responsible for serializing the OrderedDict to JSON and writing it to the configured output stream (e.g., stdout or a file). Any side effects of dump_json (I/O, buffering, flushing) are incurred here.
- No other external services or global state are modified by this method.

### `csvkit.utilities.csvjson.CSVJSON.streaming_output_ndgeojson` · *method*

## Summary:
Read CSV rows from the configured input stream and stream each row as a newline-delimited GeoJSON Feature by delegating row→Feature conversion to the GeoJsonGenerator and writing JSON using the utility's dump_json method.

## Description:
- Known callers and context:
    - CSVJSON.main: invoked when streaming mode is enabled (can_stream() is True) and geometric output is requested (is_geo() is True). This method implements the newline-delimited GeoJSON (ND-GeoJSON) streaming output pipeline.
    - CSVJSON.output_geojson indirectly implements a similar per-row streaming path for table-based streaming; streaming_output_ndgeojson is used when the code prefers a low-memory streaming CSV reader rather than building an agate.Table first.
- Lifecycle stage:
    - This method runs during the output-generation stage of the CLI: after arguments are parsed and streaming mode is selected, it reads the CSV header and then processes each subsequent CSV row, emitting one GeoJSON Feature per input row.
- Why it's a separate method:
    - Keeps streaming CSV read logic separate from non-streaming FeatureCollection assembly.
    - Minimizes memory usage by avoiding creation of a full table or in-memory FeatureCollection.
    - Encapsulates the streaming-specific loop and integration with GeoJsonGenerator and dump_json so other output paths remain simple and focused.

## Args:
    None (instance method). It uses configuration and streams available on self.

## Returns:
    None.
    - The method does not return a value; its effect is writing newline-delimited GeoJSON Feature objects to self.output_file via self.dump_json(..., newline=True).
    - There is no per-row return value; control flows back to the caller after all rows are processed or an exception occurs.

## Raises:
    This method does not raise new, bespoke exceptions itself but allows several exceptions to propagate from the operations it performs:
    - StopIteration: If the input CSV stream is empty (no header row), next(rows) will raise StopIteration.
    - Any exception raised by agate.csv.reader when initializing the CSV iterator (e.g., I/O errors from self.input_file).
    - Exceptions raised during GeoJsonGenerator construction:
        - Any exception propagated by match_column_identifier when resolving column identifiers (type depends on match_column_identifier).
    - Exceptions raised per-row while building features:
        - IndexError or TypeError: if a row is not indexable or is shorter than expected, accesses inside GeoJsonGenerator.feature_for_row or geometry_for_row may raise these.
        - json.JSONDecodeError (subclass of ValueError): if a geometry column is configured and the cell contains invalid JSON; this propagates from json.loads inside GeoJsonGenerator.geometry_for_row.
        - ValueError during float conversion is caught inside geometry_for_row (it sets lon/lat to None), but downstream geometry absence may occur.
    - Exceptions raised by dump_json:
        - TypeError: if a feature contains non-serializable objects and the fallback serializer does not handle them.
        - OSError / IOError (e.g., BrokenPipeError) or other I/O errors when writing to self.output_file.
    - All such exceptions are propagated to the caller; the method does not swallow them.

## State Changes:
- Attributes READ:
    - self.input_file: file-like object used as the CSV source (passed to agate.csv.reader).
    - self.reader_kwargs: keyword arguments passed to agate.csv.reader (dialect/encoding/other reader options).
    - self.args: parsed CLI arguments used to configure GeoJsonGenerator (lat/lon keys, geometry/type/key flags, no_bbox/crs, zero_based, etc.).
    - self.GeoJsonGenerator: inner class used to convert a CSV row into a GeoJSON Feature (constructor invoked here).
    - self.dump_json: method invoked to serialize and write each generated Feature to self.output_file.
- Attributes WRITTEN:
    - None. This method does not mutate attributes on self.

## Constraints:
- Preconditions (must hold before calling):
    - This method is intended to be called only when streaming is enabled and GeoJSON output is requested (CSVJSON.main enforces these conditions). Practically:
        - self.args.lat and self.args.lon should be provided (is_geo() is True).
        - self.input_file must be a readable file-like object positioned at the start of CSV text (or at the next unread header row).
        - self.reader_kwargs must be a mapping of valid agate.csv.reader options.
        - The CSV must contain a header row as the first record (the method reads the first line as column_names via next(rows)).
    - The header row returned by next(rows) must be iterable of column names compatible with GeoJsonGenerator column resolution.
- Postconditions (guarantees after successful completion):
    - For each input data row after the header, the method will have called self.dump_json(feature, newline=True) exactly once, where feature is the OrderedDict returned by GeoJsonGenerator.feature_for_row(row).
    - No attributes of self are modified.
    - If the input stream is fully processed without exceptions, all GeoJSON Feature objects for rows have been written to self.output_file (subject to buffering and successful writes).

## Side Effects:
- I/O: Writes newline-delimited JSON objects to self.output_file via self.dump_json (commonly stdout or another file). Each call writes a JSON representation of a single GeoJSON Feature followed by a newline.
- Resource use: Uses a streaming CSV reader (agate.csv.reader) and processes rows one-at-a-time to avoid holding the entire dataset in memory.
- Error propagation: Any exception from CSV reading, column resolution, feature generation, JSON decoding, or writing will propagate out of the method to the caller — there is no internal error-handling or retry logic.
- No external network calls or global state modifications are performed.

## `csvkit.utilities.csvjson.GeoJsonGenerator` · *class*

## Summary:
Converts tabular rows (e.g., from an agate.Table) into a GeoJSON FeatureCollection represented as an OrderedDict, mapping specified CSV columns to feature geometries, properties, and ids, and optionally computing a bbox and including a CRS entry.

## Description:
GeoJsonGenerator centralizes the logic for transforming CSV-like rows into GeoJSON Feature objects and assembling them into a FeatureCollection. It is intended to be instantiated by a CSV-to-GeoJSON converter or CLI utility after parsing command-line arguments and before serializing the resulting mapping to JSON. Responsibilities:
- Resolve column identifiers (names or indices) to integer column indices.
- Convert each row into an OrderedDict Feature with 'type', 'properties', optional 'id', and 'geometry'.
- Aggregate features into a FeatureCollection OrderedDict, optionally compute bbox and append a CRS mapping.

It does not handle CSV parsing, JSON serialization, or file I/O — it returns Python OrderedDict/list structures that callers may pass to json.dumps or similar.

## State:
Constructor parameters:
- args (object)
  - Required attributes:
    - lat: column identifier (name or index) for latitude (passed to match_column_identifier)
    - lon: column identifier (name or index) for longitude
    - zero_based: bool; passed to match_column_identifier to control index interpretation
  - Optional attributes:
    - type: column identifier to be excluded from properties (if provided)
    - geometry: column identifier that contains a JSON-encoded geometry string (if provided)
    - key: column identifier used as Feature.id (if provided)
    - no_bbox: bool; when truthy, suppress computing and including a top-level bbox
    - crs: string; when truthy, include a 'crs' OrderedDict in the output
- column_names (list[str])
  - Ordered list of column header names corresponding to table rows.

Attributes established by __init__:
- self.args (object): the same args object passed in.
- self.column_names (list[str]): the same column_names list passed in.
- self.lat_column (int | None): integer index resolved for args.lat via match_column_identifier.
- self.lon_column (int | None): integer index resolved for args.lon.
- self.type_column (int | None): index resolved for args.type if args.type is truthy, else None.
- self.geometry_column (int | None): index for args.geometry if provided, else None.
- self.id_column (int | None): index for args.key if provided, else None.

Inner class (GeoJsonBounds) state:
- min_lon, min_lat, max_lon, max_lat (float | None): bounding box accumulators; None indicates not yet set.

Invariants:
- The index attributes (lat_column, lon_column, type_column, geometry_column, id_column) are either integers (as returned by match_column_identifier) or None. The generator assumes that these indices correspond to positions in rows it receives later; index validity relative to a particular table is the caller's responsibility.

## Lifecycle:
Creation:
- Call GeoJsonGenerator(args, column_names).
  - The constructor resolves column identifiers to indices immediately (calls match_column_identifier for lat and lon unconditionally; type/geometry/key only if corresponding args attribute is truthy).
Usage:
- Primary API: generate_feature_collection(table)
  - table must provide a .rows iterable; each row must be indexable by integer (row[i]) with positions matching column_names.
  - Typical sequence:
    1. Instantiate generator = GeoJsonGenerator(args, column_names)
    2. collection = generator.generate_feature_collection(table)
    3. Serialize: json.dumps(collection) or similar
- Helper/private methods:
  - feature_for_row(row): builds a single Feature OrderedDict from a row.
  - geometry_for_row(row): returns a geometry OrderedDict (Point) or loads a JSON-encoded geometry string, or returns None.
  - GeoJsonBounds methods (add_feature, update_coordinates, update_lon/lat, bbox) are used when bbox computation is enabled.
Destruction:
- No explicit cleanup required.

## Method Map:
graph LR
    A[generate_feature_collection(table)] --> B[feature_for_row(row)]
    B --> C[geometry_for_row(row)]
    A --> D[GeoJsonBounds.__init__]
    A --> E[GeoJsonBounds.add_feature(feature)]
    E --> F[GeoJsonBounds.update_coordinates(coordinates)]
    F --> G[GeoJsonBounds.update_lon(lon)]
    F --> H[GeoJsonBounds.update_lat(lat)]

## Methods and detailed behavior:

__init__(args, column_names)
- Purpose: store configuration and resolve column identifiers to integer indices via match_column_identifier.
- Side effects: calls match_column_identifier for args.lat and args.lon unconditionally; calls it for args.type, args.geometry, args.key only when those args attributes are truthy.
- Errors: any exception raised by match_column_identifier will propagate to the caller.

generate_feature_collection(table) -> OrderedDict
- Iterates table.rows and for each row:
  - Constructs a Feature OrderedDict by calling feature_for_row(row).
  - If args.no_bbox is falsy, calls bounds.add_feature(feature) to accumulate bbox.
  - Appends Feature into a features list.
- Builds an OrderedDict with entries in this order:
  - ('type', 'FeatureCollection') always present.
  - ('bbox', [min_lon, min_lat, max_lon, max_lat]) inserted at index 1 if args.no_bbox is falsy (i.e., bbox computed).
  - ('features', features) where features is the list of feature OrderedDicts.
  - ('crs', OrderedDict({'type':'name','properties':{'name': args.crs}})) appended if args.crs is truthy.
- Return type: collections.OrderedDict
- Notes:
  - If bbox was requested but no numeric coordinates were discovered, bbox entries may be None.

feature_for_row(row) -> OrderedDict (Feature)
- Creates feature = OrderedDict([('type','Feature'), ('properties', OrderedDict())])
- For each cell c at index i (enumerate(row)):
  - Skip the cell entirely if c is None OR i equals any of (type_column, lat_column, lon_column, geometry_column).
  - If i == id_column: set feature['id'] = c
  - Else, if c is truthy (Python truthiness), set feature['properties'][column_names[i]] = c
    - This excludes falsy values such as 0, 0.0, '', False from properties.
- Calls geometry_for_row(row) and sets feature['geometry'] to its return value (which may be None).
- Returns the constructed feature OrderedDict.

geometry_for_row(row) -> OrderedDict | None
- If geometry_column is not None:
  - Returns json.loads(row[self.geometry_column]).
  - json.loads exceptions (e.g., JSONDecodeError) will propagate to the caller.
- Else, if both lat_column and lon_column are not None:
  - Attempts to convert row[lon_column] and row[lat_column] to float inside a try/except ValueError block.
    - If conversion raises ValueError, lon and lat are set to None.
  - If both lon and lat are truthy (i.e., neither is None and both evaluate True), returns OrderedDict([('type','Point'), ('coordinates', [lon, lat])]).
    - Note: numeric zeros (0 or 0.0) evaluate as falsy in Python and therefore will prevent a Point geometry from being created.
- If no geometry could be produced, returns None.

GeoJsonBounds
- add_feature(feature):
  - If feature contains a 'geometry' key and that geometry contains 'coordinates', calls update_coordinates on that coordinates value.
- update_coordinates(coordinates):
  - If coordinates appears to be a single position (len(coordinates) <= 3 and isinstance(coordinates[0], (float, int))), treat coordinates as [lon, lat, ...] and call update_lon(coordinates[0]) and update_lat(coordinates[1]).
  - Otherwise, assume coordinates is an iterable of coordinate sequences and recurse into each item.
  - This supports nested coordinate arrays used by multi-part geometries.
- update_lon/update_lat update the min/max accumulators.
- bbox() returns [min_lon, min_lat, max_lon, max_lat] (values may be None if no numeric coordinates seen).

## Raises:
- __init__: any exception raised by match_column_identifier while resolving column identifiers will propagate (type depends on match_column_identifier).
- geometry_for_row: if geometry_column is set and the cell contains invalid JSON, json.loads will raise a JSONDecodeError (subclass of ValueError) and this will propagate to the caller.
- generate_feature_collection / feature_for_row: may propagate IndexError or TypeError if provided table.rows contains rows that are not indexable or whose length does not match column_names.

## Example (minimal, concrete):
# Prepare an args-like object (argparse.Namespace or types.SimpleNamespace)
from types import SimpleNamespace
args = SimpleNamespace(
    lat='latitude',
    lon='longitude',
    type=None,
    geometry=None,
    key='id',
    zero_based=False,
    no_bbox=False,
    crs=None,
)

# Column headers order
column_names = ['id', 'name', 'latitude', 'longitude']

# Table-like object with a .rows iterable (list of lists works)
class TableLike:
    def __init__(self, rows):
        self.rows = rows

rows = [
    ['1', 'Point A', '34.05', '-118.25'],
    ['2', 'Point B', '40.71', '-74.00'],
]
table = TableLike(rows)

# Instantiate and generate
generator = GeoJsonGenerator(args, column_names)
collection = generator.generate_feature_collection(table)

# Serialize to JSON text
import json
json_text = json.dumps(collection)

# After this, json_text contains a FeatureCollection mapping. Note:
# - Each feature will have 'type', 'properties' (with 'name'), 'id', and 'geometry' (Point) keys.
# - Bbox will be present if args.no_bbox is False and numeric coordinates were found.

### `csvkit.utilities.csvjson.GeoJsonGenerator.__init__` · *method*

## Summary:
Set up GeoJSON column mappings by storing provided arguments and resolving user-specified column identifiers into 0-based integer column indices on the instance.

## Description:
This initializer runs when a GeoJsonGenerator instance is created (typically right after CLI argument parsing and reading the CSV header). It captures the provided args and column_names references and resolves the following CLI-provided identifiers to normalized 0-based column indices using match_column_identifier: latitude, longitude, and the optionally supplied type, geometry, and key columns.

By resolving identifiers once during initialization, downstream methods can rely on integer indices (or None) instead of re-parsing user input repeatedly. This separation centralizes validation/error messages (delegated to match_column_identifier) and keeps subsequent logic concise and index-based.

Known callers / typical context:
- Constructed by the csvjson CLI utility or other code that converts CSV rows to GeoJSON features after parsing CLI options and reading the header row. Called during the setup/configuration stage of the CSV → GeoJSON pipeline.

Why this is a separate method:
- Initialization centralizes resolution of user column identifiers and makes the object's state (which columns correspond to lat/lon/etc.) explicit and immutable for the generator's lifetime. Delegating parsing/validation to match_column_identifier keeps consistent error messages and avoids duplicating parsing logic.

## Args:
    args (object):
        An object (commonly argparse.Namespace) that must expose the following attributes:
        - lat (str | int): Identifier for the latitude column. Must be provided.
        - lon (str | int): Identifier for the longitude column. Must be provided.
        - type (str | int | falsy): Optional identifier for a feature type column. If truthy, it will be resolved to an integer index; if falsy (e.g., None, ''), the instance attribute will be set to None.
        - geometry (str | int | falsy): Optional identifier for a geometry column. Same handling as type.
        - key (str | int | falsy): Optional identifier for a feature id/key column. Same handling as type.
        - zero_based (int): Column offset passed to match_column_identifier. Must be an integer specifying how numeric identifiers are interpreted (common values: 1 for 1-based user input, 0 for 0-based input). This value is forwarded directly to match_column_identifier as its column_offset parameter.
        Note: All attributes accessed here (lat, lon, type, geometry, key, zero_based) must exist on args; missing attributes will raise AttributeError on access.

    column_names (Sequence[str]):
        Ordered, indexable sequence of column header names (e.g., list or tuple of strings). Must support membership testing, indexing, and len(). For deterministic ColumnIdentifierError behavior on numeric out-of-range errors, column_names should be non-empty.

## Returns:
    None
    The method initializes instance attributes and does not return a value.

## Raises:
    ColumnIdentifierError:
        Propagated from match_column_identifier when any resolved identifier (lat, lon, or an optional identifier when present and truthy) is invalid. Conditions and exact error messages are defined by match_column_identifier:
        - Non-matching non-digit string or unparsable numeric string -> "Column '%s' is invalid. It is neither an integer nor a column name. Column names are: %s"
        - Numeric value less than minimum allowed -> "Column %i is invalid. Columns are 1-based."
        - Numeric value greater than maximum allowed -> "Column %i is invalid. The last column is '%s' at index %i."
    IndexError:
        May be raised indirectly if column_names is empty and match_column_identifier attempts to reference column_names[-1] while composing an out-of-range error message.
    AttributeError:
        If args does not provide any of the attributes accessed here (lat, lon, type, geometry, key, zero_based), attribute access will raise AttributeError.

## State Changes:
    Attributes READ:
        - self.args (reads attributes: lat, lon, type, geometry, key, zero_based)
        - self.column_names (read to pass into match_column_identifier)

    Attributes WRITTEN:
        - self.args: stores the provided args reference
        - self.column_names: stores the provided column_names reference
        - self.lat_column: int (0-based index) resolved from args.lat via match_column_identifier
        - self.lon_column: int (0-based index) resolved from args.lon via match_column_identifier
        - self.type_column: int (0-based index) if args.type is truthy and resolved; otherwise None
        - self.geometry_column: int (0-based index) if args.geometry is truthy and resolved; otherwise None
        - self.id_column: int (0-based index) if args.key is truthy and resolved; otherwise None

## Constraints:
    Preconditions:
        - column_names must be an ordered, indexable sequence of strings. For predictable ColumnIdentifierError messages on numeric out-of-range inputs, column_names should be non-empty.
        - args must provide the attributes accessed here (lat, lon, zero_based at minimum).
        - args.zero_based must be an integer appropriate for match_column_identifier (commonly 0 or 1).
        - Identifiers supplied via args (lat, lon, type, geometry, key) must be either valid names present in column_names or numeric identifiers valid under the provided zero_based offset.

    Postconditions:
        - If initialization completes without raising:
            * self.lat_column and self.lon_column are integers satisfying 0 <= index < len(column_names).
            * self.type_column, self.geometry_column, self.id_column are either integers in the same valid range (when the corresponding args attribute was truthy) or None (when falsy).
            * self.args and self.column_names references are stored unchanged.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of inputs beyond storing references on self.
    - Exceptions from match_column_identifier (ColumnIdentifierError or IndexError) or AttributeError from missing args attributes will propagate to the caller; no exception handling occurs inside the initializer.

## Behavior Notes and Edge Cases:
    - Optional identifiers (type, geometry, key) are only resolved when their args attribute is truthy; when falsy they are set to None.
    - lat and lon are always resolved; invalid lat/lon identifiers cause initialization to fail with ColumnIdentifierError (or IndexError in the empty-header edge case).
    - This initializer does not validate consistency between resolved columns (for example, it does not check that lat and lon are distinct). Such validation, if needed, must be performed by the caller or by later methods.
    - The initializer stores references to the original args and column_names objects (no defensive copies).

### `csvkit.utilities.csvjson.GeoJsonGenerator.generate_feature_collection` · *method*

## Summary:
Builds and returns an OrderedDict representing a GeoJSON FeatureCollection from the provided table. The method does not modify the GeoJsonGenerator instance; it creates and mutates a transient GeoJsonBounds helper when computing an optional bbox.

## Description:
- Known callers and invocation context:
    - Called during a CSV-to-GeoJSON conversion step after an input table has been parsed. Typical pipeline: parse CSV → obtain an agate.Table (or similar table-like object) → call this method to produce a FeatureCollection mapping ready for JSON serialization.
    - Consumers: higher-level csvjson utility code (or any code that needs a FeatureCollection object) that will serialize or stream the returned OrderedDict.
- Why this is a separate method:
    - Separates collection-level responsibilities (iterating rows, aggregating per-row features, optionally computing and inserting a global bbox, and appending CRS metadata) from per-row logic (feature_for_row) and geometry parsing (geometry_for_row). This improves readability, testability, and reuse: per-row conversion and geometry parsing can be implemented and tested independently.

## Args:
    table (object with attribute `rows`):
        - Required. Must have an attribute named `rows` that is an iterable of row objects/values (e.g., agate.Table). Each element from `table.rows` is passed to self.feature_for_row(row).
        - No implicit conversion is performed; any object satisfying the `.rows` iterable contract is acceptable.

## Returns:
    collections.OrderedDict:
        - The returned OrderedDict contains at least these entries (in insertion order):
            1. 'type': the string 'FeatureCollection'
            2. 'features': a list of feature objects returned by self.feature_for_row(row), in the same order as iteration over table.rows
        - Additional optional entries:
            - 'bbox' (list) — inserted immediately after 'type' (i.e., at index 1) when self.args.no_bbox is falsy. Value is the result of a transient GeoJsonBounds.bbox(): [min_lon, min_lat, max_lon, max_lat]. Any element may be None if no numeric coordinates were observed for that axis.
            - 'crs' (OrderedDict) — appended at the end when self.args.crs is truthy. Structure:
                OrderedDict([('type', 'name'), ('properties', {'name': self.args.crs})])
        - Important detail: the 'features' list contains the exact feature objects returned by self.feature_for_row(row); no deep copies are made.

## Raises:
    - AttributeError:
        - If `table` does not have a `rows` attribute, attempting to access table.rows will raise AttributeError.
    - TypeError:
        - If `table.rows` exists but is not iterable, iterating it will raise TypeError.
        - May also be raised indirectly if bounds.add_feature(feature) or GeoJsonBounds methods encounter invalid types (for example, feature['geometry'] is None and membership/indexing on it is attempted).
    - IndexError:
        - Propagated from self.feature_for_row(row) or geometry_for_row(row) when they index into `row` or self.column_names with an out-of-range index.
    - json.JSONDecodeError or ValueError:
        - Propagated from geometry_for_row(row) if a configured geometry column contains invalid JSON (json.loads raises these).
    - Any exception raised by self.feature_for_row(row) or GeoJsonBounds methods will propagate unchanged. This method does not catch or convert exceptions raised during per-row processing or bounds computation.

## State Changes:
- Attributes READ:
    - self.args.no_bbox (checked to decide whether to compute and include 'bbox')
    - self.args.crs (checked to decide whether to append 'crs')
    - self.feature_for_row (method invoked for each row)
    - self.GeoJsonBounds (nested class referenced and instantiated)
    - Indirect reads (via feature_for_row / geometry_for_row): self.column_names, self.type_column, self.lat_column, self.lon_column, self.geometry_column, self.id_column
- Attributes WRITTEN:
    - None. No persistent attributes on self are modified by this method. Only the transient GeoJsonBounds instance is mutated.

## Constraints:
- Preconditions:
    - The GeoJsonGenerator instance (self) must be properly initialized (its __init__ has run) so that feature_for_row and geometry_for_row can operate (configured column index attributes and self.args.* exist).
    - `table` must expose a `.rows` iterable producing rows compatible with self.feature_for_row. Rows should provide values at indices referenced by configured column indices.
    - If a meaningful numeric bbox is required, per-row geometries must contain numeric coordinates (longitude and latitude). If no numeric coordinates are encountered, bbox() will return components that can be None.
- Postconditions:
    - The returned OrderedDict contains 'type' and 'features' keys always.
    - If self.args.no_bbox is falsy, the returned mapping also contains 'bbox' at position index 1 with the current GeoJsonBounds.bbox() value (possibly containing None elements).
    - If self.args.crs is truthy, the returned mapping contains a 'crs' OrderedDict as described above.
    - No attributes of self are mutated by this call.

## Side Effects:
    - Instantiates a GeoJsonBounds object and calls its mutator methods (add_feature/update_coordinates/update_lon/update_lat) for features when computing bbox (only if self.args.no_bbox is falsy). Those mutations are confined to the transient bounds instance.
    - Calls self.feature_for_row(row) for each row. feature_for_row may call geometry_for_row, which performs json.loads and float() conversions (CPU work and possible exceptions) but does not perform external I/O.
    - No file, network, or stdout/stderr I/O is performed by this method.

## Example usage (prose):
- After parsing a CSV into an agate.Table named T and constructing a GeoJsonGenerator instance G configured with lat/lon/geometry/id flags:
    - Calling G.generate_feature_collection(T) returns an OrderedDict suitable for json serialization.
    - If G.args.no_bbox is False and numeric coordinates are present, the returned mapping includes a 'bbox' entry [min_lon, min_lat, max_lon, max_lat].
    - If G.args.crs is set to a non-empty string, the returned mapping includes a 'crs' dictionary describing the coordinate reference system.

### `csvkit.utilities.csvjson.GeoJsonGenerator.feature_for_row` · *method*

## Summary:
Constructs and returns an OrderedDict representing a GeoJSON Feature for the given row; the method only reads generator configuration and row values and does not modify the generator's state.

## Description:
Called by generate_feature_collection for each table row during FeatureCollection construction. For each row it:
- Creates a Feature skeleton with 'type' == 'Feature' and an empty OrderedDict under 'properties'.
- Iterates row values by index and index/value pairs to decide whether to skip a value, assign it as the Feature 'id', or add it to 'properties'.
- Delegates geometry creation to self.geometry_for_row(row) and assigns its result to the 'geometry' key.

This logic is separate to isolate per-row mapping rules (reserved column filtering, id selection, property inclusion) and to allow geometry parsing/creation to be implemented and tested independently in geometry_for_row.

## Known callers / pipeline stage:
- generate_feature_collection: invoked once per row when assembling the FeatureCollection.

## Args:
    row (iterable / indexable): A sequence-like container of column values (e.g., list, tuple, agate.Row). The method uses enumerate(row) and may index into self.column_names using the same indices, so row must be iterable and index positions must correspond to entries in self.column_names.

## Returns:
    collections.OrderedDict with these guaranteed keys:
        - 'type' (str): The literal 'Feature'.
        - 'properties' (collections.OrderedDict): Ordered mapping of column name -> value for included properties. Entries are added in increasing column index order as encountered during enumeration; later columns with the same column name overwrite earlier entries.
        - 'geometry': The direct return value of self.geometry_for_row(row) (always present as a key). Possible values:
            * OrderedDict geometry object (e.g., {'type': 'Point', 'coordinates': [lon, lat]}) when geometry_for_row constructs one.
            * None when geometry_for_row determines there is no valid geometry (e.g., missing or unparsable lat/lon, and no geometry column provided).
        - 'id' (optional): Present only when the current index equals self.id_column and the value at that index is not None and was not skipped due to reserved-column filtering.

    Specific behaviors:
        - The 'geometry' key is always present in the returned OrderedDict; its value may be None.
        - The 'properties' mapping only receives a column's value when:
            * the value is not None,
            * the column index is not one of the reserved indices (self.type_column, self.lat_column, self.lon_column, self.geometry_column),
            * and the value is truthy (Python bool(value) is True). Values that are falsy but not None (e.g., 0, '', False) are therefore NOT added as properties.
        - The 'id' key is assigned if and only if:
            * the column index equals self.id_column,
            * the value at that index is not None,
            * and the index was not skipped due to being a reserved column (skip happens before id check).

## Raises:
    IndexError:
        - If during property insertion the code attempts to access self.column_names[i] but self.column_names has no entry at index i.
        - If geometry_for_row attempts to index row at self.geometry_column and that index is out of bounds, the resulting IndexError will propagate.

    json.JSONDecodeError (or ValueError from json.loads):
        - May be raised by geometry_for_row when a geometry column is configured and contains invalid JSON; this method does not catch such exceptions and they will propagate.

    Any other exception raised by self.geometry_for_row(row) will propagate unchanged.

## State Changes:
    Attributes READ:
        - self.type_column
        - self.lat_column
        - self.lon_column
        - self.geometry_column
        - self.id_column
        - self.column_names
        - calls self.geometry_for_row(row) (which may read additional self state)

    Attributes WRITTEN:
        - None. No self.* attributes are modified.

## Constraints:
    Preconditions:
        - self.column_names is an indexable sequence with indices aligned to positions in row.
        - Configured index attributes (self.type_column, self.lat_column, self.lon_column, self.geometry_column, self.id_column) are either None or integer indices intended for use with row and self.column_names.
        - row must be iterable and provide values for indices up to the maximum index that will be enumerated (enumeration uses len(row) implicitly); however, missing column_names entries for enumerated indices will cause IndexError when adding properties.

    Postconditions:
        - The returned OrderedDict always contains keys 'type', 'properties', and 'geometry'; 'id' may be present per the rules above.
        - No mutation to self or to the input row occurs.

## Side Effects:
    - Calls self.geometry_for_row(row), which may perform JSON parsing (json.loads) and float conversions; geometry_for_row handles float parsing failures by returning no geometry but does not catch JSON parse errors.
    - No I/O (files, network, stdout/stderr) or external service calls are performed by this method.
    - Does not mutate the input row.

### `csvkit.utilities.csvjson.GeoJsonGenerator.geometry_for_row` · *method*

## Summary:
Returns a GeoJSON geometry object for a single CSV row based on configured geometry, latitude, and longitude columns. Does not modify object state; it either returns a parsed geometry structure or None when no valid geometry can be produced.

## Description:
This method produces the geometry for one row during the CSV-to-GeoJSON conversion pipeline. Typical usage is inside the GeoJsonGenerator's per-row feature construction step: for each row it is called to obtain that row's geometry, which is then embedded into a GeoJSON Feature.

This logic is separated into its own method so the geometry-determination rules (use explicit geometry column if present, otherwise construct a Point from lat/lon) are centralized and reusable, and so callers can treat geometry production as a single unit that can be tested or overridden independently.

Known invocation context:
- Called by the GeoJsonGenerator feature-building pipeline (i.e., when converting each CSV row into a GeoJSON Feature).

## Args:
    row (sequence|mapping): Row data indexed by column identifier. The method indexes into row using self.geometry_column, self.lon_column and self.lat_column. The row must support indexing with those values (for example, a dict keyed by column names or a sequence accessed by column indices). Values read from the row are expected to be strings (for json.loads) or values convertible to float (for lat/lon).

## Returns:
    dict | OrderedDict | None:
    - If self.geometry_column is not None: returns the Python object produced by json.loads(row[self.geometry_column]) — typically a dict or list that represents a GeoJSON geometry (this is returned verbatim; it is not wrapped).
    - Else if both self.lat_column and self.lon_column are set and their values convert to floats and both evaluate truthily: returns an OrderedDict with the GeoJSON Point geometry:
        OrderedDict([('type', 'Point'), ('coordinates', [lon, lat])])
      where lon and lat are Python floats and coordinates are in [longitude, latitude] order per GeoJSON.
    - Otherwise: returns None (implicit) to indicate no geometry could be produced for this row.

Edge-case returns:
- If the geometry JSON string is invalid, json.loads will raise a JSONDecodeError (subclass of ValueError) and no return will occur.
- If row lookups fail (e.g., missing key or invalid index), a KeyError or IndexError may propagate.

## Raises:
    json.JSONDecodeError (ValueError subclass): If self.geometry_column is set and the cell value is not valid JSON, json.loads will raise this error and it propagates.
    KeyError / IndexError: If row cannot be indexed by the configured column identifier(s), indexing will raise these and they are not caught here.
    TypeError: If row is None or does not support indexing with the configured identifiers, indexing may raise TypeError.
    (Note: float() conversion errors for lat/lon are caught inside the method and will not propagate as exceptions.)

## State Changes:
    Attributes READ:
        - self.geometry_column
        - self.lat_column
        - self.lon_column
    Attributes WRITTEN:
        - None (this method does not modify any attributes on self)

## Constraints:
    Preconditions:
        - self.geometry_column, self.lat_column and self.lon_column should be set to valid column identifiers (None, integer index, or string key) appropriate for indexing into the passed row.
        - If self.geometry_column is used, the corresponding cell must contain a JSON string representing a GeoJSON geometry.
        - If lat/lon are used, their corresponding row values must be convertible to float.
    Postconditions:
        - If a geometry dict is returned, it will either be the parsed JSON object from the geometry column or an OrderedDict of the form:
            ('type': 'Point', 'coordinates': [lon (float), lat (float)])
        - If no valid geometry is available, the method returns None and does not alter object state.

Important behavioral note (constraint/edge case):
    - The method uses "if lon and lat" to decide whether to return a Point. This means that coordinates equal to 0.0 (zero latitude or longitude) are treated as falsy and will prevent a Point from being returned. As a result, valid coordinates at 0.0 are ignored by this implementation.

## Side Effects:
    - No I/O or external service calls.
    - Uses json.loads which may parse input strings and allocate Python objects.
    - May propagate exceptions from json.loads, indexing into row, or invalid row types as described in Raises.

## `csvkit.utilities.csvjson.GeoJsonBounds` · *class*

## Summary:
Represents and incrementally computes a geographic bounding box (min longitude, min latitude, max longitude, max latitude) from GeoJSON-like coordinate input.

## Description:
GeoJsonBounds is a small, stateful helper that accumulates geographic coordinate extrema found in GeoJSON Feature objects or raw coordinate arrays. Instantiate this class when you need to derive the bounding box for a collection of GeoJSON features or nested coordinate lists without pulling in a full spatial library.

Typical callers:
- CSV-to-GeoJSON converters or feature-processing loops that visit GeoJSON Feature dictionaries and want a global bounding box.
- Any code that processes GeoJSON geometries (Point, MultiPoint, LineString, Polygon, Multi* geometries) and needs to aggregate min/max longitude and latitude.

Motivation and responsibility:
- Encapsulates recursion over nested GeoJSON coordinate arrays and maintains four extrema values.
- Focused responsibility: walk coordinate lists and update extrema only. It does not validate full GeoJSON, perform coordinate normalization/projection, or compute area/centroid.

## State:
- min_lon: float | int | None
  - Current minimum longitude seen so far.
  - Starts as None; set to numeric value when the first longitude is processed.
  - Invariant: None (no coordinates seen) or a finite numeric value.

- min_lat: float | int | None
  - Current minimum latitude seen so far.
  - Starts as None; set to numeric value when the first latitude is processed.
  - Invariant: None or a finite numeric value.

- max_lon: float | int | None
  - Current maximum longitude seen so far.
  - Starts as None; updated as larger longitudes are observed.
  - Invariant: None or a finite numeric value.

- max_lat: float | int | None
  - Current maximum latitude seen so far.
  - Starts as None; updated as larger latitudes are observed.
  - Invariant: None or a finite numeric value.

Class invariants (intended to hold after processing any valid coordinate pair):
- If any extrema are not None, then min_lon <= max_lon and min_lat <= max_lat (after at least one valid coordinate has been processed, equality holds for single-point input).
- If no coordinates have been processed, all four attributes remain None.

Notes on types and values:
- Coordinates accepted are numeric (int or float). Integers are treated as numeric values.
- The attributes may remain None if no coordinates have been added; bbox() will return a list that can include None entries.

## Lifecycle:
Creation:
- Instantiate with no arguments. Example instantiation produces an object with all four attributes set to None.

Usage:
- Mutator methods update the instance in-place and return None. They do not create or return a new GeoJsonBounds object.
- Typical sequence:
  1. Call add_feature(feature) for GeoJSON Feature dictionaries, or call update_coordinates(coordinates) directly with coordinate arrays. Calls can be interleaved in any order.
  2. After one or more mutator calls, call bbox() to obtain the computed bounding box as a list.
- No destruction/cleanup is required: the object holds only numeric state and has no external resources.

## Method Map:
graph TD
    A[create GeoJsonBounds] --> B[add_feature(feature) : returns None (mutates)]
    A --> C[update_coordinates(coordinates) : returns None (mutates)]
    B --> C
    C --> D{len(coordinates) <= 3 and coordinates[0] is numeric?}
    D -->|yes| E[update_lon(lon) : returns None]
    D -->|yes| F[update_lat(lat) : returns None]
    D -->|no| C
    E --> G[(set min_lon/max_lon)]
    F --> H[(set min_lat/max_lat)]
    A --> I[bbox() : returns [min_lon, min_lat, max_lon, max_lat]]

## Methods (behavior summary and return values):
- __init__()
  - Initializes min_lon, min_lat, max_lon, max_lat to None.
  - Returns None (constructor behavior).

- bbox()
  - Returns: list [min_lon, min_lat, max_lon, max_lat]
  - Behavior:
    - If no coordinates have been processed, returns [None, None, None, None].
    - Does not modify the object's state.

- add_feature(feature)
  - Accepts: a mapping-like object expected to follow GeoJSON Feature conventions (i.e., a dict with 'geometry' key that itself is a mapping containing 'coordinates').
  - Behavior:
    - If 'geometry' is present in feature and 'coordinates' is present in feature['geometry'], passes feature['geometry']['coordinates'] to update_coordinates().
    - Performs in-place updates of extrema and returns None.
  - Error/edge cases:
    - If feature is not mapping-like, the 'in' checks or indexing may raise TypeError.
    - If feature['geometry'] is None, attempting to check 'coordinates' in feature['geometry'] will raise TypeError; the method does not catch this.
    - If required keys are absent, the method simply does nothing and returns None.

- update_coordinates(coordinates)
  - Accepts: a coordinate representation used in GeoJSON. Common forms:
    - Primitive point: [lon, lat] (a sequence with numeric first element).
    - Slightly extended point: [lon, lat, z] or any sequence of length <= 3 where index 0 is numeric (the method still uses only indices 0 and 1).
    - Nested collections: lists of points, lists of linear rings (for Polygons), or lists of lists for multi-geometries.
  - Behavior:
    - If coordinates is a sequence with length <= 3 and its first element is numeric (int or float), treat it as a primitive coordinate representation. Only the first two elements are used: coordinates[0] for longitude and coordinates[1] for latitude. Any third element (e.g., altitude) is ignored by this class.
    - Otherwise, assume coordinates is an iterable of sub-coordinate arrays and recurse: for each element in coordinates, call update_coordinates(element).
    - Performs in-place updates of extrema and returns None.
  - Error/edge cases:
    - IndexError if coordinates is an empty sequence (accessing coordinates[0] or coordinates[1] will fail).
    - TypeError if coordinates or its elements are not indexable or are of an unexpected non-iterable type (e.g., None or scalar).
    - The method intentionally does not remove duplicated closing vertices in polygon rings; duplicates simply do not change extrema.
    - The method does not validate numeric ranges (e.g., longitude bounds -180..180), so callers should normalize data if required.

- update_lon(lon)
  - Accepts: numeric lon (int or float).
  - Behavior:
    - If min_lon is None or lon < min_lon, set min_lon = lon.
    - If max_lon is None or lon > max_lon, set max_lon = lon.
    - Returns None.
  - Edge cases:
    - Comparisons with non-numeric types will raise TypeError.

- update_lat(lat)
  - Accepts: numeric lat (int or float).
  - Behavior:
    - If min_lat is None or lat < min_lat, set min_lat = lat.
    - If max_lat is None or lat > max_lat, set max_lat = lat.
    - Returns None.
  - Edge cases:
    - Comparisons with non-numeric types will raise TypeError.

## Raises:
- __init__(): does not raise.
- add_feature(feature):
  - May raise TypeError if feature is not mapping-like or if feature['geometry'] is None (attempting 'in' on None).
  - Does not raise a ValueError for missing geometry; it silently returns None when keys are absent.
- update_coordinates(coordinates):
  - IndexError if coordinates is an empty sequence or lacks index 0/1.
  - TypeError if coordinates or its elements are not indexable or are of unexpected types.
- update_lon/update_lat:
  - TypeError if non-numeric values are provided and comparisons fail.
- Mutator methods do not catch these exceptions; callers should validate inputs when necessary.

## Example (prose-only usage demonstration):
- Creation:
  - Instantiate GeoJsonBounds; min_lon/min_lat/max_lon/max_lat are all None.

- Add a Point feature:
  - Given a feature dict with 'geometry': {'coordinates': [lon, lat]}, call add_feature(feature). The object is mutated in-place (min/max values set) and the method returns None.

- Add a Polygon feature:
  - Given a feature dict whose geometry['coordinates'] is a nested list (list of linear rings, each a list of points), call add_feature(feature). update_coordinates will recurse into nested lists until it reaches primitive coordinate pairs and update extrema for every vertex encountered. The method returns None.

- Retrieve the bounding box:
  - Call bbox() at any time to obtain the current bounding box as [min_lon, min_lat, max_lon, max_lat].

- Error handling guidance:
  - For data that may include malformed features (e.g., geometry is None) or empty coordinate arrays, validate inputs before passing them to add_feature/update_coordinates or catch TypeError/IndexError around calls.

### `csvkit.utilities.csvjson.GeoJsonBounds.__init__` · *method*

## Summary:
Initializes an empty geographic bounding-box accumulator by setting the four extrema (min_lon, min_lat, max_lon, max_lat) to None, leaving the object in a ready-to-use state for subsequent incremental updates.

## Description:
- Known callers and context:
    - Instantiated by CSV-to-GeoJSON converters and feature-processing loops when computing a global bounding box for a collection of GeoJSON Features or raw coordinate arrays.
    - Typical lifecycle stage: creation occurs at the start of a bounding-box computation pipeline (before calling mutator methods such as add_feature or update_coordinates). The object is then updated incrementally as features/coordinates are processed.

- Why this is a separate method:
    - Separates object construction from bounding-box accumulation logic; __init__ only establishes the canonical empty state so subsequent mutator methods can assume and rely on a consistent initial state.
    - Keeping initialization minimal improves clarity and makes it safe to instantiate the object without performing any processing or I/O.

## Args:
    None

## Returns:
    None
    - As a constructor, it does not return a value; the instance is created and returned implicitly by Python object construction. The method itself returns None.

## Raises:
    None
    - The initializer does not raise any exceptions in normal execution.

## State Changes:
- Attributes READ:
    - None

- Attributes WRITTEN:
    - self.min_lon: set to None
    - self.min_lat: set to None
    - self.max_lon: set to None
    - self.max_lat: set to None

## Constraints:
- Preconditions:
    - None required. Safe to call only via normal Python instantiation; callers should not rely on any prior state.

- Postconditions:
    - After __init__ completes, all four extrema attributes are guaranteed to be None.
    - The object is in a valid initial state for accumulation: mutator methods (e.g., update_coordinates, add_feature, update_lon, update_lat) may be called and will update these attributes from None to numeric values as coordinates are processed.

## Side Effects:
    - No I/O, no network calls, and no mutation of objects outside self. Only the instance attributes listed under State Changes are modified.

### `csvkit.utilities.csvjson.GeoJsonBounds.bbox` · *method*

## Summary:
Return the current bounding box as a 4-element list [min_lon, min_lat, max_lon, max_lat], reflecting the effect of any prior updates to the instance's min/max latitude and longitude fields.

## Description:
Known callers and context:
- There are no internal callers to this method within the GeoJsonBounds class. Typical callers are external code that aggregates GeoJSON features (for example, a CSV-to-GeoJSON conversion pipeline) which:
  1. Create a GeoJsonBounds instance.
  2. Add features via add_feature or update_coordinates.
  3. Call this method to obtain the overall bounding box for the aggregated features.
- Lifecycle stage: invoked after features/coordinates have been processed and the caller needs a compact representation of the spatial extent (e.g., to populate a GeoJSON "bbox" property or for summarization).

Why this is a separate method:
- Encapsulates the ordering and extraction of four boundary values into a single, well-named accessor.
- Provides a single point to obtain the bbox in the canonical [min_lon, min_lat, max_lon, max_lat] ordering, improving readability and avoiding repeated inline list construction throughout the codebase.

## Args:
- None

## Returns:
- list
    - A 4-element list in the order [min_lon, min_lat, max_lon, max_lat].
    - Each element is the raw value stored on the instance (typically int or float) or None if no coordinate updates have occurred for that component.
    - Edge-case return: If no coordinates have been processed, this returns [None, None, None, None] (since all four attributes are initialized to None).

## Raises:
- None. The method performs no validation and does not raise exceptions.

## State Changes:
Attributes READ:
- self.min_lon
- self.min_lat
- self.max_lon
- self.max_lat

Attributes WRITTEN:
- None. This method does not modify any attributes.

## Constraints:
Preconditions:
- The object should be instantiated (i.e., __init__ has been called). There are no additional preconditions enforced by the method; the min/max attributes may be None or numeric.
- For meaningful numeric bbox values, callers must have invoked add_feature, update_coordinates, update_lat, or update_lon to populate the min/max fields with numeric values.

Postconditions:
- The returned list contains the current values of the instance's min/max lon/lat in the defined order.
- The instance's attributes remain unchanged by this call.

## Side Effects:
- None. The method performs no I/O, external calls, or mutations of objects outside self.

### `csvkit.utilities.csvjson.GeoJsonBounds.add_feature` · *method*

## Summary:
Integrates a single GeoJSON Feature's geometry coordinates into the instance bounding box, expanding the instance's min/max longitude and latitude fields when coordinates are present.

## Description:
- Known callers and invocation context:
    - Designed to be invoked once per GeoJSON Feature while processing a FeatureCollection or streaming GeoJSON input within csvjson utilities or similar pipelines. Typical lifecycle: create a GeoJsonBounds instance, call add_feature(feature) for each Feature to accumulate bounds, then call bbox() to retrieve [min_lon, min_lat, max_lon, max_lat].
- Why this is a separate method:
    - Encapsulates feature-level extraction (presence checks for 'geometry' and 'coordinates') and delegates recursive coordinate traversal to update_coordinates. This separation keeps feature handling distinct from numeric min/max logic and recursion, improving readability and reuse.

## Args:
    feature (mapping-like): A GeoJSON Feature-like mapping expected to contain:
        - 'geometry' (mapping-like): the geometry object.
        - feature['geometry']['coordinates'] (sequence): a nested sequence representing coordinates.
    Expected coordinate shape and semantics:
        - Coordinates use GeoJSON ordering where the first numeric element is longitude and the second numeric element is latitude (i.e., [lon, lat, ...]).
        - Point-like coordinate arrays are detected when the coordinates sequence has length <= 3 and its first element is numeric (float or int). An optional third element (altitude) is ignored.
        - Non-point geometries (LineString, Polygon, Multi*, etc.) are represented as nested sequences; update_coordinates will recurse into them.

## Returns:
    None — performs in-place updates to the GeoJsonBounds instance; no value is returned.

## Raises:
    - TypeError:
        - If feature is None or a non-container (e.g., int), the membership test "'geometry' in feature" may raise TypeError.
        - If feature['geometry'] exists but is not subscriptable by string keys (for example, an object that does not support indexing with 'coordinates'), accessing feature['geometry']['coordinates'] may raise TypeError.
    - IndexError:
        - If a sequence is treated as a point (len(coordinates) <= 3 and coordinates[0] is numeric) but has fewer than 2 elements, update_coordinates will attempt to access coordinates[1], causing IndexError.
    - RecursionError:
        - Extremely deep nesting in coordinates may exhaust Python recursion limits during recursive traversal in update_coordinates.
    - Note:
        - The method itself only performs membership checks and a single indexing into feature['geometry']; further validation and numeric checks occur in update_coordinates, so malformed coordinate structures may surface exceptions from deeper calls.

## State Changes:
- Attributes READ:
    - self.min_lon (read by update_lon for comparison)
    - self.max_lon (read by update_lon for comparison)
    - self.min_lat (read by update_lat for comparison)
    - self.max_lat (read by update_lat for comparison)
- Attributes WRITTEN:
    - self.min_lon
    - self.max_lon
    - self.min_lat
    - self.max_lat
    These attributes are updated indirectly via update_coordinates → update_lon/update_lat when point coordinates are encountered.

## Constraints:
- Preconditions:
    - feature must be a container that supports membership tests (so "'geometry' in feature" is valid).
    - If present, feature['geometry'] must support membership and indexing by the string key 'coordinates'.
    - Point-like coordinate sequences must contain at least two numeric elements (longitude and latitude) for valid min/max updates.
- Postconditions:
    - If feature contains a valid geometry with coordinates, the instance's min_lon/min_lat/max_lon/max_lat will be adjusted so the bounding box includes all point coordinates found within feature['geometry']['coordinates'].
    - If feature lacks a 'geometry' key or its geometry lacks 'coordinates' (as determined by the membership tests), the GeoJsonBounds instance is unchanged.
    - After processing one or more features via add_feature, calling bbox() returns the aggregated bounding box as [min_lon, min_lat, max_lon, max_lat], where any None values indicate that no numeric coordinates were encountered for that axis.

## Side Effects:
    - Mutates the GeoJsonBounds instance (min_lon, min_lat, max_lon, max_lat).
    - No file I/O or network access is performed.
    - update_coordinates is called and may recurse; excessive nesting can cause RecursionError.

## Usage (prose example):
    - Typical use: instantiate GeoJsonBounds, iterate a GeoJSON FeatureCollection and call add_feature(feature) for each feature, then call bbox() to obtain the final bounding box. If no features contained numeric coordinates, bbox() may return a list containing None values for axes with no observed values.

### `csvkit.utilities.csvjson.GeoJsonBounds.update_lat` · *method*

## Summary:
Incorporate a single latitude value into the object's stored latitude bounds by updating self.min_lat and self.max_lat when the provided value is outside the current range or when the bounds are uninitialized.

## Description:
This method is called each time a latitude value is processed while building or updating a GeoJSON bounding box — for example during iteration over CSV rows when converting rows with coordinate fields into GeoJSON features. It centralizes the logic for:
- Initializing bounds when they are None.
- Tightening (shrinking) the bounds when a new extreme latitude is encountered.

Why this is a separate method:
- Prevents duplication of the None-check and comparison pattern across callers.
- Encapsulates the update semantics so callers simply provide a latitude value and do not need to manage initialization order.
- Keeps bounding-box update logic localized, improving testability and maintainability.

Typical callers / lifecycle stage:
- A CSV-to-GeoJSON conversion loop that extracts latitude and longitude per row and updates aggregate bounds.
- Any incremental bounds-aggregation routine that streams coordinate values and updates an instance representing overall bounds.

## Args:
    lat (float | int | None): The latitude value to incorporate.
        - Expected types: numeric (float or int) is normal. None is allowed but handled specially (see Preconditions and Behavior).
        - No enforcement of geographic validity is performed (e.g., values outside [-90, 90] are accepted as-is).

## Returns:
    None
    - The method updates the object's attributes in-place and does not return a value.

## Raises:
    - This method does not explicitly raise exceptions. However, exceptions may propagate from attribute access or comparisons performed by the logic:
        * AttributeError: If the instance does not have the attributes `min_lat` or `max_lat`, the attempt to read them will raise AttributeError before any assignment.
        * TypeError: Can occur when a comparison is attempted between incompatible types (for example comparing a string to a number). Note: because of Python's short-circuit evaluation, a comparison with `lat` is only executed when the corresponding existing bound is not None (see Preconditions and Behavior). If both bounds are None and `lat` is a non-comparable type (e.g., an object), no comparison will occur and the attributes will be assigned that value without raising.

## State Changes:
    Attributes READ:
        - self.min_lat (checked to decide whether to update)
        - self.max_lat (checked to decide whether to update)
    Attributes WRITTEN:
        - self.min_lat (may be set to lat)
        - self.max_lat (may be set to lat)

## Constraints:
    Preconditions:
        - The instance must have attributes `min_lat` and `max_lat` accessible (commonly initialized to None before any updates).
        - If `lat` is not None, it should be a value that supports `<` and `>` comparisons with any non-None existing bound (typically numeric types). If not, a TypeError may propagate when a comparison is attempted.
    Postconditions:
        - If `lat` is a numeric value:
            * If self.min_lat was None or lat < previous self.min_lat, then after the call self.min_lat == lat.
            * If self.max_lat was None or lat > previous self.max_lat, then after the call self.max_lat == lat.
            * If neither condition holds, the bounds remain unchanged.
            * If both previous bounds were None, both self.min_lat and self.max_lat will be set to lat.
            * After successful numeric updates with finite numbers (no NaN), it holds that self.min_lat <= self.max_lat.
        - If `lat` is None:
            * If a bound was None, the short-circuit condition (bound is None) causes assignment of None to that bound; e.g., if both bounds are None, both will remain None.
            * If a bound is not None, comparing None with a numeric bound will raise TypeError (because comparison is attempted) — such exceptions propagate.
        - Special float values:
            * NaN: comparisons with NaN always return False. If lat is NaN and an existing bound is not None, neither comparison (lat < bound or lat > bound) will be True, so bounds will not be updated; if the existing bound is None, assignment will set the bound to NaN.
            * infinities: +inf and -inf compare as expected and will update bounds accordingly.

## Behavior details (exact logic to implement):
    - If self.min_lat is None OR lat < self.min_lat:
          set self.min_lat = lat
      (Note: the OR uses short-circuit evaluation; when self.min_lat is None, the comparison lat < self.min_lat is not evaluated.)
    - If self.max_lat is None OR lat > self.max_lat:
          set self.max_lat = lat
      (Similarly, when self.max_lat is None, lat > self.max_lat is not evaluated.)
    - No other checks or coercions are performed.

## Side Effects:
    - Mutates only the instance attributes self.min_lat and self.max_lat.
    - No I/O, no calls to external services, and no mutation of objects beyond the instance itself.

### `csvkit.utilities.csvjson.GeoJsonBounds.update_lon` · *method*

## Summary:
Expands the instance's longitude bounds to include the given longitude value by updating min_lon and/or max_lon in-place.

## Description:
This method compares a single longitude value against the instance's stored minimum and maximum longitude and updates those attributes so the bounding interval encompasses the value.

Known callers and context:
- No explicit callers are present in the provided snippet. In the codebase, this method is intended to be invoked while iterating over geographic coordinates (for example, when building GeoJSON features or scanning rows for coordinate values) to maintain an incremental bounding box.
- Typical pipeline stage: called for each processed coordinate during dataset-to-GeoJSON conversion or when aggregating extents from a stream of points.

Why this is a separate method:
- Centralizes and clarifies the update logic for longitude bounds, avoiding duplicated comparison/assignment code and enabling independent testing and reuse alongside a symmetric latitude update method.

## Args:
    lon (int | float | None): The longitude value to include in the bounds. The method expects numeric values (int or float). Passing None is allowed but has special behavior described under Constraints and Edge Cases.

## Returns:
    None: The method does not return a value; it mutates self.min_lon and/or self.max_lon.

## Raises:
    TypeError: Raised indirectly if lon is not orderable with the existing non-None bounds (for example, comparing None or a non-numeric type with a numeric bound). The code uses < and > comparisons; if those comparisons are not supported between lon and self.min_lon/self.max_lon, Python will raise TypeError.

## State Changes:
    Attributes READ:
        self.min_lon
        self.max_lon

    Attributes WRITTEN:
        self.min_lon (set to lon if previously None or lon < previous min_lon)
        self.max_lon (set to lon if previously None or lon > previous max_lon)

## Constraints:
    Preconditions:
        - The instance must have attributes min_lon and max_lon (they may be None initially).
        - lon should normally be a numeric value (int or float). If lon is a non-orderable type and either existing bound is not None, comparisons will raise TypeError.

    Postconditions:
        - If both self.min_lon and self.max_lon were None prior to the call, both will be set to lon.
        - If lon < previous min_lon (or previous min_lon was None), self.min_lon will equal lon after the call.
        - If lon > previous max_lon (or previous max_lon was None), self.max_lon will equal lon after the call.
        - If lon is between or equal to the existing bounds, neither bound changes (except when a bound was None, in which case it is set to lon).

## Edge Cases and Notes:
    - If lon is None:
        * If the corresponding bound is None, that bound will be set to None (no error).
        * If the corresponding bound is not None, a comparison like (None < number) or (None > number) will raise TypeError.
    - If lon is NaN (float('nan')):
        * Comparisons (nan < x) and (nan > x) are False, so bounds will only be set when the corresponding bound is None.
    - Equality: if lon equals an existing bound, no update occurs for that bound.

## Side Effects:
    - Mutates only the GeoJsonBounds instance (self.min_lon and/or self.max_lon).
    - No I/O, no external service calls, and no modifications to objects outside of self.

## Examples (illustrative, written as state transitions):
    - Start: min_lon=None, max_lon=None. Call with lon=10.0 -> Result: min_lon=10.0, max_lon=10.0
    - Start: min_lon=0.0, max_lon=20.0. Call with lon=25.0 -> Result: min_lon=0.0, max_lon=25.0
    - Start: min_lon=0.0, max_lon=20.0. Call with lon=15.0 -> Result: min_lon=0.0, max_lon=20.0 (no change)

### `csvkit.utilities.csvjson.GeoJsonBounds.update_coordinates` · *method*

## Summary:
Recursively traverse a GeoJSON-style coordinates structure and update this object's min/max longitude and latitude so the instance's bounding box includes every point encountered.

## Description:
Known callers:
    - csvkit.utilities.csvjson.GeoJsonBounds.add_feature
      - Called during feature processing: add_feature extracts feature['geometry']['coordinates'] and passes them here to incorporate that feature into the running bounding box.

When invoked:
    - This method is used during GeoJSON parsing/aggregation to fold any geometry's coordinates into the GeoJsonBounds instance. It is executed as part of the pipeline step that consumes GeoJSON feature geometry and computes an overall bounding box for one or more features.

Why this is a separate method:
    - Coordinates in GeoJSON may be arbitrarily nested (Point, LineString, Polygon, MultiPolygon, etc.). The method implements a small, focused recursive algorithm to traverse that nested structure and dispatch numeric coordinate pairs to update_lon/update_lat. Keeping recursion and leaf detection in this helper keeps add_feature simple and centralizes the traversal logic for reuse and testing.

## Args:
    coordinates (sequence): A nested sequence (list/tuple-like) representing GeoJSON coordinates.
        - Expected leaf shapes: sequences whose first element is numeric (float or int) and with at least two elements: [lon, lat] or [lon, lat, alt].
        - Non-leaf shapes: lists/tuples of coordinate sequences (e.g., LineString: [[lon, lat], ...], Polygon: [[[lon, lat], ...], ...]).
        - No default value; must be provided.

## Returns:
    None
    - The method does not return a value. Its effect is to mutate the instance's min/max longitude and latitude fields via update_lon and update_lat.

## Raises:
    IndexError:
        - If a leaf coordinate sequence has fewer than 2 elements (e.g., [] or [lon]) and code attempts to access coordinate[1].
    TypeError:
        - If `coordinates` (or a nested element) is not a sized/iterable sequence (so len(coordinates) or indexing fails).
        - If nested elements are None or otherwise non-indexable; calling len() or indexing will raise TypeError.
    RecursionError:
        - For extremely deep nesting this recursive implementation can raise RecursionError.

Note:
    - The method itself performs only a structural test to detect leaf nodes and relies on update_lon/update_lat to accept and compare numeric values; invalid numeric values passed to those methods may raise additional exceptions (e.g., if comparisons with None or non-numeric types occur).

## State Changes:
Attributes READ:
    - (indirectly, via update_lon/update_lat) self.min_lon, self.max_lon, self.min_lat, self.max_lat

Attributes WRITTEN:
    - (indirectly, via update_lon/update_lat) self.min_lon, self.max_lon, self.min_lat, self.max_lat

## Constraints:
Preconditions:
    - The top-level `coordinates` argument must be a sequence (list/tuple-like). Leaf nodes must be sequences where the first two elements are numeric (float or int).
    - If you expect empty geometries, check for and handle those before calling this method to avoid IndexError.

Postconditions:
    - After successful completion, any numeric lon/lat pairs present in the provided coordinates will have been considered and the instance's min_lon/min_lat/max_lon/max_lat will be updated to include them.
    - If no numeric coordinate pairs were encountered (e.g., empty sequences), the instance attributes remain unchanged (possibly still None).

## Side Effects:
    - Mutates the instance attributes listed above; no I/O, no external service calls.
    - Uses recursion; deeply nested coordinate arrays may consume call stack.

## Implementation notes / reimplementation hints:
    - Treat a node as a "leaf coordinate" when len(node) <= 3 and the first element is a number (float or int). On a leaf, call update_lon(node[0]) and update_lat(node[1]).
    - Otherwise assume the node is an iterable of child coordinate nodes and recursively call update_coordinates on each child.
    - Be defensive in callers: validate shapes where appropriate to provide clearer errors than IndexError/TypeError produced by direct indexing.

## `csvkit.utilities.csvjson.launch_new_instance` · *function*

## Summary:
Constructs a CSVJSON utility instance and runs it, delegating all work and side effects to that instance.

## Description:
This function is a simple entry-point helper that instantiates CSVJSON and immediately invokes its run() method.

Known callers within the provided context:
    - No direct callers were found in the provided source snippet. Functions with this shape are commonly used as a module-level entry point (for example called from an if __name__ == '__main__' block or wired to a packaging console_scripts entry point), but that usage is not present in the inspected code.

Why this logic is extracted:
    - Encapsulates the minimal plumbing required to create and execute a CSVJSON command-line utility so packaging or module entry-point code can invoke the utility with a single callable. It separates the CLI wiring (entry-point) from the CSVJSON implementation and test code.

## Args:
    This function takes no arguments.

## Returns:
    None
    - The function does not return a value; it returns implicitly (None) after CSVJSON.run() completes.
    - If CSVJSON.run() raises an exception, that exception propagates and this function does not return.

## Raises:
    - Any exception raised during CSVJSON() construction or during the execution of utility.run().
      The function contains no try/except; it does not convert or suppress exceptions.

## Constraints:
Preconditions:
    - The CSVJSON class must be importable and constructable in the current runtime context.
    - Any runtime environment or configuration required by CSVJSON (command-line arguments, environment variables, files, etc.) must be satisfied by the caller or the surrounding process.

Postconditions:
    - On normal completion (no exception), CSVJSON.run() has completed its work; any side effects performed by CSVJSON.run() will have been applied.
    - On exception, the exception bubbles to the caller and no further guarantees are made.

## Side Effects:
    - This function performs no I/O or state mutation itself beyond constructing an object and calling its run() method.
    - All I/O, stdout/stderr writes, file reads/writes, network calls, and other external effects are performed by CSVJSON.run() and therefore are side effects observable when invoking this function.
    - No global variables are modified by this function directly.

## Control Flow:
flowchart TD
    Start --> Instantiate[Create CSVJSON instance]
    Instantiate --> CallRun[Call instance.run()]
    CallRun --> Completed[run() returns — function returns None]
    CallRun --> Exception[run() raises exception — exception propagates to caller]

## Examples:
    - Typical use as a CLI entry point: the module can expose launch_new_instance to be called from an if __name__ == '__main__' block or from a packaging console_scripts entry point; calling this function will construct and run the CSVJSON utility.
    - Embedding invocation: callers that need to programmatically run the CLI behavior can call this function (or call CSVJSON().run() directly). Wrap the call in application-level try/except to handle errors emitted by CSVJSON.run().

