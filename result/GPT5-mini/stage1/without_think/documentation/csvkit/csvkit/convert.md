# `csvkit.convert`

## Tree:
convert/
├── __init__.py
├── fixed.py
└── geojs.py

## Role:
Offer format-detection utility and format-specific converters that transform non-tabular or semi-structured inputs into tabular (CSV) representations.

## Description:
- Where/when used:
  - This package is used by higher-level conversion utilities and CLI entry points that must:
    * infer a best-effort format hint from a filename,
    * convert fixed-width schema-driven text files into CSV,
    * convert GeoJSON FeatureCollections into CSV strings.
  - Typical consumers: CLI drivers, ETL scripts, and tests in the codebase that need deterministic conversion routines.

- Why these components are grouped together:
  - Cohesion principle: all modules implement conversion-focused responsibilities. Each submodule concentrates a single conversion domain:
    * fixed.py — fixed-width schema decoding, parsing, and streaming conversion primitives;
    * geojs.py — GeoJSON FeatureCollection → CSV logic;
    * __init__.py — the filename-to-format hint helper only.
  - Grouping keeps file-format-specific parsing and orchestration in one layer separate from CLI handling and downstream output concerns.

## Components:
- convert.__init__.guess_format(filename: str) -> Optional[str]
  - One-line role: Infer a canonical short format label from a filename's final extension or return None for unknown extensions.

- convert.fixed.SchemaDecoder(header: Sequence[str])
  - One-line role: Build a callable that transforms schema CSV rows into FixedWidthField descriptors.

- convert.fixed.SchemaDecoder.__call__(row: Sequence) -> FixedWidthField
  - One-line role: Produce a FixedWidthField (name, zero-based start, length) from a single schema row; discovers 1-based vs 0-based starts on the first call.

- convert.fixed.FixedWidthRowParser(schema)
  - One-line role: Construct an in-memory list of field descriptors by reading a CSV-style schema (constructor reads the schema via the CSV reader); once constructed, expose parse(line) / parse_dict(line) and headers for record parsing (note: parse and parse_dict themselves perform no I/O).

- convert.fixed.FixedWidthRowParser.parse(line: str) -> List[str]
  - One-line role: Slice and trim a record string into a list of field values (no I/O).

- convert.fixed.FixedWidthRowParser.parse_dict(line: str) -> Dict[str, str]
  - One-line role: Return a dict mapping header names to parsed field values for a single record (no I/O).

- convert.fixed.FixedWidthRowParser.headers -> List[str]
  - One-line role: Return the ordered list of configured field names (derived from in-memory field descriptors).

- convert.fixed.FixedWidthReader(f: Iterable[str] | Iterator, schema, encoding: Optional[str] = None)
  - One-line role: Iterator yielding parser.headers first, then parsed rows from the input source.

- convert.fixed.FixedWidthReader.__iter__() -> FixedWidthReader
  - One-line role: Return self to support single-pass iteration.

- convert.fixed.FixedWidthReader.__next__() -> Union[List[str], headers]
  - One-line role: Return headers on first call, then parsed rows; propagate StopIteration when input exhausted.

- convert.fixed.fixed2csv(f, schema, output=None, skip_lines: int = 0, **kwargs) -> str
  - One-line role: Orchestrate fixed-width → CSV conversion; write to provided output or return CSV text.

- convert.geojs.geojson2csv(f, key=None, **kwargs) -> str
  - One-line role: Convert a GeoJSON FeatureCollection read from f into a CSV string with id, discovered properties, geometry (as JSON text), geometry type, longitude and latitude where applicable.

Mermaid-style dependency graph (internal relationships):
graph TD
    fixed2[fixed2csv]
    fwr[FixedWidthReader]
    parser[FixedWidthRowParser]
    decoder[SchemaDecoder]
    geo[geojson2csv]
    guess[guess_format]

    fixed2 --> fwr
    fwr --> parser
    parser --> decoder
    geo --> guess[guess_format]:::utility
    classDef utility stroke-dasharray: 5 5;

(Note: guess_format is a utility exported from __init__.py. The dashed utility link indicates it is an independent filename-hint helper and is not required by geojson2csv; external dispatchers may use it to route inputs.)

## Public API (signatures, behavior notes, and common exceptions):
- guess_format(filename: str) -> Optional[str]
  - Description: Return one of 'fixed', 'csv', 'dbf', 'xls', 'xlsx', 'json' (json also for '.js'), or None when the filename's final extension is unrecognized. If filename contains no dot at all returns 'fixed'.
  - Raises: AttributeError (if filename is not string-like and lacks rfind); callers should validate input types when necessary.
  - Usage note: Best-effort hint only; do not rely on it for authoritative detection.

- fixed.SchemaDecoder(header: Sequence[str])
  - Description: Construct a decoder with required header columns 'column', 'start', 'length' (case-sensitive). The instance is callable for per-row decoding.
  - Raises: ValueError if a required column is missing in header.
  - Usage note: On first call the decoder determines whether start indices are 1-based (and adjusts to zero-based thereafter).

- fixed.SchemaDecoder.__call__(row: Sequence) -> FixedWidthField
  - Description: Return a FixedWidthField-like object with attributes .name (str), .start (int, zero-based), .length (int).
  - Raises: IndexError, ValueError, TypeError from indexing or int() conversion when a schema row is malformed.
  - Usage note: Let these exceptions propagate to surface malformed schema rows.

- fixed.FixedWidthRowParser(schema)
  - Description: Build parser from a CSV-style schema using the project's CSV reader. The constructor reads the provided schema iterable and builds in-memory field descriptors; parse and parse_dict do not perform I/O.
  - Raises:
    * StopIteration if schema has no header row.
    * ValueError if decoding any schema data row fails (message includes 1-based schema line number).
    * Other exceptions from the CSV reader if schema input is inappropriate.
  - Usage note: The constructor consumes the schema iterable; callers should manage the schema file handle lifecycle.

- fixed.FixedWidthRowParser.parse(line: str) -> List[str]
  - Description: Slice the input line per field descriptors and return stripped strings for each field. This method performs no I/O.
  - Raises: TypeError if line is not sliceable; AttributeError if field descriptors lack expected attributes.
  - Usage note: For truncated lines, slices produce shorter/empty strings (no exception).

- fixed.FixedWidthRowParser.parse_dict(line: str) -> Dict[str, str]
  - Description: Return dict(zip(headers, parse(line))). This method performs no I/O.
  - Raises: Same as parse(line) and potential AttributeError if field names missing.
  - Usage note: Duplicate header names will be overwritten according to standard dict behavior.

- fixed.FixedWidthReader(f, schema, encoding: Optional[str] = None)
  - Description: Single-pass iterator that yields headers first then parsed rows. If encoding is provided and f yields bytes, the reader wraps f with codecs.iterdecode.
  - Raises: Exceptions from parser construction (ValueError, StopIteration) and any exceptions from parser.parse during iteration. StopIteration when underlying input exhausted.
  - Usage note: Does not close f; do not iterate concurrently over the same instance.

- fixed.fixed2csv(f, schema, output=None, skip_lines: int = 0, **kwargs) -> str
  - Description: Convert fixed-width input into CSV. When output is None returns CSV text; when output is provided writes into it and returns ''.
  - Raises:
    * ValueError('skip_lines argument must be an int') if skip_lines is not an int.
    * Exceptions from FixedWidthReader or the CSV writer (propagated).
  - Usage note: If skip_lines > 0, f must implement readline(); provide encoding via kwargs if f yields bytes.

- geojs.geojson2csv(f, key=None, **kwargs) -> str
  - Description: Read JSON from f; expect a GeoJSON FeatureCollection; iterate features to build CSV with columns: id, property keys (in encounter order), geojson, type, longitude, latitude.
  - Raises:
    * json.JSONDecodeError for invalid JSON input.
    * TypeError if root JSON is not an object or lacks required top-level keys, or if root 'type' is not 'FeatureCollection'.
    * KeyError if a feature is missing the 'geometry' key (the implementation accesses feature['geometry'] directly).
    * Other exceptions from the CSV writer or memory allocation if many features are loaded into memory.
  - Usage note: The function serializes geometry and OrderedDict property values with json.dumps before writing.

## Dependencies:
- Internal:
  - convert.fixed: fixed-width parsing and conversion primitives (SchemaDecoder, FixedWidthRowParser, FixedWidthReader, fixed2csv).
  - convert.geojs: GeoJSON conversion entry point.
  - convert.__init__: exposes guess_format only (a filename-to-format hint).
  - Note: Each component-level doc contains precise internal call relationships; consult those for implementation-level wiring.

- External / stdlib:
  - json — parse GeoJSON and serialize geometries/properties in geojson2csv.
  - codecs, io — optional decoding and StringIO buffers.
  - CSV reader/writer used by the conversion primitives (the project uses an agate-based CSV reader/writer): FixedWidthRowParser relies on the CSV reader for schema reading; fixed2csv and geojson2csv use a CSV writer for output.

## Expected FixedWidthField contract:
- FixedWidthField objects produced by SchemaDecoder must expose:
  - .name (str): column name
  - .start (int): zero-based start offset into a record
  - .length (int): number of characters for the field
- Implementations may use a small namedtuple, dataclass, or simple class with these attributes.

## State and mutability notes:
- Class-level constants:
  - SchemaDecoder defines class-level constants such as REQUIRED_COLUMNS used during initialization and header validation.
- Per-instance mutable state:
  - SchemaDecoder instances keep per-instance state (one_based: Optional[bool]) that is None until the first data row is processed and then becomes a boolean used for all subsequent rows.
  - FixedWidthReader instances keep a per-instance header flag (header: bool) that toggles from True to False once headers are emitted.
- Threading implication: Because of per-instance mutable state, create separate instances for concurrent use or add synchronization.

## Constraints:
- Input and encoding:
  - If encoding is provided for FixedWidthReader/fixed2csv, the input f must yield bytes; otherwise it must yield str. Mixing will raise decoding or type errors.
  - Schema must be a CSV-acceptable iterable for the CSV reader and must include the required header columns 'column', 'start', 'length'.

- Iteration semantics:
  - FixedWidthReader is single-pass; __iter__ returns self. Recreating the reader is required to re-read input from an earlier position.
  - FixedWidthReader and FixedWidthRowParser do not close input streams; callers manage resource lifecycle.

- Schema consistency:
  - SchemaDecoder determines one-based vs zero-based start indices from the first row it processes and applies the same rule to all rows. Mixed conventions will be interpreted according to that first row.

- Thread-safety:
  - Components are not thread-safe. Instances hold mutable per-instance state (SchemaDecoder.one_based and FixedWidthReader.header). Use separate instances per thread or add external synchronization.

- Error handling:
  - The module typically propagates underlying exceptions to preserve original error types and messages (schema ValueError with line info, json.JSONDecodeError, StopIteration, TypeError). Callers should catch and handle these as appropriate.

## Where to find component details:
- See component-level documentation for full implementation guidance, examples, and edge cases:
  - csvkit.convert.__init__.guess_format
  - csvkit.convert.fixed (SchemaDecoder, FixedWidthRowParser, FixedWidthReader, fixed2csv)
  - csvkit.convert.geojs.geojson2csv

These component docs include the precise constructor semantics, exceptions, and per-method behavior needed to reimplement each piece.

---

## Files

- [`__init__.py`](convert/__init__.md)
- [`fixed.py`](convert/fixed.md)
- [`geojs.py`](convert/geojs.md)

