# `render_categorical.py`

## `src.ydata_profiling.report.structure.variables.render_categorical.render_categorical_frequency` · *function*

## Summary:
Constructs and returns a small presentation Table summarizing the "unique" statistics for a categorical variable — specifically the count of unique values and that count as a percentage — packaged for the report renderer with an anchor id derived from the variable id.

## Description:
- Known callers:
    - No direct call sites were discovered in the provided snapshot. In the typical report-generation pipeline this function is called by the categorical-variable rendering stage (the code path that builds the per-variable report fragments for categorical variables), i.e., components that assemble variable-level sections and need the "unique" statistics presented in the report.
- Why this is a separate function:
    - It isolates the presentation assembly for the "unique" frequency summary (two small metrics and their metadata: hint and alert flags). Extracting this logic keeps the higher-level categorical rendering code focused on layout and orchestration while centralizing the details of building the "Unique" Table (labels, formatted values, hint text, alert flags, anchor naming and style).

## Args:
    config (Settings):
        - The global report Settings object. The function reads config.html.style to populate the Table.style field.
        - Preconditions: config must expose an attribute html whose style field is a valid Style instance (a pydantic model used by presentation objects).
    summary (dict):
        - A dictionary with the metric values and metadata required by this renderer.
        - Required keys:
            * "n_unique" (int-like): the number of unique values; will be passed to fmt_number for formatting.
            * "p_unique" (float-like): the proportion/fraction of unique values (0..1 expected); will be passed to fmt_percent for formatting.
            * "alert_fields" (iterable of str): a collection of field names used to determine whether to mark a metric with an alert (the code checks membership of "n_unique" and "p_unique").
        - The function indexes summary directly; missing or ill-typed keys will raise the standard exceptions described below.
    varid (str):
        - A string identifier for the variable used to construct the Table.anchor_id. The anchor_id is built as f"{varid}_unique_stats".
        - Typical values are stable variable identifiers used elsewhere in the report (e.g., column names or generated ids).

## Returns:
    Renderable (specifically a Table instance):
        - Returns an instance of Table whose content contains:
            * "rows": a sequence with two row dictionaries:
                - Row 1:
                    name: "Unique"
                    value: fmt_number(summary["n_unique"]) (string)
                    hint: help("The number of unique values (all values that occur exactly once in the dataset).")
                    alert: boolean -> True if "n_unique" is in summary["alert_fields"]
                - Row 2:
                    name: "Unique (%)"
                    value: fmt_percent(summary["p_unique"]) (string)
                    alert: boolean -> True if "p_unique" is in summary["alert_fields"]
            * "name": "Unique"
            * style: config.html.style
            * anchor_id: f"{varid}_unique_stats" (passed via Table's kwargs to the ItemRenderer layer)
        - Edge-case return values:
            * If the function returns successfully, the returned Table always follows Table's content schema (keys "rows","style","name","caption" will be present; caption remains default None unless upstream Table invocation adds one).
            * The function does not return None or other types on success.

## Raises:
    - KeyError:
        - If summary does not contain any of the required keys ("n_unique", "p_unique", or "alert_fields"), attempting to access summary[...] will raise KeyError.
    - TypeError:
        - If summary["alert_fields"] is present but is not an iterable supporting membership testing, the "in" checks will raise TypeError.
        - If config or config.html is None or missing the style attribute, attempting to access config.html.style may raise AttributeError or TypeError when used; these are standard attribute-access failures.
        - fmt_number or fmt_percent may raise TypeError/ValueError if the provided values are not numeric/formattable.
    - Exceptions described above are not raised deliberately by this function but are possible as direct consequences of indexing/formatting operations with malformed inputs.

## Constraints:
- Preconditions (caller responsibilities):
    - summary must contain the required keys with semantically correct types:
        * n_unique: integer-like (int, numpy integer, etc.)
        * p_unique: numeric fraction (float-like; 0..1 expected)
        * alert_fields: iterable of strings (or values convertible to str) for membership checks
    - config must provide config.html.style (a validated Style instance).
    - varid must be a string-like identifier suitable for building an anchor id.
- Postconditions (guarantees after successful return):
    - A Table object is returned with name set to "Unique", anchor_id set to "{varid}_unique_stats", style set to config.html.style, and rows populated as described in Returns.

## Side Effects:
- None: the function performs pure construction of presentation objects and string formatting. It performs no I/O, no network calls, and does not mutate external/global state.
- Indirect external-dependency effects:
    - The appearance of the formatted strings depends on global locale settings (fmt_number uses locale-aware formatting) and on fmt_percent's formatting rules, but the function itself does not alter those settings.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckInputs{summary has keys?}
    CheckInputs -->|Missing key(s)| RaiseKeyError[KeyError propagated]
    CheckInputs -->|Keys present| FormatN[fmt_number(summary["n_unique"])]
    FormatN --> FormatP[fmt_percent(summary["p_unique"])]
    FormatP --> ComputeAlerts{Check alert membership}
    ComputeAlerts --> BuildRows[Build two row dicts with name,value,hint?,alert]
    BuildRows --> CreateTable[Instantiate Table(rows=rows, name="Unique", anchor_id=f"{varid}_unique_stats", style=config.html.style)]
    CreateTable --> Return[Return Table instance]
    CreateTable -->|If style missing| RaiseAttr[AttributeError/TypeError propagated]

## Examples:
- Typical (happy path) usage summary:
    - Inputs:
        * config: a Settings object with a valid config.html.style
        * summary: {"n_unique": 12, "p_unique": 0.034, "alert_fields": ["p_unique"]}
        * varid: "my_variable"
    - Outcome:
        * The function returns a Table whose rows present:
            - "Unique" -> formatted count "12" (via fmt_number) with a help badge hint and alert=False
            - "Unique (%)" -> formatted percent "3.4%" (via fmt_percent) with alert=True because "p_unique" is in alert_fields
        * The Table.name is "Unique" and the anchor id is "my_variable_unique_stats".
- Error handling example:
    - If summary = {"n_unique": 5, "p_unique": 0.1} (missing "alert_fields"):
        * Calling this function will result in a KeyError while evaluating "n_unique" in summary["alert_fields"].
    - To guard, callers should ensure summary["alert_fields"] exists (for example, default to an empty list when building summary) and validate config prior to calling.

## `src.ydata_profiling.report.structure.variables.render_categorical.render_categorical_length` · *function*

## Summary:
Renders a summary table of string/sequence length statistics and a corresponding histogram image for a categorical variable, returning a Table (length statistics) and an Image (length histogram) ready for inclusion in the report.

## Description:
This function assembles two Renderable objects that describe the distribution of lengths for categorical values:
- A Table named "Length" containing Min, Median, Mean, and Max length values formatted for display.
- An Image containing a histogram visualization of the lengths.

Known callers and context:
- Invoked by higher-level categorical variable rendering code within the report generation pipeline (the categorical variable renderer in the same module/package). Typical trigger: when generating the per-variable section for a categorical (object/string-like) variable and the summary dict includes length statistics.
- Typical pipeline stage: per-variable report assembly during the overall profiling report generation, after statistics for the variable have been computed.

Rationale for extraction:
- Isolates presentation logic for length-specific outputs (table formatting, histogram creation) from the broader categorical rendering logic.
- Keeps formatting details (formatters, anchor ids, image creation) in a single, testable function, allowing other code to reuse or replace length rendering without changing the overall categorical renderer.

## Args:
    config (Settings):
        - The global report configuration object.
        - Used for: numeric precision (config.report.precision), HTML style for the Table (config.html.style), and image format for the Image (config.plot.image_format).
        - Must expose attributes: report.precision (int), html.style (mapping), plot.image_format (str).
    summary (dict):
        - A dictionary containing pre-computed length statistics for the variable.
        - Required keys (used by this function):
            * "max_length": numeric (int/float) — maximum observed length.
            * "median_length": numeric — median length.
            * "mean_length": numeric — mean length.
            * "min_length": numeric — minimum observed length.
            * "histogram_length": either
                - a list of (value, count) pairs (e.g. [(v1, c1), (v2, c2), ...]) OR
                - a sequence/tuple acceptable by the histogram(...) function when expanded (e.g. (values, counts) or other signature expected by histogram).
        - Interdependencies: histogram_length must be in one of the above shapes. The function inspects histogram_length with isinstance(..., list) to choose how to call histogram.
    varid (str):
        - String identifier for the variable used to construct anchor_ids for the Table and Image:
            * Table anchor_id: f"{varid}lengthstats"
            * Image anchor_id: f"{varid}length"

## Returns:
    Tuple[Renderable, Renderable]:
        - (length_table, length_histo)
        - length_table: a Table Renderable with:
            * name: "Length"
            * rows for "Max length", "Median length", "Mean length", "Min length"
            * each row value is formatted via fmt_number or fmt_numeric and contains 'alert': False
            * anchor_id uses varid + "lengthstats"
            * style set from config.html.style
        - length_histo: an Image Renderable with:
            * image contents produced by histogram(...)
            * image_format set from config.plot.image_format
            * alt text "length histogram"
            * name "Length" and caption "Histogram of lengths of the category"
            * anchor_id uses varid + "length"
    Edge cases:
        - If histogram_length is empty or contains no meaningful data, histogram(...) will still be called and may produce an "empty" plot object depending on histogram implementation; this function will return the Table and an Image wrapping that result.

## Raises:
    KeyError:
        - If one of the required keys ("max_length", "median_length", "mean_length", "min_length", "histogram_length") is missing from summary, a KeyError will be raised when accessing summary[...] as there is no guard in this function.
    AttributeError:
        - If the config object does not expose the nested attributes used (config.report.precision, config.html.style, config.plot.image_format), an AttributeError will be raised when accessing them.
    TypeError / ValueError:
        - If histogram_length is of an unexpected type or contains incompatible elements for the histogram(...) function, the histogram call may raise TypeError or ValueError (propagated from histogram implementation).

## Constraints:
    Preconditions:
        - summary must be a dict containing the specified keys with appropriate numeric or iterable types.
        - config must be a Settings-like object exposing the required nested attributes.
        - varid must be a string that is safe to embed into HTML anchor ids.
    Postconditions:
        - Returns two Renderable objects (Table and Image) that are well-formed according to the report.presentation API used here.
        - Neither the Table nor the Image is written to disk or displayed by this function; they are constructed and returned for the caller to include in the report layout.

## Side Effects:
    - No I/O is performed by this function (no file or network access).
    - No global state is mutated.
    - The only external interactions are calls to:
        * fmt_number and fmt_numeric (formatting functions) for text formatting
        * histogram(config, ...) to produce plot data (may internally allocate or create image data)
        * Table(...) and Image(...) constructors from the report.presentation.core module (creating in-memory renderable objects)
    - All side effects are limited to creating and returning the in-memory Renderable objects and whatever internal behavior those constructors or histogram produce.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> BuildTable[Build length Table with max/median/mean/min]
    BuildTable --> CheckHist{Is summary["histogram_length"] a list?}
    CheckHist -->|Yes| ExtractPairs[Split into x-values and y-values lists]
    ExtractPairs --> CallHist1[Call histogram(config, x_values, y_values)]
    CheckHist -->|No| CallHist2[Call histogram(config, *summary["histogram_length"])]
    CallHist1 --> MakeImage[Create Image(rendered histogram, meta)]
    CallHist2 --> MakeImage
    MakeImage --> Return[Return (Table, Image)]
    Return --> End([End])

## Examples (usage description, non-code):
- Typical usage in report assembly:
    1. A summary generator computes per-variable statistics for a categorical/text variable and populates summary with keys listed above.
    2. The categorical renderer calls this function with the global config, the summary dict, and a chosen varid (e.g., a sanitized column name or unique id).
    3. The function returns length_table and length_histo:
        - The caller inserts length_table (Table) into the variable's information container or the left column of the variable report.
        - The caller inserts length_histo (Image) into the right column or the visualization area.
    4. When the full report is rendered to HTML, the anchor ids (f"{varid}lengthstats" and f"{varid}length") allow deep-linking to the length subsection.

- Handling absent or malformed histogram data:
    * If the summary lacks histogram_length, the caller must catch KeyError before calling this function and either skip rendering the length histogram or supply a safe default summary entry (e.g., histogram_length = ([], [])).
    * If histogram_length is present but empty, the function will still construct the Table and call histogram(...). The resulting Image may represent an empty plot depending on histogram implementation; the caller can decide to omit the Image if that is undesired.

## `src.ydata_profiling.report.structure.variables.render_categorical._get_n` · *function*

## Summary:
Compute and return the sum(s) of the provided value; supports either a list of summable objects or a pandas-like object with a sum() method.

## Description:
This helper extracts the logic for obtaining the numeric count(s) from an input that may be either:
- a list of objects (each expected to provide a sum() method), or
- a pandas-like object (the function annotation uses a DataFrame type) on which sum() can be called.

Known callers:
- No direct callers are available in the provided snippet. Typically, this function is used by categorical variable rendering routines that need to compute the total counts for one or multiple frequency-series before formatting or plotting.

Responsibility boundary:
- Centralizes and normalizes the "get total count(s)" operation so calling code does not need to branch on whether it received a single pandas-like object or a list of summable objects.

## Args:
    value (Union[list, pd.DataFrame]):
        - If a list: expected to be a list of objects that implement .sum() (for example, pandas.Series, numpy arrays wrapped in objects with sum(), or similar).
          Each element will be processed individually via v.sum().
        - If not a list: expected to be a pandas-like object (the code annotation uses pd.DataFrame) that implements .sum().
        - Interdependencies: list elements must each support .sum(); the non-list branch requires the object to support .sum().

## Returns:
    Union[int, float, pandas.Series, List[Union[int,float]]]:
        - If `value` is a list: returns a list where each element is the result of calling v.sum() on the corresponding element of the input list. Each element will typically be a numeric scalar (int/float) but is whatever v.sum() returns for that element.
        - If `value` is not a list: returns the result of calling value.sum(). For pandas.DataFrame this is usually a pandas.Series (column-wise sums). For pandas.Series this is usually a scalar (sum of the series).
        - Edge-case returns:
            * An empty list input returns an empty list.
            * An empty pandas.DataFrame returns an empty pandas.Series (consistent with pandas.DataFrame.sum()).
            * If the input contains non-numeric columns, pandas.sum() behavior (e.g., ignoring non-numeric types or producing dtype-dependent results) applies.

## Raises:
    - AttributeError: If the provided `value` (or elements of `value` when it's a list) do not implement a sum() method, the function will raise AttributeError when attempting to call .sum().
    - Any exception raised by the underlying .sum() calls (for example, TypeError from incompatible dtypes) will propagate to the caller.

## Constraints:
    Preconditions:
        - Caller must provide either:
            * a Python list whose elements implement .sum(), or
            * a pandas-like object (annotation suggests pandas.DataFrame) that implements .sum().
    Postconditions:
        - The function returns immediately with the computed sums (no mutation of input is performed).
        - No global state is modified.

## Side Effects:
    - None. The function performs no I/O, does not mutate global state, and does not modify the input objects (it only calls their sum() methods).

## Control Flow:
flowchart TD
    Start --> IsList{isinstance(value, list)}
    IsList -- Yes --> ForEach[Compute [v.sum() for v in value]]
    ForEach --> ReturnList[return list of sums]
    IsList -- No --> ComputeSingle[Compute value.sum()]
    ComputeSingle --> ReturnSingle[return result of value.sum()]
    ReturnList --> End[End]
    ReturnSingle --> End

## Examples:
    Example 1 — list of pandas.Series (common when computing multiple grouped counts):
        Given three pandas.Series objects s1, s2, s3 representing counts per group:
        calling the function with value = [s1, s2, s3] returns [s1.sum(), s2.sum(), s3.sum()].

    Example 2 — pandas.DataFrame (column-wise sums):
        Given a pandas.DataFrame df with numeric columns, calling the function with value = df returns df.sum(),
        which is typically a pandas.Series of column sums.

    Example 3 — empty inputs and error handling:
        - value = []  -> returns []
        - value = pandas.DataFrame()  -> returns an empty pandas.Series (pandas default)
        - value = [object_without_sum] -> raises AttributeError when .sum() is attempted

Note: This documentation intentionally describes observable runtime behavior rather than making assumptions about external callers not present in the provided code snippet.

## `src.ydata_profiling.report.structure.variables.render_categorical.render_categorical_unicode` · *function*

## Summary:
Constructs two presentation Renderables summarising Unicode characteristics of a categorical variable: a Table with high-level Unicode metrics and a Container (tabs) containing detailed frequency tables for characters, categories, scripts, and blocks.

## Description:
This function is used by the categorical variable reporting pipeline after Unicode/character statistics have been computed. Typical callers are the categorical variable renderer or a per-variable report builder that assembles Renderable objects for the presentation layer. The function is separated from the statistic-computation logic so presentation assembly (anchor ids, names, redact flags, sequence layout) is centralized and reusable.

Why extracted:
- Converts a validated numeric summary into presentation objects (Table, Container, FrequencyTable) while preserving a single responsibility: presentation assembly. It does not compute statistics or perform rendering I/O.

Known callers / pipeline stage:
- Called during the "render variable" stage for categorical/text variables, once the Unicode summary dict is available.

## Args:
    config (Settings):
        - Required attributes used:
            * n_freq_table_max (int): maximum number of explicit rows to include per frequency table (passed to freq_table as max_number_to_print).
            * vars.cat.redact (bool): redact flag applied to per-group FrequencyTable instances (per-category, per-script, per-block, and characters). Overview FrequencyTables set redact=False.
            * html.style (Style): passed as the Table.style for the overview Table.
        - Constraints: n_freq_table_max should be an integer >= 0; vars.cat.redact should be boolean.
    summary (dict):
        - Expected keys and value shapes (all keys are read directly; missing keys raise KeyError):
            * "category_alias_counts": Series-like counts (index=category alias, values=counts) — used to build the category overview.
            * "category_alias_char_counts": dict[str, Series-like] — mapping alias -> character counts (per-alias).
            * "script_counts": Series-like counts (index=script names) — used for script overview.
            * "script_char_counts": dict[str, Series-like] — mapping script -> character counts.
            * "block_alias_counts": Series-like counts (index=block alias names) — used for block overview.
            * "block_alias_char_counts": dict[str, Series-like] — mapping block alias -> character counts.
            * "character_counts": Series-like counts of individual characters.
            * "n_characters": int — total number of characters; used as the `n` argument for the character_counts frequency table.
            * "n_characters_distinct": int
            * "n_category": int
            * "n_scripts": int
            * "n_block_alias": int
        - Series-like objects must be consumable by freq_table and _get_n (i.e., support .sum() and __len__ as applicable).
    varid (str):
        - Prefix string used to build anchor_id values for produced Renderables. It is concatenated directly with suffixes (no sanitization performed).

## Returns:
    Tuple[Renderable, Renderable]
    - overview_table (Table):
        - Name: "Characters and Unicode"
        - Rows: a sequence of dicts for:
            * "Total characters" -> value fmt_number(summary["n_characters"])
            * "Distinct characters" -> fmt_number(summary["n_characters_distinct"])
            * "Distinct categories" -> fmt_number(summary["n_category"]) with a help(...) hint to Unicode categories URL
            * "Distinct scripts" -> fmt_number(summary["n_scripts"]) with a help(...) hint to Unicode scripts URL
            * "Distinct blocks" -> fmt_number(summary["n_block_alias"]) with a help(...) hint to Unicode blocks URL
        - Caption: explanatory text about Unicode (as in source).
        - Style: config.html.style
    - unicode_container (Container):
        - A Container with sequence_type="tabs" and anchor_id f"{varid}unicode" containing four named Containers (sequence_type="named_list"):
            1. Characters: contains one FrequencyTable named "Most occurring characters" with:
                - rows = freq_table(freqtable=summary["character_counts"], n=summary["n_characters"], max_number_to_print=n_freq_table_max)
                - redact = config.vars.cat.redact
                - anchor_id = f"{varid}character_frequency"
            2. Categories: a nested structure:
                - category_overview: FrequencyTable from summary["category_alias_counts"]:
                    * rows = freq_table(freqtable=summary["category_alias_counts"], n=_get_n(summary["category_alias_counts"]), max_number_to_print=n_freq_table_max)
                    * name = "Most occurring categories"
                    * anchor_id = f"{varid}category_long_values"
                    * redact = False
                - per-category Container: sequence_type="batch_grid", batch_size=1, subtitles=True, anchor_id f"{varid}categories"
                    * Iteration order: sorted(summary["category_alias_char_counts"].items(), key=lambda x: -len(x[1]))
                    * For each (category_alias_name, category_alias_counts):
                        - display name = category_alias_name.replace('_', ' ')
                        - anchor_id = f"{varid}category_alias_values_{category_alias_name.replace('_', ' ')}"
                        - rows = freq_table(freqtable=category_alias_counts, n=_get_n(category_alias_counts), max_number_to_print=n_freq_table_max)
                        - redact = config.vars.cat.redact
            3. Scripts:
                - script_overview: FrequencyTable from summary["script_counts"], redact=False, anchor_id f"{varid}script_values"
                - per-script Container: sequence_type="batch_grid", batch_size=1, subtitles=True, anchor_id f"{varid}scripts"
                    * Iteration order: sorted(summary["script_char_counts"].items(), key=lambda x: -len(x[1]))
                    * For each (script_name, script_counts):
                        - name = script_name (NO underscore-to-space replacement in source)
                        - anchor_id = f"{varid}script_values_{script_name}"
                        - rows = freq_table(freqtable=script_counts, n=_get_n(script_counts), max_number_to_print=n_freq_table_max)
                        - redact = config.vars.cat.redact
            4. Blocks:
                - block_overview: FrequencyTable from summary["block_alias_counts"], redact=False, anchor_id f"{varid}block_alias_values"
                - per-block Container: sequence_type="batch_grid", batch_size=1, subtitles=True, anchor_id f"{varid}blocks"
                    * Iteration order: summary["block_alias_char_counts"].items() (dict iteration order; source does not sort)
                    * For each (block_name, block_counts):
                        - name = block_name (NO underscore-to-space replacement in source)
                        - anchor_id = f"{varid}block_alias_values_{block_name}"
                        - rows = freq_table(freqtable=block_counts, n=_get_n(block_counts), max_number_to_print=n_freq_table_max)
                        - redact = config.vars.cat.redact
    - Note on anchor ids:
        - Only category alias display names are transformed via .replace("_", " ") in the source; those transformed strings are used both as the FrequencyTable.name and embedded in the anchor_id (which may therefore contain spaces).
        - For scripts and blocks the source uses the raw name values as-is for FrequencyTable.name and anchor ids (no replacement).
        - The function does not sanitize or escape varid or the name strings before embedding them into anchor ids; callers should ensure values are safe for the target rendering environment.

## Raises:
    - No explicit raises in the function body, but the following errors can propagate:
        * KeyError: if required keys are missing from summary.
        * AttributeError: if counts objects do not provide expected methods/attributes used by _get_n() or freq_table().
        * TypeError / ValueError: if fmt_number or freq_table operations receive incompatible types.
        * Any exception raised by freq_table/_frequency_table (e.g., ZeroDivisionError when n == 0) will propagate unchanged.

## Constraints:
    Preconditions:
        - summary contains all required keys with compatible types (see Args).
        - config has the required attributes (n_freq_table_max, vars.cat.redact, html.style).
        - varid is a string; the function does not sanitize it.
    Postconditions:
        - Returns (Table, Container) assembled from the provided inputs.
        - Input summary and config are not mutated.

## Side Effects:
    - None observable beyond constructing Renderable objects (no file/network I/O, no global state mutation).
    - The function calls helper utilities (fmt_number, help, freq_table, _get_n) which are expected to be pure; any side effects from them (none expected) will surface to the caller.

## Control Flow:
flowchart TD
    Start --> Read n_freq_table_max from config
    ReadConfig --> Build category overview FrequencyTable (uses _get_n on category_alias_counts)
    BuildCategoryOverview --> Iterate category_alias_char_counts (sorted by -len(counts))
    IterateCategories --> Create per-category FrequencyTables (replace '_' -> ' ' for display name and anchor_id suffix)
    CreatePerCategoryTables --> Build category Container (batch_grid, batch_size=1, subtitles=True)
    BuildCategoryContainer --> Build script overview FrequencyTable
    BuildScriptOverview --> Iterate script_char_counts (sorted by -len(counts))
    IterateScripts --> Create per-script FrequencyTables (use raw script_name for name and anchor_id)
    CreatePerScriptTables --> Build script Container (batch_grid)
    BuildScriptContainer --> Build block overview FrequencyTable
    BuildBlockOverview --> Iterate block_alias_char_counts (dict order, unsorted)
    IterateBlocks --> Create per-block FrequencyTables (use raw block_name for name and anchor_id)
    CreatePerBlockTables --> Build block Container (batch_grid)
    BuildBlockContainer --> Create overview Table rows (fmt_number, help URLs)
    CreateOverviewTable --> Assemble citems list (Characters, Categories, Scripts, Blocks)
    AssembleCItems --> Return (overview_table, Container(tabs, citems))

## Examples:
Example — minimal valid `summary` and usage:
    summary = {
        "category_alias_counts": pandas.Series([10, 5], index=["A", "B"]),
        "category_alias_char_counts": {
            "A": pandas.Series([6, 4], index=["x", "y"]),
            "B": pandas.Series([3, 2], index=["x", "z"]),
        },
        "script_counts": pandas.Series([12], index=["Latin"]),
        "script_char_counts": {"Latin": pandas.Series([12], index=["x"])},
        "block_alias_counts": pandas.Series([12], index=["Basic_Latin"]),
        "block_alias_char_counts": {"Basic_Latin": pandas.Series([12], index=["x"])},
        "character_counts": pandas.Series([12], index=["x"]),
        "n_characters": 12,
        "n_characters_distinct": 1,
        "n_category": 2,
        "n_scripts": 1,
        "n_block_alias": 1,
    }
    overview_table, unicode_tabs = render_categorical_unicode(config, summary, varid="var123_")

Error handling example:
    try:
        overview_table, unicode_tabs = render_categorical_unicode(config, summary, varid="v_")
    except KeyError as e:
        handle_missing_summary_key(e)
    except Exception as e:
        handle_generic_error(e)

Implementation checklist (for reimplementation):
- Use config.n_freq_table_max as max_number_to_print in freq_table calls.
- Use _get_n(obj) to compute n for freq_table for overview and per-group counts as in the source; use summary["n_characters"] directly for the character-frequency table n argument.
- For categories only: call category_alias_name = category_alias_name.replace("_", " ") prior to constructing FrequencyTable.name and anchor_id suffix.
- For scripts and blocks: use script_name and block_name exactly as provided by the summary dict (no underscore-to-space replacement in the source).
- For categories and scripts, sort items by descending len(counts) using key=lambda x: -len(x[1]); for blocks iterate the dict as-is.
- Set redact=False for overview FrequencyTables and redact=config.vars.cat.redact for per-group and character FrequencyTables.
- Always return a (Table, Container) tuple and do not render the renderables in this function.

## `src.ydata_profiling.report.structure.variables.render_categorical.render_categorical` · *function*

## Summary:
Assembles and returns a template-variables dictionary of presentation-ready renderables for a categorical variable section of the profiling report — packaging variable info, summary metrics, compact and full frequency tables, optional length/word/character subsections, and plots according to configuration flags.

## Description:
- Known callers / typical pipeline stage:
    - Invoked during the per-variable report assembly phase for variables classified as categorical/text. Typical callers are the variable-rendering orchestration code that iterates over dataset columns after the statistics-collection stage has produced a per-variable summary dict.
    - Trigger: given a summary dict for a categorical variable, call this function to convert numerical/text statistics into presentation Renderable objects for inclusion in the final HTML report.
- Why this is a separate function:
    - Concentrates presentation assembly (layout decisions, anchor id construction, conditional inclusion of subsections, and invocation of plotting/formatting utilities) for categorical variables. It keeps high-level orchestration separate from presentation details and delegates specialized rendering tasks (unique stats, length, unicode) to dedicated helper functions.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Attributes read:
            * vars.cat.n_obs (int) — number of top category rows to show in FrequencyTableSmall
            * vars.cat.words (bool) — whether to include "Common words"
            * vars.cat.characters (bool) — whether to include Unicode/character sections
            * vars.cat.length (bool) — whether to include length statistics/histogram
            * vars.cat.redact (bool) — redact toggle that controls sample visibility and redact flags
            * plot.image_format (str) — image format for Image renderables
            * plot.cat_freq.show (bool) — whether to render category frequency plots
            * plot.cat_freq.max_unique (int) — maximum unique categories allowed for plotting
            * html.style (Style-like) — style passed to presentation widgets
            * html.style._labels (sequence) — labels used when summary provides multiple labelled variants (list-shaped fields)
        - Preconditions: config must expose these nested attributes. Missing attributes will raise AttributeError.

    summary (dict):
        - Type: dict
        - Always-required keys (this function indexes these directly):
            * "varid" (str) — unique identifier used to build anchor ids
            * "varname" (str) — human-readable variable name for display
            * "type" (str or list) — variable type; if list, the first element is used
            * "alerts" (iterable) — alerts passed to VariableInfo
            * "description" (str) — description to show in VariableInfo
            * "alert_fields" (iterable[str]) — names of fields that should be displayed with an alert marker if present
            * "n_distinct" (int or sequence) — distinct count (scalar or per-label sequence)
            * "p_distinct" (float or sequence) — distinct proportion (0..1) (scalar or per-label sequence)
            * "n_missing" (int or sequence) — number of missing observations
            * "p_missing" (float or sequence) — missing proportion (0..1)
            * "memory_size" (int) — memory footprint in bytes
            * "value_counts_without_nan" (pandas.Series or list[pandas.Series]) — frequencies excluding NaN; if list, must align with html.style._labels
            * "first_rows" (sequence or list-of-sequences) — first observed values used to construct the Sample table
        - Keys used by helpers (conditionally required or expected by different helpers):
            * render_common expects summary["n"] (numeric) for building freq_table rows used in full frequency table.
            * FrequencyTableSmall in this function is built using summary["count"], i.e., this function reads summary["count"] to supply the n argument for the compact frequency table. To avoid mismatch, callers should ensure summary["n"] and summary["count"] are provided consistently (common profiling pipelines set both or alias them to the same value).
            * If config.vars.cat.length is True: keys required by render_categorical_length such as "max_length", "median_length", "mean_length", "min_length", "histogram_length".
            * If config.vars.cat.characters is True: keys required by render_categorical_unicode (e.g., "category_alias_counts", "category_alias_char_counts", "script_counts", "script_char_counts", "block_alias_counts", "block_alias_char_counts", "character_counts", "n_characters", "n_characters_distinct", "n_category", "n_scripts", "n_block_alias").
            * If config.vars.cat.words is True: "word_counts" is expected.
        - Interdependencies:
            * If summary["value_counts_without_nan"] is a list, its length must equal len(config.html.style._labels).
            * Multi-variant plotting logic assumes each list element corresponds to a label in html.style._labels.

## Returns:
    dict:
        - A mapping of template variables used by the report renderer. Important keys:
            * All keys returned by render_common(...) are included (explicitly: "freq_table_rows", "firstn_expanded", "lastn_expanded").
            * "top": Container — contains VariableInfo, the metrics Table (Distinct, Distinct (%), Missing, Missing (%), Memory size) and a FrequencyTableSmall of top categories.
            * "bottom": Container (sequence_type="tabs") — typically contains:
                - an "Overview" container with overview items (Length table, Unicode overview, Unique stats table, optional Sample table)
                - a "Categories" container containing the full frequency table and category visualizations or placeholders
            * Optional Containers appended into "bottom" for "Words" and "Characters" if enabled and data present.
        - Shape variability:
            * The returned dict always includes template variables produced by render_common plus the "top" and "bottom" containers; presence of subsections depends on config flags and the availability of corresponding summary keys.

## Raises:
    - KeyError:
        - If any required summary key (see Args) is missing, indexing summary[...] will raise KeyError.
    - AttributeError:
        - If required nested attributes are missing on config (e.g., config.html.style or config.plot.cat_freq), attribute access will raise AttributeError.
    - TypeError / ValueError:
        - If values are incompatible with formatters (fmt, fmt_percent, fmt_bytesize, fmt_number) or plotting utilities (cat_frequency_plot, histogram) those functions may raise TypeError/ValueError which propagate.
    - Error propagation policy:
        - The helper functions used here (render_common, freq_table, render_categorical_frequency, render_categorical_length, render_categorical_unicode, cat_frequency_plot) are presentation-focused and do not perform I/O. This function does not catch exceptions from those helpers: errors caused by malformed inputs or lower-level formatting/plotting code will propagate to the caller. Callers should validate summary data before invoking this renderer.

## Constraints:
- Preconditions:
    - summary must be constructed by the profiling statistics stage and include required keys with expected shapes and numeric types.
    - For list-shaped summary entries, lengths must align with config.html.style._labels.
    - config must be a valid Settings object exposing the nested attributes referenced above.
- Postconditions:
    - Returns a dict where "top" and "bottom" are Container renderables, and where "freq_table_rows" from render_common is present for downstream rendering.
    - Does not mutate global state.

## Side Effects:
- No filesystem or network I/O performed directly by this function.
- Constructs in-memory presentation objects and calls plotting helpers (cat_frequency_plot, histogram via helpers). Those may allocate in-memory plot objects; this function does not persist them.
- No mutation of global variables or caches.

## Anchor IDs created (examples based on varid):
    - f"{varid}common_values"            — full "Common Values" FrequencyTable
    - f"{varid}cat_frequency_plot"       — Container anchor for per-label category plots
    - f"{varid}cat_frequency_plot_{idx}" — per-label Image/HTML placeholder anchor when value_counts_without_nan is a list
    - f"{varid}overview"                 — Overview container anchor
    - f"{varid}string"                   — Categories container anchor
    - f"{varid}bottom"                   — bottom-level tabs anchor
    - f"{varid}cwo"                      — Common words FrequencyTable anchor
    - f"{varid}word"                     — Words container anchor
    - f"{varid}characters"               — Characters container anchor
    - f"{varid}lengthstats"              — Length Table anchor (from render_categorical_length)
    - f"{varid}length"                   — Length histogram Image anchor (from render_categorical_length)
    - Additional anchors delegated to helpers, e.g.:
        * render_categorical_length uses f"{varid}lengthstats" and f"{varid}length"
        * render_categorical_unicode uses anchors like f"{varid}unicode", f"{varid}character_frequency", f"{varid}category_long_values", f"{varid}categories", f"{varid}scripts", f"{varid}blocks", f"{varid}block_alias_values_<name>", etc.
        * render_categorical_frequency typically constructs an anchor such as f"{varid}_unique_stats"

## Control Flow:
flowchart TD
    Start([Start]) --> ReadConfig[Read config booleans and thresholds]
    ReadConfig --> CallRenderCommon[template_variables := render_common(config, summary)]
    CallRenderCommon --> NormalizeType{Use summary["type"]; if list take first element}
    NormalizeType --> BuildInfo[Create VariableInfo(...)]
    BuildInfo --> BuildTable[Create metrics Table (Distinct, Distinct (%), Missing, Missing (%), Memory size)]
    BuildTable --> BuildFQM[Create FrequencyTableSmall from summary["value_counts_without_nan"], n=summary["count"], max_number_to_print=config.vars.cat.n_obs]
    BuildFQM --> SetTop[template_variables["top"] = Container([info, table, fqm])]
    SetTop --> BuildFrequencyTable[frequency_table = FrequencyTable(template_variables["freq_table_rows"], anchor_id=f"{varid}common_values")]
    BuildFrequencyTable --> CallUnique[unique_stats := render_categorical_frequency(config, summary, varid)]
    CallUnique --> InitOverview[overview_items = []]
    InitOverview --> CheckLength{if config.vars.cat.length and "max_length" in summary}
    CheckLength -->|yes| CallLength[call render_categorical_length -> (length_table, length_histo); overview_items.append(length_table)]
    CallLength --> CheckCharacters{if config.vars.cat.characters and "category_alias_counts" in summary}
    CheckCharacters -->|yes| CallUnicode[call render_categorical_unicode -> (overview_table_char, unitab); overview_items.append(overview_table_char)]
    CheckCharacters --> AppendUnique[overview_items.append(unique_stats)]
    AppendUnique --> CheckRedact{if not config.vars.cat.redact}
    CheckRedact -->|not redact| BuildSample[Create Sample Table from summary["first_rows"] and overview_items.append(sample)]
    BuildSample --> BuildStringItems[string_items = [frequency_table]; if length then append length_histo]
    BuildStringItems --> PlotDecision{if config.plot.cat_freq.show and config.plot.cat_freq.max_unique > 0}
    PlotDecision -->|True and value_counts_without_nan is list| BuildContainerPlot[Create per-label Images or HTML placeholders inside Container anchor f"{varid}cat_frequency_plot"]
    PlotDecision -->|True and single-label| SinglePlot[If n_distinct <= max_unique: append single Image]
    BuildContainerPlot --> BuildBottom[Construct bottom_items with Overview and Categories containers]
    BuildBottom --> WordsCheck{if config.vars.cat.words and "word_counts" in summary}
    WordsCheck -->|yes| BuildWords[Create FrequencyTable for words and append as "Words" Container]
    WordsCheck --> CharactersCheck{if config.vars.cat.characters and "category_alias_counts" in summary}
    CharactersCheck -->|yes| AppendUnicodeContainer[Append unitab to bottom_items]
    AppendUnicodeContainer --> FinalizeBottom[template_variables["bottom"] = Container(bottom_items, sequence_type="tabs", anchor_id=f"{varid}bottom")]
    FinalizeBottom --> Return[return template_variables]

## Examples:
- Happy-path (single-label):
    - Preconditions: summary contains required keys; config enables length/characters/words; summary["value_counts_without_nan"] is a pandas.Series and both summary["n"] and summary["count"] are present or equivalent.
    - Outcome: template_variables["top"] contains VariableInfo, the metrics Table and a FrequencyTableSmall of the top n_obs categories; template_variables["bottom"] contains Overview and Categories tabs with length Table, Unicode overview, Unique stats, Sample (if not redacted), Category frequency Image (if n_distinct <= max_unique), and Words/Characters tabs if data present.

- Multi-label example:
    - If summary["value_counts_without_nan"] is a list with one Series per label and config.html.style._labels contains the corresponding labels, the Categories container will include a Container with one Image or placeholder per label depending on the per-label unique count thresholds.

- Error handling:
    - Missing required keys (e.g., "value_counts_without_nan", "first_rows") or incompatible types for formatters/plotters will produce exceptions (KeyError, TypeError, ValueError, etc.) propagated from this function or its helpers. Callers should validate/normalize summary inputs before calling.

