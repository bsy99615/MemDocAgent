# `csvstat.py`

## `csvkit.utilities.csvstat.CSVStat` · *class*

*No documentation generated.*

### `csvkit.utilities.csvstat.CSVStat.add_arguments` · *method*

## Summary:
Populate the utility's argument parser with all command-line options supported by the CSVStat utility, registering flags and their destinations so the parser will produce the expected attributes on parsed args.

## Description:
This method is called during CLI initialization by the CSVKit utility framework (the CSVKitUtility-based CLI bootstrap) to add CSVStat-specific command-line options to its ArgumentParser before parse_args is invoked. Typical lifecycle: when the CLI program creates or configures the argument parser for this utility, it calls this method to register all flags; later the framework calls parse_args() to produce self.args used by main().

This logic is separated into its own method because:
- It keeps argument registration distinct from parsing and runtime logic (clean separation of responsibilities).
- It allows the CSVKitUtility framework to iterate or compose arguments across multiple utilities consistently.
- It centralizes flag definitions (names, types, defaults, help text) in one place for maintainability and testability.

## Args:
None (no direct parameters). The method operates on self and uses the following attribute:
- self.argparser (required): an argparse-like parser object with add_argument(name_or_flags..., **kwargs).

## Registered command-line options (flag -> dest, type, default, short description):
- --csv
  - dest: csv_output
  - type: bool flag (action='store_true')
  - default: False
  - help: Output results as a CSV table, rather than plain text.
- --json
  - dest: json_output
  - type: bool flag
  - default: False
  - help: Output results as JSON text, rather than plain text.
- -i, --indent
  - dest: indent
  - type: int
  - default: None (not set unless provided)
  - help: Indent the output JSON this many spaces. Disabled by default.
- -n, --names
  - dest: names_only
  - type: bool flag
  - default: False
  - help: Display column names and indices from the input CSV and exit.
- -c, --columns
  - dest: columns
  - type: str
  - default: None
  - help: Comma-separated list of column indices, names or ranges to be examined (e.g. "1,id,3-5"); defaults to all columns.
- --type
  - dest: type_only
  - type: bool flag
  - default: False
  - help: Only output data type.
- --nulls
  - dest: nulls_only
  - type: bool flag
  - default: False
  - help: Only output whether columns contain nulls.
- --non-nulls
  - dest: nonnulls_only
  - type: bool flag
  - default: False
  - help: Only output counts of non-null values.
- --unique
  - dest: unique_only
  - type: bool flag
  - default: False
  - help: Only output counts of unique values.
- --min
  - dest: min_only
  - type: bool flag
  - default: False
  - help: Only output smallest values.
- --max
  - dest: max_only
  - type: bool flag
  - default: False
  - help: Only output largest values.
- --sum
  - dest: sum_only
  - type: bool flag
  - default: False
  - help: Only output sums.
- --mean
  - dest: mean_only
  - type: bool flag
  - default: False
  - help: Only output means.
- --median
  - dest: median_only
  - type: bool flag
  - default: False
  - help: Only output medians.
- --stdev
  - dest: stdev_only
  - type: bool flag
  - default: False
  - help: Only output standard deviations.
- --len
  - dest: len_only
  - type: bool flag
  - default: False
  - help: Only output the length of the longest values.
- --max-precision
  - dest: maxprecision_only
  - type: bool flag
  - default: False
  - help: Only output the most decimal places.
- --freq
  - dest: freq_only
  - type: bool flag
  - default: False
  - help: Only output lists of frequent values.
- --freq-count
  - dest: freq_count
  - type: int
  - default: None
  - help: The maximum number of frequent values to display.
- --count
  - dest: count_only
  - type: bool flag
  - default: False
  - help: Only output total row count.
- --decimal-format
  - dest: decimal_format
  - type: str
  - default: '%.3f'
  - help: %-format specification for printing decimal numbers. Defaults to locale-specific formatting with "%.3f".
- -G, --no-grouping-separator
  - dest: no_grouping_separator
  - type: bool flag
  - default: False
  - help: Do not use grouping separators in decimal numbers.
- -y, --snifflimit
  - dest: sniff_limit
  - type: int
  - default: 1024
  - help: Limit CSV dialect sniffing to the specified number of bytes. Use 0 to disable sniffing entirely, or -1 to sniff the entire file.
- -I, --no-inference
  - dest: no_inference
  - type: bool flag
  - default: False
  - help: Disable type inference when parsing the input. Disable reformatting of values.

## Returns:
- None. The method registers arguments on self.argparser and does not return a value.

## Raises:
- AttributeError: if self.argparser is not present (None or missing) or does not implement add_argument.
- TypeError or ValueError: may be raised by the underlying argument parser's add_argument implementation if called with invalid parameters or conflicting option strings.
- Note: add_arguments itself does not perform validation of semantic conflicts between options (e.g., mutually exclusive usage of --csv with certain operation flags) — such validation occurs later in main().

## State Changes:
- Attributes READ:
  - self.argparser (reads to call add_argument)
- Attributes WRITTEN / Mutated:
  - self.argparser: multiple new argument specifications are added; the parser's internal option/argument tables are mutated so parse_args() will populate the corresponding dest attributes on the resulting args object.
- No other attributes of self are read or modified by this method.

## Constraints:
- Preconditions:
  - self.argparser must be initialized and must implement add_argument(name_or_flags..., **kwargs) (e.g., an argparse.ArgumentParser or compatible API).
  - The environment should supply appropriate locale/encoding only if help rendering depends on it (not required for registration).
- Postconditions:
  - After calling this method, the parser referenced by self.argparser will accept all listed flags and, when parse_args() is called, will produce an args object containing the named destinations and types described above (unless the underlying parser applies different behavior).
  - No runtime validation of inter-option constraints is guaranteed by this method.

## Side Effects:
- Mutates the provided argument parser (self.argparser) by registering a comprehensive set of CLI options.
- No I/O is performed, and no external services are called.
- Because help text uses percent-format specifiers in some strings, these help strings are stored as-is on the parser; they do not perform formatting at registration time.

### `csvkit.utilities.csvstat.CSVStat.main` · *method*

## Summary:
Execute the csvstat command-line workflow: validate CLI arguments, read input CSV data into an agate Table, compute requested statistics or a single requested operation for the selected columns, and emit results to the configured output (human-readable text, CSV, JSON, or simple line count). This method is the CLI entrypoint that drives the utility's high-level control flow and produces observable output; it does not return a value.

## Description:
- Known callers / invocation context:
    - This method is intended to be invoked as the command-line entrypoint of the CSVStat utility class when the csvstat CLI action is run. It is executed during the CLI lifecycle after argument parsing and before the process exits. In practice, the CSVKit CLI runner instantiates CSVStat (a CSVKitUtility subclass) and calls main() to perform the utility's work.
- Why this logic is a separate method:
    - main encapsulates the complete CLI execution flow (argument validation, input acquisition, table construction, operation selection, and output formatting). Separating it as an instance method keeps the entrypoint logic centralized and testable, while allowing helper methods (print_column_names, calculate_stats, print_csv, etc.) to implement the detailed behaviors. It avoids inlining procedural code in the class constructor or external scripts and enables subclassing or unit-testing of the CLI workflow.

## Args:
    None (method signature: def main(self)). The method uses attributes on self.args and other instance attributes described below; callers should prepare those attributes via the usual CSVKit/argparse setup before invoking main.

## Returns:
    None
    - All observable outputs are produced via side effects (writing to self.output_file, calling self.argparser.error which triggers an error exit, or printing via helper methods). The method uses explicit `return` only to stop further processing; no meaningful value is returned.

## Raises:
    - Calls to self.argparser.error(...) in multiple validation branches:
        * If no input is provided but additional_input_expected() returns True: raises an argparse error via self.argparser.error('You must provide an input file or piped data.').
        * If more than one mutually-exclusive operation flag is provided: error('Only one operation argument may be specified (--mean, --median, etc).').
        * If an operation is requested together with --csv, --json, or --count: error('You may not specify --csv and an operation ...') or similar messages for json/count.
      (Note: self.argparser.error is invoked directly; its behavior (typically causing program exit / SystemExit) is delegated to the argument parser implementation.)
    - Exceptions raised by CSV parsing and table construction:
        * agate.Table.from_csv(...) may raise file I/O errors, parsing errors, or agate-specific exceptions; these propagate unless caught by callers.
        * agate.csv.reader(...) used for count-only mode can raise I/O/parsing errors that will propagate.
    - Any exceptions raised by helper methods invoked here (e.g., self.get_column_types, parse_column_identifiers, self.calculate_stats, self.print_* methods) are propagated.

## State Changes:
- Attributes READ:
    - self.args.names_only
    - self.args.count_only
    - self.args.no_header_row
    - self.args.sniff_limit
    - self.args.skip_lines
    - self.args.columns
    - self.args.csv_output
    - self.args.json_output
    - self.args.freq_count
    - self.argparser (used to call argparser.error)
    - self.reader_kwargs (passed into CSV reader / agate.Table.from_csv)
    - self.input_file (passed to agate.Table.from_csv)
    - self.output_file (used for write in count-only mode and may be used by print_* helpers)
    - self.get_column_types() (method called to obtain column_types)
    - self.get_column_offset() (method called to compute column offset for parse_column_identifiers)
    - self.additional_input_expected() (method called to validate input presence)
    - self.skip_lines() (method called to obtain an input iterator for counting)
    - parse_column_identifiers (module-level helper used to convert CLI column specs to internal column identifiers)
- Attributes WRITTEN:
    - None directly. The method does not assign to any self.<attr> fields. It does, however, produce external side effects (writing to files, printing).

## Constraints:
- Preconditions:
    - The instance must have a populated self.args namespace with the expected attributes (names_only, count_only, no_header_row, sniff_limit, skip_lines, columns, csv_output, json_output, freq_count). Typically, this is satisfied by the CSVKit argument parsing and initialization.
    - self.input_file must be a readable file-like object or path acceptable to agate.Table.from_csv.
    - self.output_file must be a writable file-like object for textual output.
    - Helper methods used here (get_column_types, get_column_offset, calculate_stats, print_one, print_csv, print_json, print_stats, print_column_names, skip_lines, additional_input_expected) must be present and operate according to their contracts; main delegates detailed behavior to them.
- Postconditions:
    - If execution completes normally (no argparser.error path and no uncaught exceptions), one of the following will have occurred:
        * If names_only: column names have been printed via self.print_column_names(), then method returned.
        * If count_only: the number of data rows (header excluded unless no_header_row is set) has been written to self.output_file and method returned.
        * Otherwise: an agate.Table has been constructed from input, requested operation(s) or statistics have been computed for the selected column(s), and results emitted via one of self.print_one, self.print_stats, self.print_csv, or self.print_json depending on flags.
    - No instance attributes are mutated by main itself; the core effect is external I/O/output produced by helper methods.

## Side Effects:
- I/O:
    - Reads input via agate.Table.from_csv(self.input_file, ...), which consumes the input CSV (may open files and read streams).
    - In count-only mode, iterates self.skip_lines() through agate.csv.reader(...) to compute line count.
    - Writes textual output:
        * count-only: writes a single integer followed by newline to self.output_file.
        * Other modes: delegates formatted output to print_one / print_stats / print_csv / print_json which write to self.output_file or stdout as implemented.
- Process control / exit:
    - Calls self.argparser.error(...) to signal CLI validation failures; that call delegates to the argument parser and typically terminates the process (e.g., by raising SystemExit).
- Memory / CPU:
    - Constructs an agate.Table for the full input (may require memory proportional to input size) unless a helper implements streaming; caller should be aware of potential memory usage for large inputs.
- Delegation:
    - The method delegates most detailed computation and formatting to helper methods (calculate_stats, print_one, print_stats, print_csv, print_json). Any side effects performed by those helpers (file writes, logging, warnings) are part of the overall side effects of main.

### `csvkit.utilities.csvstat.CSVStat.is_finite_decimal` · *method*

## Summary:
Return True when the given value is a Decimal instance representing a finite number (not NaN or infinite); otherwise return False. This is a pure predicate used to decide whether numeric Decimal results should be formatted for output.

## Description:
Known callers and context:
- CSVStat._calculate_stat: Called after an aggregation to determine whether the aggregated value (v) is a finite Decimal and therefore should be formatted (via format_decimal) before being returned or printed. This is part of the statistics calculation / output-preparation pipeline.
- CSVStat.print_stats (freq formatting branch): Called when iterating frequency rows for a numeric column to determine whether a freq row's value is a finite Decimal and needs formatting.
Indirect callers (via _calculate_stat / print_stats):
- CSVStat.print_one and CSVStat.calculate_stats call into _calculate_stat, and therefore may cause this predicate to be evaluated during generation of per-column outputs.

Why this is a separate method:
- Centralizes the exact check for Decimal finiteness in one place so formatting decisions are consistent across the codebase.
- Improves readability and testability compared to inlining the isinstance + is_finite check at each call site.

## Args:
    value (any): The value to test. Typically the result of an agate aggregation or a column value; may be any object. No default.

## Returns:
    bool: True if and only if:
        - value is an instance of decimal.Decimal (or a subclass), and
        - value.is_finite() returns True (i.e., the Decimal is neither NaN nor infinite).
    Returns False for:
        - non-Decimal values,
        - Decimal('NaN'),
        - Decimal('Infinity') or Decimal('-Infinity'),
        and any other Decimal for which is_finite() is False.

## Raises:
    None: The method performs safe type checking and calls Decimal.is_finite() only on objects confirmed to be instances of Decimal, so it will not raise due to type errors.

## State Changes:
    Attributes READ: None (does not read any self.<attr> attributes)
    Attributes WRITTEN: None (no modifications to self)

## Constraints:
    Preconditions:
        - None required: the method accepts any Python object as input.
    Postconditions:
        - The method returns a boolean and leaves the CSVStat instance and all other objects unchanged.

## Side Effects:
    - None. The method performs no I/O, does not call external services, and does not mutate objects outside of its local scope.

### `csvkit.utilities.csvstat.CSVStat._calculate_stat` · *method*

*No documentation generated.*

### `csvkit.utilities.csvstat.CSVStat.print_one` · *method*

## Summary:
Prints a single computed statistic for a specified column of an agate.Table to the utility's configured output stream, optionally prefixed with a numbered label. Special-cases the 'freq' operation by rendering a compact mapping-style string.

## Description:
- Known callers and invocation context:
    - CSVStat.main: used during the CLI output stage.
        * When main is invoked with exactly one requested operation and a single column, it calls print_one(..., label=False) to emit just the value (suitable for scripting or piping).
        * When main iterates over multiple columns for a selected operation, it calls print_one(...) with the default label=True to produce numbered, human-readable lines for each column.
    - This method is invoked after computation/delegation to self._calculate_stat; it is responsible only for formatting and writing the single-stat output.
- Why this logic is a separate method:
    - Consolidates per-column formatting (numbering, column name inclusion, newline termination) and the 'freq' formatting rule in one place so all callers produce consistent output without duplicating logic. This separation also makes unit-testing and potential future changes (different label styles or output streams) straightforward.

## Args:
    table (agate.Table)
        The table containing the data and column metadata. Must expose column_names (indexable sequence of strings).
    column_id (int)
        Zero-based index of the target column in table.column_names. Must be a valid index.
    op_name (str)
        Operation key to compute/format (for example: 'mean', 'median', 'freq', 'count', etc.). Must be a key present in the module-level OPERATIONS mapping used by _calculate_stat.
    label (bool, default True)
        If True, writes a labeled line of the form "  n. column_name: stat" (column number is 1-based and right-aligned to width 3). If False, writes only the stat followed by a newline.
    **kwargs
        Forwarded to self._calculate_stat. Accepts operation-specific parameters (for example, 'freq_count' to limit how many frequent values are returned). Valid keys and value types depend on the operation/generator used by _calculate_stat.

## Returns:
    None
    - No value is returned. The method's effect is the side-effect of writing a single line to self.output_file.
    - Examples of exact written lines:
        * Labeled (label=True): "  3. column_name: 12.345\n"
        * Unlabeled (label=False): "12.345\n"
        * Frequency output (op_name == 'freq'): "{ "foo": 5, "bar": 3 }\n"
        * When the statistic is None: "None\n" (or "  3. column_name: None\n" if labeled)

## Raises:
    - IndexError:
        * If column_id is out-of-range for table.column_names, attempting to index table.column_names[column_id] raises IndexError.
    - KeyError:
        * If op_name is not present in the module-level OPERATIONS mapping, indexing OPERATIONS[op_name] raises KeyError before calling _calculate_stat.
    - TypeError / AttributeError / KeyError (formatting-related):
        * For op_name == 'freq', the method expects the value returned by _calculate_stat to be an iterable of mapping-like rows with keys 'value' and 'count'. If the returned stat is None, not iterable, or rows lack these keys, the list comprehension or subsequent formatting will raise TypeError/AttributeError/KeyError.
    - IOError / OSError:
        * Any I/O error raised by self.output_file.write (for example, broken pipe or closed stream) will propagate.
    - Exceptions from self._calculate_stat:
        * Any exception that propagates out of _calculate_stat (for example, from agate aggregations or custom getters) will propagate through print_one. Note that _calculate_stat may swallow some exceptions internally, but not all operation-specific code is guaranteed to be swallowed.

## State Changes:
- Attributes READ:
    - self.output_file (write method is invoked)
    - self._calculate_stat (invoked to compute the statistic; that method may read other self attributes)
    - module-level OPERATIONS (looked up for op_name)
- Attributes WRITTEN:
    - None (the method does not modify self attributes; effects are external writes to the output stream).

## Constraints:
- Preconditions:
    - table must be a valid agate.Table-like object exposing column_names.
    - column_id must be a valid zero-based index into table.column_names.
    - op_name must exist as a key in OPERATIONS used by _calculate_stat.
    - If op_name == 'freq', the returned stat from _calculate_stat must be an iterable of mappings each containing 'value' and 'count'.
    - self.output_file must be a writable text stream implementing write(str).
- Postconditions:
    - A single formatted line representing the statistic for the specified column has been written to self.output_file.
    - No instance attributes on self are mutated.

## Side Effects:
    - Writes to external I/O: uses self.output_file.write to output the formatted string (this may write to stdout, a file, or another stream provided by the CLI harness).
    - Delegates to self._calculate_stat, which may perform computation (including agate aggregations), formatting (for Decimal values), and may emit warnings. Those side effects are considered part of this method's observable behavior.
    - No global variables or self attributes are modified by this method.

## Examples:
    - Typical labeled output for a numeric mean:
        1. age: 34.567
      (Where "1." is the 1-based column number right-aligned)
    - Unlabeled output mode used for scripting (label=False):
        34.567
    - Frequency output for a column with the top two values:
        { "US": 120, "CA": 30 }
    - When no statistic is available (stat is None), the literal string "None" is written (with or without label, depending on the label argument).

### `csvkit.utilities.csvstat.CSVStat.calculate_stats` · *method*

## Summary:
Return a mapping of every supported operation to its computed statistic for a single column, without mutating the CSVStat instance.

## Description:
Known callers and context:
- CSVStat.main: When no single operation flag is specified, main builds a stats dict per column by calling this method for each selected column (see CSVStat.main where stats[column_id] = self.calculate_stats(table, column_id, **kwargs)).
- Other internal code: print_stats, print_csv and print_json consume the mapping produced by main; print_one calls _calculate_stat directly for a single operation.

Why this is a separate method:
- Encapsulates the common pattern of iterating all operations (the OPERATIONS mapping) and delegating each calculation to _calculate_stat.
- Keeps calling code simple (main and any other callers) by returning a complete per-operation mapping for a column in one call, rather than requiring callers to duplicate the iteration and call _calculate_stat repeatedly.

## Args:
    table (agate.Table): The loaded table object whose column will be analyzed. Must be a valid agate Table instance produced by agate.Table.from_csv or equivalent.
    column_id (int): Zero-based index of the column to analyze in table.column_names / table.columns. Expected to be within the valid column index range for the table.
    **kwargs: Arbitrary keyword arguments forwarded unchanged to self._calculate_stat for each operation. Typical keys used by callers include:
        - freq_count (int): maximum number of frequent values to return for the 'freq' operation.
    Notes:
        - calculate_stats does not validate kwargs; they are passed through to the underlying getters/aggregations.

## Returns:
    dict[str, Any]: A mapping whose keys are the operation names from the module-level OPERATIONS mapping and whose values are the computed statistics for the specified column.
    - Values are the raw results returned by self._calculate_stat for each operation.
    - Possible value types include numeric types (e.g., Decimal), strings (e.g., formatted decimals returned when formatting is applied), lists/dicts (e.g., the 'freq' operation returns a list of rows like {'value', 'count'}), or None.
    - If an individual operation calculation fails or raises an exception, _calculate_stat swallows the exception and returns None; therefore, calculate_stats will contain None for that operation.

## Raises:
    This method does not explicitly raise any exceptions itself.
    - If column_id is out of range for the provided table, downstream calls inside _calculate_stat (or agate internals) may raise IndexError or other errors; calculate_stats does not perform bounds checking.
    - If OPERATIONS is not defined or is malformed, a NameError/TypeError may occur at runtime (OPERATIONS is expected to be a module-level mapping).

## State Changes:
    Attributes READ:
        - None directly. This method does not directly read any self.<attr> fields.
        - Note: the delegated method self._calculate_stat may read self.args and other attributes; those are not read directly by calculate_stats itself.
    Attributes WRITTEN:
        - None. calculate_stats does not modify self or any of its attributes.

## Constraints:
    Preconditions:
        - table should be a valid agate.Table with an accessible column at index column_id.
        - The OPERATIONS mapping must be an iterable mapping of operation_name -> operation_metadata available at module scope.
    Postconditions:
        - Returns a mapping containing one entry for every operation key present in OPERATIONS (same keys and iteration order as OPERATIONS.items()).
        - No mutation of self or table is performed by calculate_stats itself.

## Side Effects:
    - Calls self._calculate_stat repeatedly; effects produced by those calls (e.g., formatting decimals, aggregating data via agate, suppressed warnings) are side effects of the delegated work but are not caused directly by calculate_stats beyond invoking the method.
    - Does not perform I/O, logging, or writes to external services itself.

### `csvkit.utilities.csvstat.CSVStat.print_stats` · *method*

## Summary:
Write human-readable descriptive statistics for a set of columns from an agate Table to the utility's configured output file; this method renders per-column labeled statistics (including frequency lists) and a final row count, but does not modify the CSVStat object's persistent state.

## Description:
Known callers and call context:
- CSVStat.main invokes this method when the user requests plain-text output (neither --csv nor --json) and multiple columns are being reported. In main, after calculate_stats produces a mapping of statistics for each requested column, main calls print_stats(table, column_ids, stats) as the final presentation step.
- Typical lifecycle stage: the final presentation/printing phase after statistics are computed for the requested columns.

Why this is a separate method:
- Encapsulates the plain-text presentation logic for multiple columns: alignment of labels, special rendering for frequency lists, value formatting for numeric entries, and final row-count summary. Separating rendering from computation (calculate_stats/_calculate_stat) keeps concerns distinct and allows other output formats (CSV, JSON) to reuse the computed stats without duplicating presentation code.

## Args:
    table (agate.Table):
        The table object containing data and metadata. Expected to expose:
        - table.column_names: sequence of column name strings (indexable by integer column_id)
        - table.columns: sequence of column objects; each column object must expose a data_type attribute (compared against agate.Number)
        - table.rows: sequence/iterable of rows; len(table.rows) is used for row count
    column_ids (iterable[int]):
        Iterable of integer column indices to print (0-based). Each element must be a valid index into table.column_names and table.columns; typical values come from parse_column_identifiers.
    stats (dict[int, dict[str, Any]]):
        Mapping keyed by column index (the same indices in column_ids) to a mapping of operation name -> computed stat value. For each column_id, the inner dict must contain an entry for each operation name present in the global OPERATIONS mapping (values may be None to indicate a skipped/missing stat).
        Special expectations:
        - If an operation named 'freq' is present and not None, stats[column_id]['freq'] must be an iterable (typically a list) of dict-like rows with keys 'value' and 'count'. Each 'row' is expected to be accessed as row['value'] and row['count'].

## Returns:
    None
    The method only writes to self.output_file and does not return a value.

## Raises:
The method does not explicitly raise custom exceptions, but callers should expect the following exceptions to propagate under the exact conditions shown:
    - NameError: if the global OPERATIONS or helper functions (format_decimal) are not defined in the module scope at call time (name lookup failure).
    - KeyError: if stats does not contain an entry for a requested column_id (accessing stats[column_id]).
    - IndexError: if a provided column_id is out of range for table.column_names or table.columns (accessing table.column_names[column_id] or table.columns[column_id]).
    - KeyError: if a freq row dict is missing required keys 'value' or 'count' (accessing row['value'] / row['count']).
    - TypeError, ValueError, or other exceptions from format_decimal / locale.format_string if numeric formatting fails (these propagate from the format_decimal function).
    - IOError / OSError or their subclasses raised by self.output_file.write if writing to the output stream fails.

## State Changes:
Attributes READ:
    - self.output_file: file-like object with write(s: str) method; used for all text output.
    - self.args.decimal_format: string format used when calling format_decimal for Decimal values.
    - self.args.no_grouping_separator: boolean flag forwarded to format_decimal to disable grouping separators.
    - self.is_finite_decimal (method): invoked to decide whether a numeric 'value' from a 'freq' row should be formatted via format_decimal.
    - global OPERATIONS: mapping of operation name -> operation metadata (used to determine label width and iterate operations).
    - format_decimal (module-level helper): called to format Decimal numeric values for display.
    - agate.Number (type): used in isinstance(column.data_type, agate.Number) checks to decide numeric formatting path.
    - table.column_names, table.columns, table.rows: table metadata used for labels, data_type inspection, and final row count.

Attributes WRITTEN:
    - None of the CSVStat object's attributes are modified by this method.
    - Side-effect writing: the method writes formatted text to self.output_file (external I/O), but does not mutate self.* attributes.

## Constraints:
Preconditions (must be true before calling):
    - OPERATIONS must be defined and be an iterable/mapping whose values are dict-like objects containing a 'label' key (string). The method computes label_column_width = max(len(op_data['label']) for op_data in OPERATIONS.values()).
    - table must be an agate.Table-like object with indexable column_names and columns sequences and a length-measurable rows collection (len(table.rows) must be valid).
    - Every integer in column_ids must be a valid index into table.column_names and table.columns.
    - stats must contain an entry stats[column_id] for each column_id provided.
    - For any column where stats[column_id]['freq'] is not None, that value must be iterable and yield dict-like items with keys 'value' and 'count'.
    - self.output_file must be a writable text stream (implementing write(str)).

Postconditions (guaranteed after calling):
    - The output file will contain a plain-text block for each column in column_ids (unless all of a column's operation values are None), with aligned labels and properly-rendered values for known operations; frequency values are listed with counts in parentheses and numeric Decimal frequency values will be formatted according to self.args.decimal_format and the no_grouping_separator flag when they are finite Decimals.
    - The final line written is "Row count: N\n" where N == len(table.rows).
    - The method returns None.

## Side Effects:
    - Writes text to self.output_file. This is the main side effect and is responsible for all observable output.
    - May call format_decimal which depends on the process-wide locale (locale.format_string); thus, the output may vary with the global locale state.
    - No network calls or filesystem mutations are performed by the method itself (aside from the possibility that self.output_file.write triggers OS-level I/O if self.output_file points to stdout, a file, or another stream).

## Behavior notes and edge cases:
    - Operations with a None value in column_stats are skipped entirely.
    - The 'freq' operation is rendered as a vertical list. For the first freq row the operation label is printed once, subsequent freq rows align under an empty label of the same width.
    - When a freq row's 'value' is numeric:
        - The code path checks isinstance(column.data_type, agate.Number). If true and the value is a Decimal and finite (self.is_finite_decimal(value) True), format_decimal is used. Other numeric types or non-finite Decimals are converted via str(value).
    - For non-frequency operations:
        - The 'nulls' operation value, when truthy, will be annotated with " (excluded from calculations)".
        - The 'len' operation value will be suffixed with " characters".
    - If a frequency list for a column is empty, no freq lines are written for that column (and the freq label is not emitted).
    - Zero/null distinctions:
        - For 'nulls', a value of 0 is falsy and will not receive the "excluded" annotation.
    - If format_decimal is given a format string that produces no decimal point (e.g., '%.0f'), its internal trimming behavior (removing trailing zeros) can produce surprising results (see format_decimal docs); such issues propagate to print_stats because it relies on format_decimal for presentation of finite Decimal values.

### `csvkit.utilities.csvstat.CSVStat.print_csv` · *method*

## Summary:
Emit the computed statistics for the requested columns to the utility's configured output_file as a CSV table whose header is ['column_id', 'column_name'] followed by one column per operation.

## Description:
Known callers and context:
    - CSVStat.main(): After statistics are computed for each requested column (when --csv / csv_output is specified and no single-operation flags are used), main() calls print_csv(table, column_ids, stats) to produce the final CSV-formatted output. This method is the CSV-specific output renderer in the CSVStat execution pipeline.

Why this is a separate method:
    - Encapsulates CSV formatting and emission details (header construction, per-row assembly, frequency-list serialization) so other output formats (plain text, JSON) remain separate and easier to maintain.
    - Keeps concerns separated: calculation (calculate_stats/_calculate_stat), row assembly (_rows), and output formatting/writing (print_csv/print_json/print_stats).

## Args:
    table (agate.Table)
        - A materialized agate Table instance containing input rows and metadata.
        - Must expose .column_names (sequence of strings) and .rows/.columns as per agate.Table semantics.
    column_ids (iterable[int])
        - Iterable of zero-based integer column indices indicating which columns to output and their order.
        - Each index must satisfy 0 <= column_id < len(table.column_names).
    stats (dict[int, dict[str, Any]])
        - Mapping: column_id -> mapping of operation name (str) -> computed value for that operation.
        - The set of operation names is expected to match the keys of the global OPERATIONS mapping used by the class.

## Returns:
    None
    - The function writes to self.output_file (side effect) and returns nothing.

## Raises:
    - IOError / OSError: If writing to self.output_file fails (e.g., closed stream, disk error). These errors propagate from the underlying file write operations.
    - ValueError: Potentially raised by the underlying agate.csv.DictWriter.writerow if the row contains keys not listed in the DictWriter fieldnames (behavior depends on the DictWriter implementation; the stdlib csv.DictWriter raises ValueError by default for extra keys).
    - TypeError: If a yielded row contains a 'freq' value that is not iterable (the code attempts to iterate it).
    - KeyError: If an element of the iterable in 'freq' is not a mapping containing the 'value' key; the code accesses item['value'] directly.
    - Any other exceptions raised by agate.csv.DictWriter.writeheader / writerow are propagated unchanged.

## State Changes:
Attributes READ:
    - self.output_file: the writable text stream used as CSV output target.
    - global OPERATIONS: used to build the header ordering via list(OPERATIONS).
    - self._rows (method): invoked to obtain dictionaries representing rows to write.

Attributes WRITTEN:
    - No CSVStat attributes are modified.
    - External mutation: bytes/text are written to the underlying self.output_file.

## Constraints:
Preconditions:
    - self.output_file must be a writable, text-mode file-like object compatible with agate.csv.DictWriter (supports write()).
    - table must be a valid agate.Table and column_ids must reference valid indices.
    - stats must include entries for each column_id in column_ids, with inner mappings containing keys corresponding to operation names (strings) present in OPERATIONS.
    - The global OPERATIONS should be an iterable mapping (mapping-like object) whose keys are the operation names (strings). The iteration order of OPERATIONS determines the order of operation columns in the CSV header; use an OrderedDict (or Python 3.7+ dict) if a stable order is required.

Postconditions:
    - A CSV header row is written to self.output_file: 'column_id','column_name', followed by operation names in the order produced by list(OPERATIONS).
    - For each column_id in column_ids, exactly one CSV row will be written. Fields corresponding to operation names not present (i.e., absent or None in the row dict) are emitted as empty fields by the DictWriter (it substitutes restval for missing keys).
    - If a row contains a 'freq' key, its value is converted in-place (in the yielded row dict) to a single comma-and-space separated string built from the sequence of items in the original freq value by taking str(item['value']) for each item. The original 'count' or other metadata in freq items is not included in the CSV value.

## Side Effects:
    - Writes CSV text to self.output_file via agate.csv.DictWriter.writeheader() and writerow().
    - Mutates each per-row dictionary yielded by self._rows only insofar as it replaces the 'freq' entry with its string serialization.
    - Uses str() on each freq item['value'] when serializing, so complex objects are coerced to their string representations.
    - Potential data loss relative to the in-memory stats: frequency counts associated with 'freq' entries (e.g., item['count']) are not preserved in the CSV output — only the values are emitted.

## Example:
    Given:
        OPERATIONS iteration order -> ['nulls', 'freq', 'mean']
        A stats mapping for one column like:
            stats[0] = {
                'nulls': 2,
                'freq': [{'value': 'a', 'count': 4}, {'value': 'b', 'count': 3}],
                'mean': None,
            }
    The header written will be:
        column_id,column_name,nulls,freq,mean
    The row written for column_id 0 will include freq serialized as:
        "a, b"
    Resulting CSV row (conceptual):
        1,ColumnName,2,"a, b",

### `csvkit.utilities.csvstat.CSVStat.print_json` · *method*

## Summary:
Serialize the per-column statistics produced by _rows into JSON and write the JSON text to the utility's configured output stream.

## Description:
- Known callers and lifecycle:
    - Invoked from CSVStat.main when the user requests JSON output (args.json_output is True). This occurs in the final output stage after the table has been parsed and statistics have been computed for the requested columns.
- Why this is a separate method:
    - Separates JSON serialization and formatting concerns from row assembly and other output formats. Both CSV and JSON output paths reuse the same row-generation logic (_rows), so this method centralizes JSON-specific options (indentation, non-ASCII handling, and the default serializer).

## Args:
    table (agate.Table):
        - The agate Table containing the parsed CSV input. _rows uses table.column_names to label rows; table itself is not modified.
    column_ids (iterable[int]):
        - Iterable of zero-based column indices to include in the output. Each index must be valid for table.column_names.
    stats (dict[int, dict]):
        - Mapping from column index to a dict of operation-name -> statistic value (as produced by calculate_stats). Values are expected to be either JSON-serializable by the standard json library or handled by the module-level default serializer.

## Returns:
    None
    - Writes JSON text to self.output_file. Does not return a value.
    - Edge-case returns:
        - If column_ids is empty, the output is an empty JSON array: [].

## Raises:
    - TypeError:
        - Raised by json.dump if an object in the data cannot be serialized and the provided default serializer does not convert it to a serializable type.
    - ValueError / OSError / IOError:
        - Propagated from underlying file writes if self.output_file is not writable or an I/O error occurs during writing.
    - Note:
        - json.dump is called with default=default_float_decimal (imported from csvkit.cli). That function must be present in the module namespace to provide any custom Decimal/float serialization behavior CSVKit expects; otherwise json.dump's default behavior applies.

## State Changes:
- Attributes READ:
    - self._rows(table, column_ids, stats) is iterated to produce the sequence of output rows.
    - self.args.indent is read to determine the indentation level passed to json.dump (int or None).
    - self.output_file is used as the destination writeable file-like object.
- Attributes WRITTEN:
    - None. The method does not modify any attributes on self.

## Constraints:
- Preconditions:
    - self.output_file must be an open, text-mode file-like object implementing write(str).
    - Each column_id in column_ids must be a valid index into table.column_names, and stats must contain an entry for that column_id.
    - The dictionaries yielded by self._rows (mapping string keys to values) are expected to be serializable by json.dump, or be convertible by the module-level default serializer default_float_decimal.
    - default_float_decimal must be available in the module namespace (it is imported from csvkit.cli in this module).
- Postconditions:
    - On success, self.output_file contains the JSON serialization of the list of rows returned by _rows.
    - No attributes on self are modified.

## Side Effects:
- I/O:
    - Writes the serialized JSON text to self.output_file using json.dump. json.dump is called with ensure_ascii=False, so non-ASCII characters are written directly (not escaped).
- Memory:
    - The generator returned by self._rows is fully materialized into a list before serialization; peak memory usage will grow with the number of columns emitted.
- External calls:
    - Calls json.dump with default=default_float_decimal and ensure_ascii=False. The default serializer (default_float_decimal) is expected to handle Decimal/float formatting per CSVKit conventions; if it does not convert a value to a JSON-serializable type, json.dump raises TypeError.

### `csvkit.utilities.csvstat.CSVStat._rows` · *method*

## Summary:
Yield a sequence of output rows (mapping/dicts) summarizing statistics for each requested column, producing a row-per-column that includes the 1-based column index, column name, and any computed operation values present for that column.

## Description:
- Known callers and lifecycle:
    - CSVStat.print_csv: iterates rows yielded by this method to write a CSV table (it performs a small post-processing step for the 'freq' field before writing).
    - CSVStat.print_json: materializes list(self._rows(...)) to produce JSON output.
    - Both callers invoke this method during the output/serialization stage after statistics for all requested columns have been computed (i.e., after CSVStat.calculate_stats has populated the stats mapping). This method is part of the final formatting/output pipeline executed from CSVStat.main.
- Why this is a separate method:
    - Encapsulates the logic that converts internal stats data structures into the uniform row/dict representation used by both CSV and JSON output routines. Extracting this produces a single place to adapt output row shape, keeps print_csv/print_json small, and centralizes future changes to output schema.

## Args:
    table (agate.table.Table):
        - The agate Table instance created from the input CSV.
        - Must expose .column_names (sequence of header strings).
    column_ids (iterable[int]):
        - Iterable of integer column indices (0-based) indicating which columns to include and in what order.
        - Values must be valid indices into table.column_names.
    stats (Mapping[int, Mapping[str, Any]]):
        - Mapping keyed by the same column index integers in column_ids.
        - Each value is a mapping from operation name (str) to the computed statistic (or None).
        - The set of operation names referenced by this method is derived from the module-level OPERATIONS mapping (it iterates OPERATIONS.items()).

## Returns:
    generator[dict]:
        - Yields one dict per column_id in column_ids.
        - Each yielded dict has at minimum:
            * 'column_id' (int): the 1-based column index (column_id + 1).
            * 'column_name' (str): table.column_names[column_id].
        - Additionally, for each operation name present in OPERATIONS, if column_stats[op_name] is not None then the dict will contain an entry op_name: column_stats[op_name].
        - Possible values:
            * Scalars (int, float, Decimal, str), lists, or nested dicts depending on how calculate_stats/_calculate_stat produced values (e.g., 'freq' is typically a list of { 'value': ..., 'count': ... } rows).
            * For CSV output, callers may further stringify some fields (e.g., join 'freq' values into a single string).
        - Edge-case return behavior:
            * If column_ids is empty, the generator yields nothing.
            * Values are emitted as-provided from stats; no further formatting is applied here.

## Raises:
    - IndexError:
        - If any integer in column_ids is out of range for table.column_names (accessing table.column_names[column_id]).
    - KeyError:
        - If stats does not contain an entry for a column_id (stats[column_id]) or if the column_stats mapping lacks a required operation key and the caller attempts to index it.
    - TypeError:
        - If column_ids is not iterable.
        - If table.column_names is not subscriptable (unlikely for a correctly-constructed agate.Table).
    - NameError:
        - If the module-level OPERATIONS name is not defined in the module namespace.
    - Note: The method does not catch or translate these exceptions; they propagate to the caller.

## State Changes:
- Attributes READ:
    - None of self's attributes are read by this method. The method solely reads the provided arguments:
        * table.column_names
        * the stats mapping argument
        * the global OPERATIONS mapping (module-level)
- Attributes WRITTEN:
    - None. The method does not modify self or the input objects; it constructs and yields new dict objects.

## Constraints:
- Preconditions:
    - table must be an agate Table-like object with a sequence attribute column_names accessible by integer index.
    - column_ids must be an iterable of valid 0-based column indices into table.column_names.
    - stats must be a mapping keyed by the same integer column indices and each stats[column_id] must be a mapping whose keys include all operation names present in OPERATIONS (or at least safely return None for operations that are not applicable).
    - The module-level OPERATIONS mapping must be defined and iterable (supports .items()).
- Postconditions:
    - For every column_id in column_ids the method yields exactly one dict containing the 1-based column id, the column name, and any non-None operation results from stats[column_id].
    - The method does not mutate table, column_ids, stats, or any self attributes.

## Side Effects:
    - No I/O (no reading/writing files, no network calls).
    - No mutation of external objects (only creates fresh dicts that it yields).
    - Reads the module-level OPERATIONS mapping (no mutation).

## `csvkit.utilities.csvstat.format_decimal` · *function*

## Summary:
Format a numeric value using a printf-style format with locale-aware separators, then remove trailing fractional zeros and a trailing decimal point to produce a concise display string.

## Description:
A small presentation helper that calls locale.format_string with a single numeric value, then trims trailing '0' characters and a trailing '.' to avoid outputs like "123.000". It centralizes locale-aware formatting and the common post-format trimming used when rendering numeric statistics or summary values.

Known callers and typical usage context:
- Located in the csvstat utility module (csvkit.utilities.csvstat). It is intended to be invoked by csvstat's output/presentation code when preparing numeric statistics (means, percentiles, counts) for display or reporting.
- Typical pipeline stage: formatting numeric results immediately before writing rows to stdout or assembling JSON/text summaries.

Why this is a separate function:
- Encapsulates two concerns in one place: (1) applying locale-aware formatting with an adjustable grouping option and (2) normalizing the formatted string by removing insignificant trailing zeros and a trailing decimal point. This avoids duplication and ensures consistent presentation across csvstat output.

## Args:
    d (int | float | decimal.Decimal):
        The numeric value to format. Should be a numeric type appropriate for old-style printf numeric conversions.
    f (str, optional):
        Old-style printf format string for a single numeric argument. Default: '%.3f'.
        Examples: '%.2f', '%.0f', '%d'
    no_grouping_separator (bool, optional):
        If True, disables thousands/grouping separators. Default: False.
        Internally passed to locale.format_string as grouping=not no_grouping_separator (so grouping is enabled when no_grouping_separator is False).

Interdependencies and notes:
- The resulting string depends on the current process locale (locale.getlocale()/locale.setlocale). If callers need reproducible separators (decimal point and thousands separator), set the locale before calling.
- The trimming step is unconditional and will remove trailing '0' characters from the formatted string even if the string contains no decimal point (see edge case below).

## Returns:
    str: The final formatted and trimmed string.
    Behavior specifics:
      - First, locale.format_string(f, d, grouping=not no_grouping_separator) is called to produce a locale-aware formatted string.
      - Then .rstrip('0') is applied, removing any trailing '0' characters.
      - Finally .rstrip('.') is applied, removing a trailing decimal point if present.
    Possible outcomes / examples (locale-dependent):
      - d = 1234.5, f='%.3f', grouping enabled -> '1,234.5'
      - d = 1000, f='%.3f' -> '1,000' (because '1,000.000' → '1,000')
      - d = 1000, f='%.0f' -> '1' (see edge case below)
    The function never returns None; it returns a string or propagates an exception.

## Raises:
    Any exception raised by locale.format_string will be propagated. This includes (but is not limited to):
      - TypeError when the format string and the supplied value are incompatible (for example, using '%d' with a non-integer-like object).
      - ValueError if the format string is malformed in a way that locale.format_string rejects.
    The function itself does not catch or wrap these exceptions.

## Constraints:
Preconditions:
    - f must be a valid old-style printf format string for a single numeric argument.
    - d should be a numeric type compatible with f and locale.format_string.
Postconditions:
    - The returned string contains no trailing '0' characters that remained after the first rstrip step, and no trailing '.' if one existed.
    - The string reflects grouping and decimal separators of the current locale according to grouping=not no_grouping_separator.

Edge cases (important):
    - If the formatted string produced by locale.format_string does not include a decimal point (for example, when f produces integer output such as '%.0f' or '%d'), the unconditional .rstrip('0') call will remove trailing '0' characters from the integer part as well. Example: locale.format_string('%.0f', 1000) -> '1000'; .rstrip('0') -> '1' (incorrectly shortened). Callers should avoid passing format strings that produce no decimal point if they expect to preserve integer trailing zeros, or should pre-format differently.
    - If you require safer trimming that only affects fractional zeros, consider ensuring the format produces a decimal point (e.g., use '%.3f') or post-process with logic that only trims fractional zeros (outside this function).

## Side Effects:
    - No I/O performed by this function.
    - No mutation of global variables performed by this function.
    - The output depends on the process-wide locale. Reading the locale state is an implicit dependency (locale is global process state), so results can vary across environments or if locale.setlocale is called elsewhere.

## Control Flow:
flowchart TD
    Start[Start] --> ComputeGrouping["grouping = not no_grouping_separator"]
    ComputeGrouping --> CallFormat["formatted = locale.format_string(f, d, grouping=grouping)"]
    CallFormat --> StripZeros["s1 = formatted.rstrip('0')"]
    StripZeros --> StripDot["s2 = s1.rstrip('.')"]
    StripDot --> Return["Return s2"]
    CallFormat -->|error| Propagate["Propagate exception from locale.format_string"]

## Examples:

Example 1 — Typical use (set locale to use commas as thousands separators):
    import locale
    locale.setlocale(locale.LC_ALL, '')  # or a specific locale like 'en_US.UTF-8'
    format_decimal(1234.5)               # returns '1,234.5' in a grouping locale

Example 2 — Disable grouping:
    format_decimal(1234.5, f='%.3f', no_grouping_separator=True)  # '1234.5'

Example 3 — Decimal input:
    from decimal import Decimal
    format_decimal(Decimal('1234.5000'))  # '1,234.5' (locale-dependent)

Example 4 — Dangerous format that can truncate integer trailing zeros:
    # Avoid formats that omit the decimal point if you need to preserve trailing zeros.
    format_decimal(1000, f='%.0f')  # locale.format_string -> '1000' -> rstrip('0') -> '1' (likely unintended)
    # Recommendation: use a format that includes a decimal point if trimming should only affect fraction digits,
    # or post-process with safer logic before calling this helper.

## `csvkit.utilities.csvstat.get_type` · *function*

## Summary:
Return the name of the agate data type class used by a specific column as a simple string (e.g., "NumberType", "TextType").

## Description:
This small helper extracts the class name of a column's data_type and returns it as a string for presentation or reporting purposes.

Known callers:
- No direct callers were discovered in the provided scan of the codebase. Conceptually, this function is intended for use by CSV statistics or reporting code paths (for example, a CLI or report generator) that need a human-readable type label for each column.

Why this logic is extracted:
- Converting a column's data type to a compact, printable label is a single, well-defined responsibility used in multiple reporting contexts. Extracting it centralizes the formatting logic, keeps presentation code concise, and isolates the single point that determines how a column's type is represented as text.

## Args:
    table (object): A table-like object (commonly an agate.Table) that exposes a `columns` mapping or sequence. Each column object accessed via table.columns[column_id] is expected to have a `data_type` attribute.
    column_id (int | str | object): Identifier used to index into table.columns. Typical values are:
        - int: positional index into a sequence-like `columns`
        - str: column name used as a key in a mapping-like `columns`
      The allowed types depend on the concrete type of table.columns.
    **kwargs: Additional keyword arguments are accepted but ignored by this function. They exist to allow a uniform call signature across different reporters.

Notes on interdependencies:
- The meaning and accepted types for `column_id` depend entirely on the runtime type and semantics of `table.columns`. This function does not validate or coerce column identifiers.

## Returns:
    str: The simple class name of the column's data_type attribute.
    - Typical return values include human-readable agate type class names such as:
        "NumberType", "TextType", "BooleanType", "DateType", etc.
    - If the column exists but its data_type is None, the returned string will be "NoneType".
    - The function always returns the __class__.__name__ of whatever `table.columns[column_id].data_type` points to.

## Raises:
    KeyError: If table.columns is a mapping and `column_id` is not a present key.
    IndexError: If table.columns is a sequence and `column_id` is an out-of-range index.
    AttributeError: If `table` or `table.columns[column_id]` does not have a `data_type` attribute.
    TypeError: If `table.columns` is not subscriptable (for example, None) or `column_id` is an invalid key type for the underlying container.
    Any exception raised by the indexing operation on table.columns will propagate unchanged.

## Constraints:
Preconditions:
    - `table` must be a non-null object exposing `columns` that supports subscription with `column_id`.
    - The selected column object must have a `data_type` attribute (it may be None).
Postconditions:
    - On success, returns a non-empty string containing the class name of the column's data_type.
    - No mutation of `table` or its columns occurs.

## Side Effects:
    - None. This function performs no I/O and does not modify external state.

## Control Flow:
flowchart TD
    Start([Start]) --> AccessColumn{Access table.columns[column_id]}
    AccessColumn -->|Access succeeds| GetDataType[Get column.data_type]
    GetDataType -->|data_type present (or None)| ReturnName[Return data_type.__class__.__name__]
    AccessColumn -->|KeyError / IndexError / TypeError| PropagateError[Propagate indexing exception]
    GetDataType -->|AttributeError| PropagateAttrError[Propagate AttributeError]

## Examples:
- Typical read-only usage:
    Given an agate.Table `table` whose first column (index 0) is numeric, calling the function will yield a concise type label:
    get_type(table, 0) -> "NumberType"

- When using named columns (mapping-style):
    If `table.columns` supports string keys and contains a column "age" of numeric type:
    get_type(table, "age") -> "NumberType"

- Error handling pattern:
    If the caller cannot guarantee the column exists, wrap the call to handle missing columns:
    - Attempt the call and catch KeyError/IndexError to provide a fallback label or skip the column in reporting.
    - Catch AttributeError if the column object does not expose `data_type`.

Notes:
- The function intentionally accepts and ignores extra keyword arguments to allow callers with richer parameter sets to pass through a uniform signature when composing multiple report/value functions.

## `csvkit.utilities.csvstat.get_unique` · *function*

## Summary:
Compute and return the number of distinct values present in a specified column of the provided table.

## Description:
This function obtains the column identified by column_id from table.columns, calls its values_distinct() accessor to obtain the distinct values collection/iterable, and returns the length of that result.

Known callers / usage context:
- Not determinable from the single-file snippet provided. The function is intended for use in a per-column statistics pipeline (for example, a csvstat-like utility) where callers compute multiple column metrics (unique counts, null counts, etc.) and aggregate them for display or serialization.
- It is implemented as a small, reusable metric extractor so that metric-reporting code can call a uniform interface for different statistics.

Reason for extraction:
- Encapsulates the single responsibility of counting distinct entries in a column, keeping higher-level metric orchestration code simple and consistent.
- Accepts **kwargs for compatibility with other metric functions that share a common calling convention, even though those kwargs are ignored here.

## Args:
    table (object):
        A table-like object exposing a .columns attribute. table.columns must be indexable by column_id and return a column object.
        Typical implementations: an agate.Table or a compatible abstraction provided by the surrounding codebase.
    column_id (hashable or int):
        Identifier used to select the column from table.columns. This may be a string column name or an integer index depending on table.columns' semantics.
    **kwargs:
        Keyword arguments are accepted for API uniformity with other metric functions but are ignored by this function.

Interdependencies:
- column_id must be valid for table.columns; otherwise the indexing operation will raise an exception (see Raises).

## Returns:
    int
        Non-negative integer equal to the number of distinct values in the column as reported by the column object's values_distinct() method.
        Edge-case returns:
        - 0 if the column exists and values_distinct() yields no elements.
        - A positive integer otherwise.
        Note: If values_distinct() returns an iterable without __len__ (a generator/iterator), then len(...) will raise TypeError (see Raises) — callers should convert such iterables to a sized container before calling this function or handle the propagated exception.

## Raises:
    AttributeError
        If the column object lacks a values_distinct attribute (attempting to call values_distinct will raise AttributeError).
    KeyError or IndexError
        If column_id is not valid for table.columns (depending on whether columns is a mapping or sequence).
    TypeError
        If values_distinct() returns an object without a defined length (an iterator/generator), calling len(...) will raise TypeError.
    Any other exception raised by the underlying table indexing or values_distinct implementation is propagated unchanged.

## Constraints:
Preconditions:
- table must have a .columns attribute supporting indexing by column_id.
- The returned column object must implement values_distinct().

Postconditions:
- On success, returns an integer >= 0 representing the distinct count.
- The function does not mutate table or column objects.

## Side Effects:
- The function itself performs no I/O and does not alter external state.
- Any side effects would originate from table.columns[column_id] or values_distinct(), which are external to this wrapper and not introduced by get_unique.

## Control Flow:
flowchart TD
    Start --> Access[Access table.columns[column_id]]
    Access -->|success| CallValues[Call column.values_distinct()]
    CallValues -->|returns sized collection| Len[Compute len(result)]
    Len --> Return[Return integer]
    CallValues -->|returns iterator/no __len__| TypeError[TypeError raised by len()]
    Access -->|invalid column_id| IndexErrorOrKeyError[KeyError/IndexError raised]
    CallValues -->|missing method| AttributeError[AttributeError raised]
    IndexErrorOrKeyError --> Propagate[Propagate exception]
    TypeError --> Propagate
    AttributeError --> Propagate

## Examples:
- Typical high-level pipeline usage (descriptive):
    1. A CSV file is parsed into a table-like object.
    2. For each column identifier, the metric orchestration layer calls this function to obtain the distinct-value count.
    3. The returned integer is included in tabular output or encoded into JSON.

- Example usage with defensive handling (pseudocode description):
    - If values_distinct() may return a generator (no __len__), convert to a sized container before invoking this function, or catch TypeError:
        * Option A: Replace the column's values_distinct implementation to return a list or set.
        * Option B: In client code, attempt get_unique(...); if TypeError is raised, obtain the iterable by calling values_distinct() directly and compute the count with a safe fallback (e.g., iterating and counting).

Notes:
- This function performs no normalization (case folding, trimming, or type coercion) of column values — any normalization must be applied before counting or provided by the column implementation's values_distinct method.
- The function assumes the distinct-values computation is reasonably efficient; large datasets where values_distinct materializes a very large container may have memory implications determined by that implementation.

## `csvkit.utilities.csvstat.get_freq` · *function*

## Summary:
Returns a list of the top-N most frequent values from a specific table column; each entry is a dictionary with the original value and its occurrence count.

## Description:
This function extracts values from a specified column of a table, counts how many times each distinct value appears, and returns the most-common items up to the requested limit.

Known callers:
- Intended for use by the csvstat command in csvkit to produce frequency-summary sections of column statistics. No direct callers were present in the provided snippet; typical usage is within a reporting pipeline after a table has been loaded and column identifiers resolved.

Why this logic is a separate function:
- Encapsulates frequency-counting behavior so presentation/formatting code can remain focused on output concerns.
- Reusable for any context that needs a top-N frequency summary of a column.
- Simplifies unit testing of counting behavior independently of I/O and table parsing.

## Args:
    table (object):
        - Expected type: agate.Table or any object exposing a `columns` attribute.
        - Requirement: `table.columns` must accept indexing with `column_id` and return a column-like object.
        - The column object must implement a `values()` method that returns an iterable of cell values.
    column_id (str|int):
        - Identifier used to select the column from `table.columns`. Exact accepted types depend on the table implementation (string names, integer indices, etc.).
        - If invalid, indexing will raise KeyError or IndexError (depending on mapping/list implementation).
    freq_count (int|None, optional):
        - Maximum number of most-common items to return. Defaults to 5.
        - Recommended: a non-negative integer. If None is passed, the function will request all distinct values (delegated to collections.Counter.most_common behavior).
        - Passing non-integer types (e.g., float, object) will likely cause a TypeError raised by the underlying list-slicing logic inside Counter.most_common.
        - Negative integers are not recommended: Counter.most_common will be called with that negative value and Python's list-slicing semantics may produce surprising results; callers should avoid negative values.
    **kwargs:
        - Accepted for compatibility with higher-level callers; ignored by this function.

Interdependencies:
- Relies on collections.Counter to count hashable values and its most_common method to select top items.

## Returns:
    list[dict]: Ordered list (descending by count) containing up to `freq_count` dictionaries with keys:
        - 'value': the original cell value as returned by the column's values() iterable (can be None, str, int, Decimal, etc.).
        - 'count': int, the number of occurrences of that value in the column.

Possible return shapes and edge cases:
- []: returned when the column has no values.
- If the number of distinct values is fewer than `freq_count`, the list contains only those distinct values.
- If `freq_count` is None, the function returns all distinct values ordered by frequency.
- Ties (equal counts) are ordered according to collections.Counter.most_common's ordering, which depends on the Counter's internal ordering and is not guaranteed to be stable across Python versions.

## Raises:
This function does not explicitly raise new exceptions; errors come from underlying operations:

    AttributeError:
        - If `table` lacks a `columns` attribute, or if the column object lacks a `values()` method.
    KeyError or IndexError:
        - If `column_id` is not present in `table.columns`.
    TypeError:
        - If elements returned by values() are unhashable (e.g., lists or dicts), Counter() will raise TypeError.
        - If `freq_count` is not an integer or None (e.g., a float), Counter.most_common will attempt a list slice with a non-integer and a TypeError will be raised.
    Any other exceptions thrown by table.columns[column_id].values() will propagate.

Callers should catch and handle these exceptions when column identifiers or data contents are dynamic or untrusted.

## Constraints:
Preconditions:
- The caller must ensure `table.columns[column_id].values()` returns an iterable of hashable items (hashability is required by collections.Counter).
- `freq_count` should be a non-negative integer or None.

Postconditions:
- The returned list length is <= freq_count (or equals the number of distinct values if smaller).
- No mutation: `table` and its column objects remain unmodified.

## Side Effects:
- None. The function performs pure computation: no I/O, no global state changes, and no mutation of the input table or its columns.

## Control Flow:
flowchart TD
    Start([Start]) --> AccessColumn[Access table.columns[column_id]]
    AccessColumn --> CallValues[Call column.values() -> iterable]
    CallValues --> BuildCounter[Build Counter from iterable]
    BuildCounter --> MostCommon[Call Counter.most_common(freq_count)]
    MostCommon --> MapToDicts[Map (value,count) pairs -> {'value': value, 'count': count}]
    MapToDicts --> Return([Return resulting list])
    Return --> End([End])

## Examples:
- Typical usage:
    - Given an agate.Table `table` with a "color" column:
      get_freq(table, "color", freq_count=3)
      -> [{'value': 'blue', 'count': 42}, {'value': 'red', 'count': 15}, {'value': None, 'count': 2}]

- Request all values:
    - get_freq(table, "status", freq_count=None)
      -> returns all distinct status values ordered by frequency.

- Error handling for dynamic inputs:
    - If column identifiers come from user input, guard against missing columns:
      try:
          freqs = get_freq(table, user_column, freq_count=5)
      except (KeyError, IndexError, AttributeError) as e:
          # handle missing column or malformed table
          raise

    - If source data may contain unhashable items (lists/dicts), guard and pre-process:
      try:
          freqs = get_freq(table, 'col_with_possible_unhashables', freq_count=5)
      except TypeError:
          # convert unhashable items to a hashable representation, or skip them
          pass

## `csvkit.utilities.csvstat.launch_new_instance` · *function*

## Summary:
Creates a CSVStat instance and invokes its run method; acts as a minimal bootstrap/entry point that transfers control to CSVStat.

## Description:
This function performs two explicit operations in sequence: it constructs an object named CSVStat and then calls the object's run method. It does not perform any argument parsing, I/O, error handling, or further orchestration itself — all such behaviors occur inside CSVStat.__init__ or CSVStat.run and will be observed by callers of this function.

Known callers within the provided source:
    - None present in the loaded context. The function is suitable to be referenced as a program entry point, but no direct call sites are visible in the provided files.

Reason for extraction:
    - The function isolates the simple bootstrap sequence (instantiate then execute) into a single, reusable symbol that can be referenced by external wiring (for example, by packaging entry points or a module-level main guard) without inlining that sequence elsewhere.

## Args:
    None

## Returns:
    None
    - The function does not return any value (implicit None). It also does not return or expose the created CSVStat instance to callers.

## Raises:
    - NameError: if the name CSVStat is not defined in the function's scope at call time.
    - Any exception raised by CSVStat.__init__: will propagate directly out of this function.
    - Any exception raised by CSVStat.run: will propagate directly out of this function.
    - No exceptions are caught or transformed by this function; it preserves the original exception types and tracebacks.

## Constraints:
Preconditions:
    - The identifier CSVStat must be bound to a callable/class in the function's execution scope (typically via an import or prior definition).
    - Any runtime resources required by CSVStat.__init__ or CSVStat.run (files, environment variables, locale settings, etc.) must be available; this function performs no validation of such resources.

Postconditions:
    - On successful return, CSVStat.run has completed and any side effects produced by __init__ or run have occurred.
    - If an exception is raised, it originated from either resolving CSVStat, CSVStat.__init__, or CSVStat.run; no partial cleanup or exception handling is performed by this function.

## Side Effects:
    - This function itself performs only object creation and a method call; all observable side effects (console output, file reads/writes, process termination via sys.exit, modifications to global state) are effects of CSVStat.__init__ or CSVStat.run.
    - The function does not perform additional I/O, logging, or state mutation beyond what the CSVStat implementation performs.

## Control Flow:
flowchart TD
    Start --> CheckCSVStat[Is CSVStat defined?]
    CheckCSVStat --> Undefined[No: NameError raised]
    CheckCSVStat --> Instantiate[Yes: Instantiate CSVStat]
    Instantiate --> InitException[__init__ raises exception]
    Instantiate --> CallRun[__init__ succeeds -> call run()]
    CallRun --> RunException[run() raises exception]
    CallRun --> Success[run() completes successfully]
    InitException --> End[Propagate exception]
    RunException --> End[Propagate exception]
    Undefined --> End
    Success --> End[Return None]

## Examples:
- Typical top-level use (described): A module's main guard can invoke this function to start the CSVStat command-line behavior; callers that want to handle failures should call the function from a try/except block and handle or log exceptions raised by CSVStat.

- Error-handling guidance (described): If a caller must ensure the process does not exit or must perform cleanup after failures, the caller should wrap the call in exception handling and perform any necessary teardown; this function does not implement such handling itself.

Notes:
    - To learn exactly what exceptions may be raised and which side effects will occur, consult the implementations of CSVStat.__init__ and CSVStat.run.
    - This documentation intentionally limits claims to behaviors that follow directly from the two-line implementation of this function.

