# `fixed.py`

## `csvkit.convert.fixed.fixed2csv` · *function*

## Summary:
Convert a fixed-width record stream into CSV-formatted output, either returning the CSV as a string (non-streaming mode) or writing rows into a provided writable text stream (streaming mode).

## Description:
This function orchestrates conversion of a fixed-width formatted input into CSV by:
- Optionally skipping an initial number of lines from the input.
- Creating an agate CSV writer bound to either an internal in-memory buffer (for non-streaming usage) or to a user-supplied writable output stream (for streaming usage).
- Instantiating a FixedWidthReader with the provided schema (which yields the header row then parsed data rows).
- Writing all rows emitted by the FixedWidthReader via writer.writerows(...).

Known callers in this codebase:
- No direct call sites were discovered in the scanned code when this documentation was produced. Typical call sites include CLI commands and higher-level conversion utilities in csvkit that transform files from fixed-width to CSV format, and ETL pipelines that convert legacy fixed-width exports into CSV for downstream processing.

Why this is a separate function:
- It encapsulates the conversion workflow (pre-skipping input, constructing writer/reader, and producing CSV output) so that other parts of the toolchain can reuse a consistent, tested conversion step without duplicating skip/streaming/encoding handling or dealing with the writer/reader lifecycle.

## Args:
- f (file-like object or iterator): Source of input records. Expected to support reading lines. If skip_lines > 0, f must provide a readline() method; otherwise skip_lines will raise an exception when attempting to call readline. Accepts either:
    - a text-mode file/iterator that yields str per iteration, or
    - a binary-mode file/iterator that yields bytes (in which case FixedWidthReader may decode it when an encoding is supplied).
  Note: The function itself does not decode bytes; encoding handling is delegated to FixedWidthReader.

- schema (any): Schema describing the fixed-width fields. Passed through to FixedWidthReader (and, transitively, to FixedWidthRowParser). The exact form is whatever FixedWidthRowParser expects (commonly a CSV-like schema source acceptable to agate.csv.reader). This function treats schema opaquely and will propagate any exceptions raised during parser construction.

- output (file-like writable, optional): If provided, this writable object receives CSV output via agate.csv.writer(output). It must accept text writes (i.e., a write(str) method). When provided, the function operates in streaming mode: it writes into this object and returns an empty string. When omitted or None (the default), the function collects CSV in an internal StringIO and returns it as a single string.

- skip_lines (int, default 0): Number of initial input lines to discard before converting. Must be an int. If skip_lines > 0, the function calls f.readline() skip_lines times before conversion begins. If skip_lines is not an int, a ValueError is raised.

- **kwargs: Additional keyword arguments. Recognized keyword:
    - encoding (str, optional): Passed to FixedWidthReader via its constructor call in this function. If provided and the input yields bytes, FixedWidthReader may decode the byte stream to text using this encoding. Any other kwargs are ignored by fixed2csv.

Interdependencies:
- If skip_lines > 0, f must have a readline() method; otherwise an AttributeError occurs.
- If output is provided, it must be writable and accept str. Otherwise, agate.csv.writer will raise an error when attempting to write.

## Returns:
- str: In non-streaming mode (output is None), returns the entire CSV content produced from the input as a single string. The internal StringIO buffer is closed before return.
- str (empty): In streaming mode (output provided), returns an empty string ('') after writing to the provided output stream. The function does not close the provided output stream.

## Raises:
- ValueError: Raised if skip_lines is not an int. The exact message produced by this function is 'skip_lines argument must be an int'.
- Any exception raised by FixedWidthReader construction or iteration (for example, schema-related ValueError, TypeError, or parser errors) will propagate unchanged.
- Any exception raised by agate.csv.writer(...) or writer.writerows(...) (for example, if output is not a suitable text-writable stream or rows are malformed) will propagate unchanged.
- AttributeError or TypeError may be raised if f does not support required operations (e.g., missing readline when skip_lines > 0, or not iterable when FixedWidthReader iterates it).

## Constraints:
Preconditions:
- The caller is responsible for providing a valid schema acceptable to FixedWidthReader/FixedWidthRowParser.
- If skip_lines > 0, f must implement a readline() method. If f yields bytes, and decoding is necessary, provide encoding via kwargs so FixedWidthReader can handle decoding.
- If output is provided, it must be a writable text-mode stream (i.e., supports write(str)).

Postconditions:
- The input stream f is consumed for all rows processed; the function does not rewind the input or close it.
- If output was provided, the CSV data has been written to that stream; the stream remains open.
- If output was not provided, the function returns the full CSV text and the internal StringIO used to collect it has been closed.

## Side Effects:
- I/O:
    - Reads from f (calls readline() when skipping lines, then iterates f via FixedWidthReader).
    - Writes CSV text to output (either the provided output stream or an internal StringIO).
- External state:
    - Does not close or modify the provided input stream f or provided output stream. If using internal StringIO, the function closes it before returning the string.
- No network, database, or other external service calls are made by this function itself; any such effects would only occur if FixedWidthReader or the writer's configuration caused them (which is not typical).

## Control Flow:
flowchart TD
    A[Start fixed2csv(f, schema, output=None, skip_lines=0, **kwargs)]
    A --> B{output provided?}
    B -- yes --> C[streaming = True; use provided output]
    B -- no  --> D[streaming = False; create internal StringIO as output]
    C --> E[Extract encoding from kwargs if present else encoding=None]
    D --> E
    E --> F{is skip_lines an int?}
    F -- no --> G[raise ValueError('skip_lines argument must be an int')]
    F -- yes --> H[call f.readline() skip_lines times]
    H --> I[writer = agate.csv.writer(output)]
    I --> J[reader = FixedWidthReader(f, schema, encoding=encoding)]
    J --> K[writer.writerows(reader)  (writes header then rows)]
    K --> L{streaming is False?}
    L -- yes --> M[get data = output.getvalue(); output.close(); return data]
    L -- no  --> N[return '' (empty string)]

## Examples (prose):
- Non-streaming conversion (collect CSV as return string):
  Provide a text-mode file (or other iterator producing str), a schema acceptable to your FixedWidthRowParser, and leave output as None. The function will return a single string containing the CSV (including header). After the call, the input file position will be advanced to the end of the consumed rows; the input file remains open and must be closed by the caller if appropriate.

- Streaming conversion (write directly to an output file):
  Provide an open writable text-mode file as output. The function will write header and rows directly into the provided stream and return an empty string. The provided output stream will NOT be closed by the function; it is the caller's responsibility to flush/close it as needed.

- Binary input with encoding:
  If your input is a binary stream (yields bytes) and the parser expects text, provide an encoding keyword (e.g., encoding='utf-8'). FixedWidthReader will be constructed with that encoding and will handle decoding so the CSV writer receives text rows. If encoding is omitted and input yields bytes, parsing or writing may raise TypeError or other decoding-related exceptions.

- Error handling:
  - If skip_lines is accidentally passed as a non-int value, expect a ValueError with message 'skip_lines argument must be an int'.
  - Schema or parsing problems coming from FixedWidthReader/FixedWidthRowParser will raise their native exceptions; callers should validate or catch those exceptions where appropriate.

## `csvkit.convert.fixed.FixedWidthReader` · *class*

## Summary:
An iterator that reads a fixed-width data file and yields a header row (list of column names) followed by parsed rows (lists of field values) according to a provided fixed-width schema.

## Description:
FixedWidthReader wraps a file-like iterator of record lines and a FixedWidthRowParser (constructed from a schema) to provide a simple, Python iterator-style interface for fixed-width files. On the first iteration it yields the parser.headers (a list of column names); each subsequent iteration yields parser.parse(line) for the next input line.

When to instantiate
- Use when you have:
  - a fixed-width data file (or any iterator of records) and
  - a schema describing fields (suitable for FixedWidthRowParser).
- Typical callers:
  - ETL code that converts fixed-width text files into row lists for CSV or database insertion.
  - Higher-level converters/factories that combine schema reading and data streaming.
- The schema argument should be whatever FixedWidthRowParser expects (commonly a CSV-like schema source acceptable to agate.csv.reader).

Motivation and responsibility boundary
- Responsibility: provide an easy-to-use iterator over an input fixed-width data source that first emits headers then parsed rows, delegating parsing logic to FixedWidthRowParser.
- FixedWidthReader does not parse schema contents itself, does not validate file encoding beyond optionally wrapping byte streams, and does not manage file lifecycle (closing) for you.

## State:
- file (iterator of str)
  - Type: iterator or any object supporting the iterator protocol returning str on each iteration (e.g., an open file in text mode, an iterator of strings, or an iterator returned by codecs.iterdecode when wrapping a byte stream).
  - Invariants: each next(self.file) call must produce a str record. If file yields non-str (e.g., bytes), parser.parse may raise; callers should ensure encoding handling is correct.
- parser (FixedWidthRowParser)
  - Type: FixedWidthRowParser instance
  - Meaning: the schema-aware parser used to produce headers and parse records.
  - Invariants: parser.headers is a list of column names; parser.parse accepts a single str record and returns a list of values in the same order as headers.
- header (bool)
  - Type: bool
  - Meaning: indicates whether the next __next__ call should return headers (True) or parse a data line (False).
  - Invariant: header is True only before the iterator has yielded headers; after the first __next__ call it becomes False for the remainder of the iterator's life.

Class invariants:
- parser is a valid FixedWidthRowParser (constructed during __init__); if parser construction raised, the FixedWidthReader is not created.
- file is an iterator that will supply records compatible with parser.parse (i.e., strings); if not, parsing errors may occur.
- header toggles from True to False exactly once, causing a single headers emission at the start of iteration.

## Lifecycle:
Creation:
- Call FixedWidthReader(f, schema, encoding=None)
  - f: file-like object or iterator of records. If f yields bytes and encoding is a str, the constructor will wrap f using codecs.iterdecode(f, encoding) so subsequent iterations yield str.
  - schema: passed to FixedWidthRowParser(schema). See FixedWidthRowParser documentation for accepted schema formats. Construction will raise any exceptions propagated from FixedWidthRowParser.
  - encoding: optional str specifying the character encoding to use when f yields bytes; default None.
Usage:
- The object implements the iterator protocol:
  - Use in a for-loop: for row in FixedWidthReader(...): ...
  - On first iteration, yields parser.headers (list[str]).
  - On subsequent iterations, yields parser.parse(next(self.file)) (list[str] for each record).
- Ordering and sequencing:
  - __iter__ returns self; __next__ must be called repeatedly until StopIteration is raised by the underlying file.
  - The required order is: first headers, then zero or more parsed rows. There is no method to re-emit headers; to restart you must create a new FixedWidthReader.
Destruction / cleanup:
- FixedWidthReader does not own or close the underlying file object. If the caller opened a file (e.g., open(...)), the caller is responsible for closing it (or using a context manager around file creation).
- No explicit close(), __enter__, or __exit__ is provided by FixedWidthReader.

## Method Map:
flowchart LR
    A[__init__(f, schema, encoding=None)]
    A --> B{encoding is not None?}
    B -- yes --> C[wrap f with codecs.iterdecode(f, encoding) -> iterator of str]
    B -- no  --> D[use f as provided]
    C --> E[self.file = iterator]
    D --> E
    A --> F[self.parser = FixedWidthRowParser(schema)]
    A --> G[self.header = True]
    E --> H[__iter__() -> returns self]
    H --> I[__next__()]
    I --> J{self.header is True?}
    J -- True --> K[self.header = False; return self.parser.headers]
    J -- False --> L[next(self.file) -> line -> return self.parser.parse(line)]

## Raises:
- __init__:
  - ValueError: may be raised if FixedWidthRowParser(schema) raises a schema-related ValueError (for example, malformed schema). These exceptions propagate unchanged.
  - TypeError / other exceptions from FixedWidthRowParser or agate: may propagate if schema is an unexpected type.
  - Note: codecs.iterdecode does not itself raise synchronously; errors may arise when iterating if the byte stream contains invalid sequences and the chosen error handling triggers exceptions.
- __next__:
  - StopIteration: propagated when the underlying file iterator is exhausted. If StopIteration occurs on the first data read, only headers will have been emitted.
  - TypeError: may be raised if next(self.file) yields an object not suitable for parser.parse (e.g., bytes instead of str) or if self.file is not iterable.
  - Any exception raised by FixedWidthRowParser.parse (propagated). For example, if parser.parse expects a str and receives incompatible input, a TypeError may result.

## Example:
- Typical usage patterns (conceptual, not code-level internals):
  - If your data file is binary (yields bytes), open it in binary mode and provide an encoding:
    - Provide f as a binary iterator (e.g., open('data.txt','rb')) and encoding='utf-8'. FixedWidthReader will wrap f so records are decoded to str.
  - If your data file is already text (str), pass the text-mode file (e.g., open('data.txt','r')) and leave encoding as None.
  - Iteration semantics:
    1. Instantiate reader = FixedWidthReader(f, schema, encoding)
    2. First iteration yields headers (list of column names).
    3. Each later iteration yields a list of values parsed from the next input line until the underlying file raises StopIteration.
  - Cleanup: close the file you opened after iteration; FixedWidthReader does not close it for you.

### `csvkit.convert.fixed.FixedWidthReader.__init__` · *method*

## Summary:
Initializes the reader by preparing a line iterator (optionally decoding bytes to text), constructing a FixedWidthRowParser from the provided schema, and setting the reader to emit a header row on first iteration.

## Description:
This initializer is called when a FixedWidthReader is created as the first step in a fixed-width file reading pipeline. Typical callers instantiate this object when they need an iterator that yields a header row first (derived from the schema) and then parsed record rows. The constructor is a separate method to encapsulate setup responsibilities: (1) normalize/prepare the incoming file/line source (text vs bytes), (2) create and configure the schema-driven parser, and (3) initialize iteration state (header emission flag). Keeping this logic in __init__ keeps iteration (__next__) simple and ensures that parser construction (which may read the schema) happens exactly once at creation time.

## Args:
    f (iterable or iterator): The file or sequence of input lines that will supply record text lines to read.
        - If encoding is None (default), f must yield str (text) lines (for example, an opened text file or any iterator of strings).
        - If encoding is provided (a str), f must yield bytes (for example, an opened file in binary mode or a bytes iterator). The initializer will wrap f with codecs.iterdecode(f, encoding) to produce a text iterator.
        - The object must be an iterator or otherwise support next(f) when iteration begins; callers that provide a non-iterator iterable should rely on Python to obtain an iterator before passing it (or pass iter(f)).
    schema (file-like or iterable): The schema source describing fixed-width fields. Accepted forms match what FixedWidthRowParser accepts (i.e., any input acceptable to agate.csv.reader — commonly a text file-like object or iterable of CSV-formatted strings describing columns "column", "start", and "length").
    encoding (str or None, optional): Codec name used to decode bytes from f into text. If None, no decoding wrapper is applied and f is used directly. If provided, codecs.iterdecode is used to wrap f so subsequent iteration yields decoded str lines.

## Returns:
    None

## Raises:
    - Any exception raised by codecs.iterdecode when given an invalid encoding or incompatible input will propagate (e.g., LookupError for unknown codec, or TypeError if f yields str instead of bytes when an encoding is supplied).
    - Any exception raised by FixedWidthRowParser(schema) will propagate. Notable exceptions that may be raised by the parser constructor (and therefore by this initializer) include:
        - ValueError: when the schema is malformed (the parser wraps schema-decoding errors with ValueError indicating the failing schema line).
        - StopIteration: if the schema source contains no header row (agate.csv.reader yields no rows). This originates from the parser's attempt to read the schema header.
        - Other exceptions from agate.csv.reader if the schema argument is of an inappropriate type.
    - No exceptions are explicitly caught in this initializer; all such errors propagate to the caller.

## State Changes:
    Attributes READ:
        - None (this method does not read any existing self attributes)

    Attributes WRITTEN:
        - self.file: set to either the original f or the iterdecode-wrapped text iterator when encoding is provided.
        - self.parser: set to a new FixedWidthRowParser instance constructed with the provided schema.
        - self.header: set to True to indicate that the first value yielded by iteration should be the header row.

## Constraints:
    Preconditions:
        - The provided schema must be valid for FixedWidthRowParser (a CSV-like schema with required columns). If it is not, parser construction will raise (see Raises).
        - If encoding is supplied, f must yield bytes; supplying an encoding while passing a text iterator will likely lead to a TypeError when iterdecode tries to decode non-bytes input.
        - If encoding is None, f should yield str; if it yields bytes instead, later parsing (which expects str) will fail or produce incorrect behavior.
        - f must be an object that can be iterated with next(self.file) during subsequent iteration (i.e., an iterator or iterable that the caller or Python turns into an iterator).

    Postconditions:
        - After return:
            - self.file is an iterator that yields text (str) lines for parsing.
            - self.parser is a ready-to-use FixedWidthRowParser that exposes headers and parse(parse_dict) methods.
            - self.header is True so that the first call to __next__ returns parser.headers.

## Side Effects:
    - Construction of FixedWidthRowParser(schema) may read from the schema iterable/file (it uses agate.csv.reader internally). The schema source will therefore be consumed (at least the header row and subsequent schema rows). If the caller passed a file-like schema object, it may be advanced/partially consumed as a result.
    - No files are opened or closed by this method directly; no network or external service calls are made.
    - No mutation of objects external to this instance occurs other than consuming the provided schema iterable and wrapping the provided file iterator with iterdecode when encoding is supplied.

### `csvkit.convert.fixed.FixedWidthReader.__iter__` · *method*

## Summary:
Returns the reader instance itself so the object can be used as a Python iterator without altering its internal state.

## Description:
This implements the iterable half of Python's iterator protocol so FixedWidthReader can be used directly in iteration contexts (for loops, the iter() builtin, or any API that accepts an iterable). Typical callers include:
- A for-in loop that consumes rows: for row in fixed_width_reader: ...
- The iter() builtin when a caller explicitly obtains an iterator: it = iter(fixed_width_reader)
- APIs that convert iterables to collections: list(fixed_width_reader), tuple(fixed_width_reader)

This logic is its own method to satisfy Python's iterator protocol (an object is iterable if it defines __iter__ that returns an iterator). The method is intentionally minimal — it returns self so the object acts as its own iterator (the __next__ method on the same object advances reading). Keeping this logic here (rather than inlined elsewhere) makes the iterator contract explicit and keeps iteration-related behavior localized.

## Args:
None.

## Returns:
FixedWidthReader
    The same instance (self). This is the iterator object that will be repeatedly queried (via __next__) to produce rows. Repeated calls to __iter__ return the same instance; the method does not create or return a fresh iterator.

## Raises:
None. This method does not raise exceptions itself.

## State Changes:
Attributes READ:
    None — this method does not access any of the instance attributes.

Attributes WRITTEN:
    None — this method does not modify any instance attributes.

## Constraints:
Preconditions:
    - The FixedWidthReader instance must have been initialized (its __init__ called) so it is a valid object. However, __iter__ itself does not require any particular attribute values.

Postconditions:
    - The method returns self without changing any attributes.
    - The returned object will be used as the iterator; subsequent iteration will call this object's __next__ method, which advances the reader's state (for example, toggling header from True to False on first next()).

Important behavioral guarantees and caveats:
    - Calling iter(reader) or using reader in a for loop does NOT reset reader.header or any other internal state. Iteration is single-pass: once consumption has advanced (via __next__), that state remains.
    - Because the instance is its own iterator, multiple concurrent iterations over the same FixedWidthReader will share iteration state and interfere with each other. If independent iterations are needed, create separate FixedWidthReader instances.

## Side Effects:
    - None. This method performs no I/O and does not mutate external objects.

### `csvkit.convert.fixed.FixedWidthReader.__next__` · *method*

## Summary:
Return the next row from the reader, yielding the parser-provided header on the first call and parsed data rows thereafter; flips the internal header flag when the header is consumed.

## Description:
This method implements the iterator protocol's next operation for FixedWidthReader. Typical callers are consumer code that iterates over a FixedWidthReader instance (for example, "for row in reader:" or code that explicitly calls next(reader)). In a CSV/format conversion pipeline it is invoked during the row-by-row read stage to obtain the header first (once) and then each parsed data row in sequence.

This logic is implemented as its own method because it is the iterator protocol hook (__next__) and must:
- return the header row exactly once (lazily) without consuming a data line,
- advance and parse data lines thereafter,
- integrate with Python's StopIteration semantics.
Separating this behavior into __next__ keeps iteration semantics centralized and avoids duplicating header/first-row logic in callers.

## Args:
    self (FixedWidthReader): instance initialized via FixedWidthReader.__init__.
        Required object state (established by __init__):
            - self.file: an iterator (supports next()) that yields raw input lines (typically strings).
            - self.parser: an object exposing:
                * headers (attribute): the header row to return on first call.
                * parse(line) (method): accepts one raw line from self.file and returns a parsed row object.
            - self.header: bool flag indicating whether the header has not yet been returned.

## Returns:
    parser.headers or parser.parse(...) result
    - On the very first call when self.header is True: returns the value of self.parser.headers (type is whatever FixedWidthRowParser.headers provides — typically a sequence of column names).
    - On subsequent calls: returns the value returned by self.parser.parse(next(self.file)) — a row-like object as defined by the parser (commonly a list, tuple, or namedtuple representing parsed fields).
    - There is no special sentinel return value; normal end-of-input is signaled by raising StopIteration.

## Raises:
    StopIteration:
        - If called when there are no more data lines and the method tries to advance self.file (i.e., next(self.file) raises StopIteration).
        - Note: If header is True and there are no data lines, this method will still return parser.headers on the first call; subsequent calls will raise StopIteration when advancing self.file.
    Any exception raised by self.parser.parse(line):
        - Errors coming from the parser (e.g., value/formatting errors) are not caught here and will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.header
        - self.parser
        - self.file
    Attributes WRITTEN:
        - self.header (set to False on the first call that returns the header)

## Constraints:
    Preconditions:
        - The instance must have been initialized such that:
            * self.file is an iterator yielding raw input lines (string-like).
            * self.parser exists and exposes both .headers and .parse(line).
            * self.header is a boolean (True to return headers first, False to skip).
    Postconditions:
        - After the first call that returned the header, self.header is False.
        - Each successful non-header return advances self.file by exactly one element.
        - Iteration follows Python semantics: when underlying file iterator is exhausted, StopIteration will be raised to the caller.

## Side Effects:
    - Advances/mutates the external file iterator (self.file) by consuming elements via next(self.file); if self.file is a file object or generator, this performs I/O or generator progression.
    - Delegates parsing work to self.parser.parse, which may have its own side effects (these are not handled here).

## `csvkit.convert.fixed.FixedWidthRowParser` · *class*

## Summary:
Parses lines from a fixed-width text record using a CSV-based schema; produces lists of field values or dictionaries keyed by field names.

## Description:
FixedWidthRowParser consumes a schema (CSV-like) that describes fixed-width fields and builds an ordered list of field descriptors (FixedWidthField objects with attributes .name, .start, .length). After construction it can parse any record-line (a string) according to that schema.

When to instantiate:
- Use when you have a schema file (or iterable of rows) describing fixed-width columns with at least the columns "column", "start", and "length".
- Typical caller: code that reads a fixed-width data file and needs to convert each record into row values or a mapping keyed by field names.
- The constructor expects an argument acceptable to agate.csv.reader: a file-like object or iterable of lines (the same input type you would pass to the CSV reader).

Motivation and responsibility boundary:
- This class separates schema decoding from record parsing: SchemaDecoder converts schema rows into canonical FixedWidthField descriptors; FixedWidthRowParser stores those descriptors and applies them to actual record lines.
- It is intentionally small: responsibilities are (1) read schema -> build list of fields, (2) slice input lines by those fields, (3) provide header names and a dict-oriented parsing helper. It does not validate semantic constraints of start/length values beyond trusting the schema produced by SchemaDecoder.

## State:
- fields (list[FixedWidthField])
  - Type: list of objects/tuples with attributes .name (str), .start (int), .length (int).
  - Meaning: ordered descriptors for each fixed-width field in the record.
  - Invariant: fields is an ordered list; for each field f, f.start and f.length are integers and f.name is a string. The parser assumes f.start is a zero-based offset into the record.
  - Populated in __init__ by iterating the schema rows and applying SchemaDecoder to each row.
- No other instance attributes are stored.

Notes on FixedWidthField contract (expected):
- Minimal required attributes on each element of fields:
  - name: str — the field name (used by headers and parse_dict).
  - start: int — zero-based start offset inside a record.
  - length: int — number of characters for the field.
- SchemaDecoder (used by __init__) is expected to normalize input so start is zero-based.

Class invariants:
- After initialization, fields is non-empty when the schema contains rows; if the schema has no data rows, fields will be an empty list.
- All parse and header operations read from self.fields; altering self.fields externally will change parser behavior.

## Lifecycle:
Creation:
- FixedWidthRowParser(schema)
  - schema: an object acceptable to agate.csv.reader (commonly a file-like object opened in text mode or an iterable of strings representing CSV rows).
  - The constructor uses agate.csv.reader(schema). It reads the CSV header row (first row) to construct a SchemaDecoder, then iterates the remaining schema rows and appends the SchemaDecoder(row) result to self.fields.
  - If SchemaDecoder(row) raises, the constructor catches it and re-raises a ValueError with the message "Error reading schema at line %i: %s" where %i is the 1-based schema file line number for the failing data row (header counts as line 1, so the first data row is reported as line 2).

Usage:
- parse(line) -> list[str]
  - Input: line (expected str representing one record of fixed-width text).
  - Behavior: for each field in self.fields, extracts line[field.start: field.start + field.length], trims whitespace (.strip()), and appends to a list of values. Returns the list of strings in the same order as the schema.
  - Sequence: call parse repeatedly for each data record. parse is stateless and idempotent per call (reads only self.fields and the provided line).

- parse_dict(line) -> dict[str, str]
  - Input: same as parse.
  - Behavior: returns a dict mapping header names (from headers property) to their corresponding parsed value for the given line. Internally calls parse(line) and zips headers with the list of parsed values.
  - Use when you want name->value lookups rather than positional lists.

- headers (property) -> list[str]
  - Behavior: returns [field.name for field in self.fields]. Useful to obtain column names in order.

Destruction/cleanup:
- No explicit resource management or close() is required. The parser holds only in-memory descriptors. If you opened the schema file yourself to pass into the constructor, you are responsible for closing it.

## Method Map:
graph LR
    A[__init__(schema)] --> B[agate.csv.reader(schema)]
    B --> C[next(schema_reader) -> header]
    C --> D[SchemaDecoder(header)]
    D --> E[for each schema row: schema_decoder(row) -> FixedWidthField]
    E --> F[self.fields.append(FixedWidthField)]
    F --> G[parse(line)]
    G --> H[for field in self.fields: slice and strip -> collect values]
    H --> I[return list of values]
    G --> J[parse_dict(line)]
    J --> K[headers property]
    K --> L[return dict(zip(headers, values))]

Typical invocation order:
1. Instantiate: parser = FixedWidthRowParser(schema_stream)
2. Repeatedly: values = parser.parse(line) or row_map = parser.parse_dict(line)
3. Access headers as needed: names = parser.headers

## Raises:
- __init__(schema):
  - ValueError: re-raised when SchemaDecoder(row) (or any other error while decoding a schema data row) raises an exception. The message is formatted as "Error reading schema at line %i: %s" where i is the 1-based line number of the offending schema data row (header is line 1).
    - Typical triggers: malformed or missing numeric start/length values in a schema row, index errors when a schema row is shorter than the header, or other conversion errors surfaced by SchemaDecoder.
  - StopIteration: if the provided schema has no header row (i.e., agate.csv.reader(schema) yields no rows), next(schema_reader) will raise StopIteration. This is not caught; callers should ensure schema contains at least a header row.
  - TypeError / other exceptions from agate.csv.reader: if schema is not an appropriate iterable/file-like object for the CSV reader, agate.csv.reader may raise; these propagate.

- parse(line):
  - Generally does not raise if line is a str. Slicing a short string returns shorter strings or empty strings; no exception is raised.
  - If line is not subscriptable (e.g., None), Python will raise a TypeError when attempting to slice.

- parse_dict(line):
  - No direct exceptions beyond those possible in parse; if number of values from parse does not match headers length (should not happen for well-formed fields), zip silently truncates to the shorter length.

Edge conditions and notes:
- If schema contains negative start or length values (SchemaDecoder or the schema permits them), slicing semantics are those of Python string slicing and may produce surprising results. Upstream validation is recommended if negative indices are not acceptable.
- If a field's start index is beyond the end of the string, slicing yields an empty string; parse will return '' for that field (after .strip()).
- Mixed one-based and zero-based starts in the same schema file are not supported; SchemaDecoder determines one-based vs zero-based based on the first data row and that choice is applied to all rows.

## Example (usage walkthrough, prose):
1. Open or otherwise obtain a schema source that is readable by agate.csv.reader. The schema must have a header row containing at least "column", "start", and "length", followed by one row per field describing the field name, start position, and length.
2. Instantiate the parser with that schema source. The constructor will read the header and build self.fields using SchemaDecoder; any schema-decoding error will raise ValueError indicating which schema line failed.
3. For each fixed-width record line (a text string), call parser.parse(line) to obtain the list of field values (trimmed), or parser.parse_dict(line) to obtain a dict mapping field names to values.
4. No explicit cleanup of the parser is necessary. If you opened the schema file, close it when finished.

### `csvkit.convert.fixed.FixedWidthRowParser.__init__` · *method*

## Summary:
Initializes the parser by reading a CSV-style schema and building self.fields — an ordered list of FixedWidthField descriptors (name, zero-based start, length) used to slice fixed-width records.

## Description:
This constructor runs during parser setup and is typically called immediately after obtaining a schema source (a file-like object or an iterable of CSV rows). Typical callers open or provide a schema stream and instantiate FixedWidthRowParser(schema) to produce a parser ready to parse fixed-width data lines.

Why this is its own method:
- It isolates schema-reading and descriptor construction from runtime parsing logic. SchemaDecoder handles header interpretation and per-row normalization; the constructor consumes the schema, builds the canonical list of field descriptors, and guarantees that parse/parse_dict can operate solely against in-memory descriptors.
- Centralizing schema reading here makes it easy to report schema-row errors with line numbers and prevents repeating header-parsing logic elsewhere.

## Args:
    schema (iterable[str] | file-like): An input acceptable to agate.csv.reader — commonly a text-mode file object or any iterable yielding CSV-formatted lines. The schema must include a header row containing the exact column names "column", "start", and "length" (case-sensitive). Each subsequent data row must provide corresponding values.

## Returns:
    None — as a constructor, it initializes instance state. On successful return:
      - self.fields is populated with zero or more FixedWidthField-like objects, one per schema data row.

## Raises:
    StopIteration
        If the provided schema yields no rows (i.e., there is no header). This happens when next(schema_reader) is called and the reader is exhausted; this exception is not caught.

    ValueError
        Two situations produce ValueError:
        1. If SchemaDecoder.__init__(header) detects a missing required column in the header, it raises ValueError with a message of the form "A column named \"<name>\" must exist in the schema file." That ValueError will propagate from the constructor (it is not caught here).
        2. If an exception occurs while decoding any schema *data row* (the per-row call to the SchemaDecoder instance), the constructor catches the exception and re-raises ValueError with the message "Error reading schema at line %i: %s" where the line number is 1-based in the schema file (header is line 1, so the first data row is reported as line 2). The original exception message is included after the colon.

    Other exceptions propagated from agate.csv.reader
        If agate.csv.reader(schema) raises (for example, because schema is not an appropriate input), those exceptions will propagate (not wrapped) to the caller.

## State Changes:
Attributes READ:
    - None of self's pre-existing attributes are read; the constructor constructs new state.

Attributes WRITTEN:
    - self.fields (list[FixedWidthField]): created as an empty list, then appended with one FixedWidthField-like object per schema data row. Each appended element is expected to have:
        - .name (str): field name
        - .start (int): zero-based start offset
        - .length (int): field character length

## Constraints:
Preconditions:
    - schema must be an iterable or file-like object accepted by agate.csv.reader.
    - The schema header must contain the exact column names 'column', 'start', and 'length'. If not, SchemaDecoder.__init__ will raise ValueError (see Raises).

Postconditions:
    - On success, self.fields is an ordered list of descriptors produced by SchemaDecoder(header) called for every schema data row. Each descriptor must be compatible with the parser's expectations (attributes .name, .start, .length).
    - If the schema had no data rows, self.fields will be an empty list.
    - If decoding a data row fails, the constructor raises ValueError and the FixedWidthRowParser instance is not successfully constructed.

## Side Effects:
    - Consumes the provided schema iterable/reader up through the end of the schema input; callers who opened a file must manage closing it themselves.
    - No external I/O (other than reading the supplied schema object) or network calls are made.
    - Errors encountered while decoding data rows are wrapped into a ValueError that includes the original exception message and a 1-based schema file line number for the failing row.

### `csvkit.convert.fixed.FixedWidthRowParser.parse` · *method*

## Summary:
Extracts and returns column values from a single fixed-width input line by slicing it according to the parser's configured field definitions; does not modify parser state.

## Description:
This method is the core per-line extraction routine for the FixedWidthRowParser. For each configured field (in order) it slices the provided input line from field.start up to field.start + field.length, strips surrounding whitespace, and returns the resulting list of values.

Known callers and lifecycle:
- FixedWidthRowParser.parse_dict (same class) calls this method to produce a list of values which it then pairs with headers to build a dict.
- Typical usage (not shown in this class) is: for each line of a fixed-width file, call parse(line) once to obtain the row values as a list; this occurs during the row-processing stage of a fixed-width-to-tabular conversion pipeline.

Why separate this logic:
- The method isolates the simple but repeatedly-used logic of slicing and trimming a single input line. Separating it keeps parsing code modular (so callers can get raw lists or dicts via parse_dict) and makes unit testing of the slice/trim behavior straightforward.

## Args:
    line (str or sequence): The input record to parse. Expected to be a text string (str). Any object supporting Python slicing and .strip() for the slice result (e.g., str) is acceptable; passing None or a non-sliceable object will raise a runtime error.

## Returns:
    list[str]: A list of strings, one element per configured field in self.fields, in the same order as self.fields.
    - Each element is the substring of line corresponding to the field's start/length, with leading and trailing whitespace removed by strip().
    - If the input line is shorter than a field's slice range, that slice yields a shorter string (possibly empty), and strip() is applied; the returned list still has the same length as self.fields.
    - The returned list length is exactly len(self.fields).

## Raises:
    - TypeError: If the provided line is not subscriptable/sliceable (for example, None), or if field.start or field.length are not integers (Python slicing will raise a TypeError).
    - AttributeError: If an entry in self.fields does not have the required attributes (.start and .length), attribute access will raise AttributeError.
    Note: The method itself does not explicitly raise custom exceptions; these are the standard runtime exceptions that may occur due to invalid inputs or malformed field definitions.

## State Changes:
    Attributes READ:
        - self.fields (list): Iterated to obtain field definitions.
        - For each field in self.fields: field.start (int), field.length (int) are read.
    Attributes WRITTEN:
        - None. This method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - self.fields must be an iterable (typically a list) of field descriptor objects, each exposing integer attributes .start and .length.
        - The caller should provide line as a text string (str). While other sliceable types may work, expected behavior and whitespace semantics assume text strings.
    Postconditions:
        - After completion, the parser's state is unchanged.
        - The returned list contains one element per configured field and contains only stripped strings (no leading/trailing whitespace).

## Side Effects:
    - None. The method performs no I/O, makes no external service calls, and does not mutate objects outside the scope of local variables and the return value.

## Example:
    Given self.fields = [fieldA(start=0,length=5), fieldB(start=5,length=10)] and
    line = "abc  defghijklm",
    parse(line) will return ["abc", "defghijklm"] (each element stripped of surrounding whitespace).

### `csvkit.convert.fixed.FixedWidthRowParser.parse_dict` · *method*

## Summary:
Return a mapping of header names to extracted field values for a single fixed-width input line; this produces a row-shaped dict without modifying the parser's state.

## Description:
Known callers and lifecycle:
- Commonly invoked by higher-level fixed-width-to-tabular conversion routines during the row-processing stage when a dictionary/record representation (header -> value) is required for downstream processing (for example, to build agate rows or to write output in a keyed format).
- Internally, this method is a thin convenience wrapper around the parser's list-based extraction routine: it calls the parser's parse(line) to obtain an ordered list of values and pairs those values with the parser's headers.

Why this is a separate method:
- Separating list extraction (parse) from header-to-value mapping (parse_dict) keeps responsibilities small and composable: callers that need raw lists can use parse, while callers that need keyed records can call parse_dict. This avoids duplicating the zip-and-dict creation logic across the codebase and makes both behaviors independently testable.

## Args:
    line (str or sliceable sequence):
        The input record to parse. Expected to be a text string (str) or another object supporting slicing that yields text substrings whose .strip() makes sense.
        - Passing None or a non-sliceable object will result in a runtime error from the underlying parse call.

## Returns:
    dict[str, str]:
        A dictionary mapping header names (strings) to extracted field values (strings).
        - Normally, there will be one entry per configured field (header) in self.fields.
        - If the number of headers and the number of parsed values differ (for example, if self.headers or self.fields were modified between calls), the pairing follows Python's zip semantics: only pairs up to the length of the shorter iterable are included.
        - If multiple fields share the same header name, the resulting dict will contain the last value provided for that header (standard dict behavior: later keys overwrite earlier ones).

## Raises:
    - Any exception raised by self.parse(line):
        * TypeError: if line is not sliceable/subscriptable; or if field.start/field.length are not valid integer indices.
        * AttributeError: if expected field attributes (.start, .length) are missing or if headers computation fails because a field lacks .name.
        These exceptions are not caught here and propagate to the caller.
    - The method itself does not raise custom exceptions.

## State Changes:
    Attributes READ:
        - self.headers (property): read to obtain the list of header names; this in turn reads self.fields and their .name attributes.
        - Through the call to self.parse(line): self.fields and each field's .start and .length attributes are read.
    Attributes WRITTEN:
        - None. This method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - self.fields must be a sequence/iterable of field descriptors, each exposing:
            * .name (str)
            * .start (int)
            * .length (int)
        - The caller must provide line as a text string (str) or another sliceable object where slicing returns a string-like object appropriate for .strip().
        - Do not concurrently mutate self.fields or field attributes while calling this method; changing fields between reading headers and parsing can cause mismatches.

    Postconditions:
        - The parser's internal state (self.fields and related attributes) remains unchanged.
        - The returned dict contains header->value pairs for each header/value pair produced by zip(self.headers, self.parse(line)); no other side effects occur.

## Side Effects:
    - None: the method performs no I/O and does not call external services. It only creates and returns a new dict based on in-memory data and the provided line.

## Examples:
    Given self.fields = [field(name='id', start=0, length=3), field(name='name', start=3, length=10)]
    and line = "001John Smith",
    parse(line) -> ["001", "John Smith"]
    parse_dict(line) -> {"id": "001", "name": "John Smith"}

    Notes on edge cases:
    - If a field's slice is shorter than its length because the input line is truncated, the corresponding value will be the stripped substring (possibly empty), and the dict will still include that header.
    - If self.fields contains duplicate .name values, the dict will retain the last value encountered for that key.
    - If self.headers and the list returned by parse(line) differ in length (for example due to external mutation), only the first min(len(headers), len(values)) pairs are present in the returned dict.

### `csvkit.convert.fixed.FixedWidthRowParser.headers` · *method*

## Summary:
Returns an ordered list of column names derived from the configured fixed-width fields, exposing the parser's header values without modifying parser state.

## Description:
Known callers and context:
- FixedWidthRowParser.parse_dict calls this property to build a mapping from header names to parsed values when converting a fixed-width line into a dict. This property is used during the data-parsing stage after the parser has been constructed and its schema (self.fields) initialized in __init__.
- It may also be used by external code that needs the ordered column names for output formatting, validation, or downstream mapping.

Why this logic is a separate property:
- Exposing header names as a property centralizes access to the schema-derived names and keeps parse_dict and other consumers simple and readable.
- As a read-only property it documents that header names are derived data (not something to be mutated through this interface).
- Separating this logic avoids duplicating the list-comprehension in multiple places and encapsulates the mapping from field objects to their name strings.

## Args:
None.

## Returns:
list
    A list containing, in order, the value of field.name for each element in self.fields.
    - If self.fields is empty, returns an empty list.
    - The length of the returned list equals len(self.fields).
    - Values are returned in the same order as fields appear in self.fields.
    - Typical element type: str (schema field names), but the method does not enforce the type of field.name.

## Raises:
AttributeError
    Raised if self.fields is missing (e.g., the instance is not properly initialized) or if any element in self.fields does not have a .name attribute. This arises from normal attribute access and is not explicitly raised in code.

## State Changes:
Attributes READ:
    - self.fields

Attributes WRITTEN:
    - None (this property does not modify any attribute on self)

## Constraints:
Preconditions:
    - The FixedWidthRowParser instance should have been initialized so that self.fields exists and is an iterable (typically a list) of field objects.
    - Each item in self.fields should expose a .name attribute (commonly a string) for meaningful header values.

Postconditions:
    - After calling, self remains unchanged.
    - The caller receives a list whose entries correspond one-to-one, in order, with the parser's configured fields.

## Side Effects:
    - None. This property performs no I/O, external service calls, or mutations of objects outside self.

## `csvkit.convert.fixed.SchemaDecoder` · *class*

## Summary:
SchemaDecoder is a callable helper that, given a header row describing a fixed-width schema, decodes subsequent schema rows into FixedWidthField instances by extracting the field name, start position, and length from each row.

## Description:
SchemaDecoder should be instantiated once per schema file using the header (an iterable of column names) that names the columns containing the field definition. It is designed to be used while reading a schema CSV-like file where each data row contains at least the columns "column", "start", and "length". Typical callers create a SchemaDecoder from the schema file header and then use it as a function to transform each schema row into a FixedWidthField object for downstream fixed-width parsing logic.

Motivation: Schema files may use a variety of conventions (start positions 0-based or 1-based). SchemaDecoder encapsulates the logic of locating the required columns in the header, determining whether the schema uses one-based starts by inspecting the first data row, and producing a canonical field description with a zero-based start and integer length. It enforces the boundary between reading raw schema rows and producing consistent field descriptors for the fixed-width reader.

## State:
- Class attributes (set during initialization and use)
  - REQUIRED_COLUMNS: list[tuple[str, type|None]]
    - Value: [('column', None), ('start', int), ('length', int)]
    - Purpose: Defines the required column names in the header and an optional "val_type" flag used at init time.
  - column: int
    - Meaning: index (0-based) into a schema-row sequence that yields the field name. Set in __init__ to header.index('column').
    - Constraint: integer >= 0 and less than header length. Must not be changed by callers.
  - start: int
    - Meaning: index into a schema-row sequence that yields the start position string/value. Set in __init__ to header.index('start').
    - Constraint: integer >= 0 and less than header length.
  - length: int
    - Meaning: index into a schema-row sequence that yields the field length string/value. Set in __init__ to header.index('length').
    - Constraint: integer >= 0 and less than header length.
  - one_based: bool | None
    - Meaning: determined on the first data row processed; True if the schema's start positions are 1-based, False if 0-based. None until the first call.
    - Invariants: once set to True or False, it remains constant for the instance and is used for all subsequent rows.

Class invariants:
- After __init__, column, start, and length are integers that are valid indices into any schema-row sequence produced from the same file format.
- one_based is either None (no rows processed yet) or a boolean determined by the first row; all subsequent rows are interpreted using that same one_based value.

## Lifecycle:
- Creation:
  - Instantiate with header: SchemaDecoder(header)
    - header: sequence (e.g., list or tuple) of strings representing column names from the schema file header.
    - Required: header must contain the strings "column", "start", and "length" (case-sensitive).
  - Example instantiation: decoder = SchemaDecoder(['column', 'start', 'length'])
- Usage:
  - After creation, call the instance with each schema data row: field = decoder(row)
    - row: sequence (e.g., list/tuple) of cell values corresponding to header columns.
    - On the first call, SchemaDecoder sets its one_based flag by evaluating whether int(row[self.start]) == 1.
    - For each call, SchemaDecoder:
      1. Reads the raw start value from row[self.start] and converts it to int.
      2. Adjusts the start to be zero-based if one_based is True (subtracts 1).
      3. Reads the length value from row[self.length] and converts it to int.
      4. Reads the column name from row[self.column] (kept as-is).
      5. Returns FixedWidthField(column_name, adjusted_start, length_as_int).
  - Typical ordering: instantiate -> call repeatedly for each row in file -> pass resulting FixedWidthField objects into the fixed-width parser builder.
- Destruction:
  - No explicit cleanup required. SchemaDecoder does not hold external resources.

## Method Map:
graph LR
    A[__init__(header)] --> B[set attributes: column,start,length]
    B --> C[__call__(row)]
    C --> D[determine one_based on first row]
    C --> E[compute adjusted_start]
    C --> F[return FixedWidthField(name, adjusted_start, length)]

(Above is a simple flow: instantiate then call many times. The __call__ operation depends on FixedWidthField factory/class.)

## Expected FixedWidthField contract (dependency):
SchemaDecoder returns whatever FixedWidthField resolves to in the module scope. To implement the consuming code, FixedWidthField should be a callable (class or factory function) accepting three positional arguments:
- name: str — the field name (taken directly from row[self.column])
- start: int — the zero-based start offset inside a record (adjusted for one-based input)
- length: int — number of characters for the field (as int)

A minimal compatible implementation example (for implementer reference) is a simple namedtuple-like triple or a dataclass with attributes .name, .start, .length.

## Raises:
- __init__(header)
  - ValueError: raised when any of the required column names "column", "start", or "length" are not found in header. Message: A column named "<name>" must exist in the schema file.
- __call__(row)
  - IndexError: if the row sequence is shorter than expected and indexing row[self.start], row[self.length], or row[self.column] fails.
  - ValueError: if the text found in the start or length column cannot be converted to int (e.g., empty string, non-numeric text).
  - TypeError: if row is not subscriptable (missing __getitem__) or contains values incompatible with int() conversion; these are the standard exceptions raised by Python built-ins.

Note: The class intentionally defers numeric conversion errors to the built-in int() conversion so callers may see ValueError with the original problematic string.

## Edge cases and constraints:
- Header matching is case-sensitive (uses header.index('column')).
- The determination of one_based uses only the first row processed; mixed conventions across rows will be interpreted according to the first row and may lead to incorrect start calculations for later rows.
- If a schema file legitimately uses 1-based starts, the first row must contain a start value equal to 1 to trigger one_based=True.
- Negative starts or lengths are not explicitly checked here; int() conversion will succeed for negative numbers, but their semantics for fixed-width parsing are likely invalid. Upstream code should validate range constraints if required.

## Example:
- Instantiate with a header that contains the required column names.
  - header = ['column', 'start', 'length', 'description']
  - decoder = SchemaDecoder(header)
- Process rows (each row is a sequence aligned with header):
  - row = ['first_name', '1', '10', 'First name field']
  - field = decoder(row)  # Determines one_based from this first call; returns FixedWidthField('first_name', 0, 10)
- On subsequent rows, decoder will reuse the same one_based setting:
  - row2 = ['last_name', '11', '15', 'Last name field']
  - field2 = decoder(row2)  # returns FixedWidthField('last_name', 10, 15)

Implementation note: If FixedWidthField is not present in the codebase, implement a small container with attributes (.name, .start, .length) to receive the three values returned by SchemaDecoder.

### `csvkit.convert.fixed.SchemaDecoder.__init__` · *method*

## Summary:
Initializes the decoder by locating required column names in the provided header and setting instance attributes for each required column to the index (or the result of applying an optional conversion callable) of that column in the header.

## Description:
This constructor is called once when a SchemaDecoder is created for a schema file. Typical usage is at the start of schema processing: instantiate SchemaDecoder(header) where header is the sequence of column names from the schema file; later the instance is used to decode each data row. The method is separated from decoding logic so that header validation and attribute binding happen once at construction time rather than repeated for each row.

Known callers / lifecycle stage:
- Instantiated during schema file processing before any data rows are converted (for example: decoder = SchemaDecoder(header)). It prepares the decoder for repeated calls (decoder(row)) that transform schema rows into fixed-width field descriptors.

Why this is a separate method:
- Header parsing and verification are one-time operations; isolating them in __init__ ensures attribute setup and early failure (missing columns) instead of repeating work for every data row. It enforces the class invariant that required attribute names map to integer indices (or converted indices) for all subsequent operations.

## Args:
    header (Sequence[str]):
        A sequence (e.g., list or tuple) of column name strings representing the schema file header.
        - Required properties: supports header.index(value) and contains the required column names defined by self.REQUIRED_COLUMNS.
        - Case-sensitive matching: exact string equality is used when searching.

## Returns:
    None
    - The constructor does not return a value; it configures the instance by setting attributes.

## Raises:
    ValueError:
        Raised when any required column name (each p in self.REQUIRED_COLUMNS) is not found in header.
        Exact message emitted: A column named "<p>" must exist in the schema file.
        This is triggered by header.index(p) raising ValueError and being caught and re-raised with the above message.

    (Note: other exceptions raised by calling header.index (e.g., AttributeError if header lacks index()) or by val_type(header.index(p)) may propagate, but only the missing-column case is explicitly caught and re-raised by this method.)

## State Changes:
Attributes READ:
    - self.REQUIRED_COLUMNS

Attributes WRITTEN:
    - For each tuple (p, val_type) in self.REQUIRED_COLUMNS, this method sets an attribute named p on self:
        - If val_type is truthy (callable), sets self.<p> = val_type(header.index(p))
        - If val_type is falsy (e.g., None), sets self.<p> = header.index(p)
    - Common concrete result (based on typical REQUIRED_COLUMNS): sets self.column, self.start, self.length to integer index values (or conversion results) corresponding to their column positions in header.

## Constraints:
Preconditions:
    - header must be a sequence-like object that implements .index(value) (for example, list or tuple of strings).
    - header must contain each column name p present in self.REQUIRED_COLUMNS; matching is exact and case-sensitive.
    - Each val_type in self.REQUIRED_COLUMNS, if present and intended to transform the index, should be a callable that accepts a single int argument. The code will call val_type(header.index(p)).

Postconditions:
    - After successful return, for every (p, val_type) in self.REQUIRED_COLUMNS an attribute self.<p> exists.
        - If val_type was provided, self.<p> == val_type(header.index(p))
        - Otherwise, self.<p> == header.index(p)
    - No return value is produced; object is ready for row decoding operations that rely on these attributes.

## Side Effects:
    - Mutates the instance by adding or updating attributes named after each required column.
    - Does not perform I/O or call external services.
    - No global state is mutated.

## Implementation notes / edge cases:
    - The method re-raises a ValueError with a clear message when a required column is missing, ensuring early and specific failure for common misconfiguration.
    - If self.REQUIRED_COLUMNS is not defined on the class, attribute access will fail before any header lookup; callers should ensure the class-level REQUIRED_COLUMNS is present and correctly formed as an iterable of (name, val_type) tuples.
    - val_type is applied to the index integer (i.e., val_type(header.index(p))). If val_type is int this effectively returns the same integer; if val_type is a different callable it may transform the index before assignment.
    - Because header.index performs exact matching, variations in capitalization or whitespace in header strings cause the constructor to raise ValueError for missing columns.

### `csvkit.convert.fixed.SchemaDecoder.__call__` · *method*

## Summary:
Convert a schema-row (sequence of values) into a FixedWidthField descriptor, normalizing the field start to 0-based indexing and updating the decoder's one_based discovery flag.

## Description:
This callable is used during schema parsing to transform a single row from the schema CSV into a fixed-width field descriptor. Typical callers: CSV/row iteration logic that reads a schema file and maps each schema row through SchemaDecoder to produce a sequence of field definitions; i.e., it is invoked once per schema row during the schema-parsing stage of a fixed-width conversion pipeline.

This logic is implemented as a method on a stateful SchemaDecoder object because:
- It needs to determine whether the schema's "start" values are 1-based or 0-based by inspecting the first data row it receives (it stores that decision on the instance).
- It must produce a reusable field descriptor for each row while using the decoder's stored column index configuration created from the schema header.

## Args:
    row (Sequence): An indexable sequence (e.g., list or tuple) representing a parsed schema CSV row. The sequence must contain values at the indices self.start, self.length, and self.column (these indices are integers set by SchemaDecoder.__init__). Values at these positions are typically strings (e.g., '1', '10', 'field_name') that are convertible to the expected types.

## Returns:
    FixedWidthField: An object representing a fixed-width field, constructed as:
        FixedWidthField(name, start, length)
    where:
        - name (str): value taken from row[self.column]
        - start (int): 0-based start position for this field (adjusted from the schema's value)
        - length (int): length of the field as an integer (int(row[self.length]))

    Edge cases:
        - If row[self.length] or row[self.start] cannot be converted to int, int(...) will raise ValueError or TypeError (see Raises).
        - If row lacks the required index positions, IndexError will be raised.

## Raises:
    IndexError: If the provided row is too short and does not contain entries at self.start, self.length, or self.column.
    ValueError: If int(row[self.start]) or int(row[self.length]) fails because the string is not a valid integer literal.
    TypeError: If the values at the required positions are of a type that int(...) cannot handle (e.g., None).
    (Note: These exceptions are not explicitly raised by this method but are direct consequences of indexing and int(...) conversion used here.)

## State Changes:
    Attributes READ:
        - self.one_based: read to determine whether start values should be adjusted (only read after possible initialization below).
        - self.start: index into row where the raw start value is stored.
        - self.length: index into row where the raw length value is stored.
        - self.column: index into row where the field name value is stored.

    Attributes WRITTEN:
        - self.one_based: if currently None, it is set to a boolean computed as (int(row[self.start]) == 1). Subsequent calls will not overwrite this attribute.

## Constraints:
    Preconditions:
        - SchemaDecoder.__init__ must have previously run successfully, so that self.start, self.length, and self.column are integer indices (set from the schema header). If these are not set to valid integer indices, this method will raise IndexError or TypeError/ValueError during conversion.
        - The provided row must be indexable and contain values at the indices specified by self.start, self.length, self.column.
        - row[self.start] and row[self.length] must be convertible to int.

    Postconditions:
        - self.one_based is guaranteed to be a boolean after the first call that reaches the discovery branch (i.e., after the first row is processed, self.one_based will no longer be None).
        - The returned FixedWidthField.start value is guaranteed to be 0-based (i.e., adjusted_start >= 0).
        - The returned FixedWidthField.length is an int converted from row[self.length].

## Side Effects:
    - No I/O or external service calls are performed.
    - The only external mutation is the potential update of the instance attribute self.one_based.
    - No mutation of the input row is performed.

## Implementation notes / reimplementation tips:
    - Determine whether schema start indices are 1-based by checking the first row: set self.one_based = (int(row[self.start]) == 1) only if self.one_based is None.
    - Compute adjusted_start = int(row[self.start]) - 1 when one_based is True; otherwise adjusted_start = int(row[self.start]).
    - Construct and return FixedWidthField(row[self.column], adjusted_start, int(row[self.length])).
    - Be explicit about exception propagation: let IndexError, ValueError, or TypeError propagate to the caller so they can surface malformed schema rows.

