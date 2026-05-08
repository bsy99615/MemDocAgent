# `render_text.py`

## `src.ydata_profiling.report.structure.variables.render_text.render_text` · *function*

## Summary:
Assembles presentation objects (Containers, Tables, Images, FrequencyTable, VariableInfo) into a template_variables dictionary for rendering a profiling report section of a text variable, honoring configuration flags (redaction, words, characters, length) and available summary data.

## Description:
Transforms a precomputed per-variable summary and global Settings into the templating structures the reporting renderer expects. The function decides which UI components to include (top metadata, formatted stats, mini and full wordclouds, frequency tables, length/character summaries, and sample rows), formats scalar values for display, and constructs anchor IDs used in the final report.

Known callers and trigger conditions:
- Called by the report generation pipeline when rendering an individual variable that has been classified as text (the variable-level render dispatcher).
- Early delegation: if config.vars.text.redact is True, the function immediately calls and returns render_categorical(config, summary) (delegation avoids showing raw text content).

Why this is a separate function:
- Encapsulates presentation composition and conditional logic for text variables, keeping feature toggles and rendering decisions centralized and testable, while leaving summary computation and final HTML conversion to other modules.

## Args:
    config (Settings)
        - The global Settings instance. Exact attributes read by this function:
            * config.vars.text.redact (bool)
            * config.vars.text.words (bool)
            * config.vars.text.characters (bool)
            * config.vars.text.length (bool)
            * config.html.style (any) — passed to Table/Container/VariableInfo constructors
            * config.plot.image_format (str) — passed to Image(image_format=...)
        - Behavior: if config.vars.text.redact is True, the function delegates to render_categorical and returns its result without constructing other objects.

    summary (Dict[str, Any])
        - Per-variable summary dictionary produced earlier in the profiling pipeline. Keys used (required vs conditional):
            * Required for non-redacted path:
                - "varid" (str): used to create anchor_id strings, e.g., f"{varid}overview", f"{varid}bottom".
                - "varname" (str)
                - "type" (str)
                - "alerts" (list-like)
                - "description" (str)
                - "n_distinct" (int)
                - "p_distinct" (float)
                - "n_missing" (int)
                - "p_missing" (float)
                - "memory_size" (int)
                - "alert_fields" (iterable of str): used with membership checks for "n_distinct", "p_distinct", "n_missing", "p_missing"
                - "first_rows" (iterable) — used to build the "Sample" Table (see shapes below)
            * Conditionally required (only when corresponding config.flag is True):
                - "word_counts" — required if config.vars.text.words is True; shape must be compatible with freq_table(...) and plot_word_cloud(...)
                - "max_length" — required if config.vars.text.length is True (used by render_categorical_length)
                - "category_alias_counts" — required if config.vars.text.characters is True (used by render_categorical_unicode)
        - Format notes for "first_rows":
            * Case A — list shape (isinstance(summary["first_rows"], list) is True):
                - The implementation performs zip(rows, *summary["first_rows"]) and then iterates with for name, *value in zip(...).
                - Interpretation: summary["first_rows"] should be a list of iterables; for each row label the comprehension collects one element from each iterable in the list into the list `value`. Thus each Table cell's value becomes a list with length equal to len(summary["first_rows"]) (which will then be passed to fmt()).
            * Case B — non-list iterable:
                - The implementation performs zip(rows, summary["first_rows"]) and for each pair uses the single scalar value for the Table cell (passed to fmt()).
            * zip truncation: zip will stop at the shortest input; if fewer than five values are available, the resulting Sample Table will contain correspondingly fewer rows (no explicit padding is performed).
        - Callers must ensure the presence and shape of keys that the enabled features require; otherwise the function will raise KeyError or type-related exceptions when trying to access or iterate unexpected structures.

## Returns:
    Dict[str, Any]
        - Returns a dictionary template_variables (starting from render_common(config, summary) and augmented by this function) with the following keys and types:
            * "top": Container (sequence_type="grid") containing:
                - VariableInfo instance with:
                    + anchor_id = summary["varid"]
                    + var_name = summary["varname"]
                    + var_type = summary["type"]
                    + alerts = summary["alerts"]
                    + description = summary["description"]
                    + style = config.html.style
                - Table instance representing summary rows (list of row-dicts with keys "name", "value", "alert"):
                    + "Distinct" -> value = fmt(summary["n_distinct"]), alert True if "n_distinct" in summary["alert_fields"]
                    + "Distinct (%)" -> value = fmt_percent(summary["p_distinct"]), alert True if "p_distinct" in summary["alert_fields"]
                    + "Missing" -> value = fmt(summary["n_missing"]), alert True if "n_missing" in summary["alert_fields"]
                    + "Missing (%)" -> value = fmt_percent(summary["p_missing"]), alert True if "p_missing" in summary["alert_fields"]
                    + "Memory size" -> value = fmt_bytesize(summary["memory_size"]), alert False
                - Optional Image instance (mini wordcloud) created only when config.vars.text.words is True and "word_counts" in summary:
                    + image data returned by plot_word_cloud(config, summary["word_counts"])
                    + image_format = config.plot.image_format
                    + alt = "Mini wordcloud"
            * "bottom": Container (sequence_type="tabs", anchor_id=f"{varid}bottom") containing:
                - An Overview Container (sequence_type="batch_grid", anchor_id=f"{varid}overview", batch_size=len(overview_items), titles=False) whose items include, in order:
                    + length_table (first element returned by render_categorical_length(config, summary, varid)) when config.vars.text.length True and "max_length" in summary
                    + overview_table_char (returned by render_categorical_unicode(config, summary, varid)) when config.vars.text.characters True and "category_alias_counts" in summary
                    + unique_stats (returned by render_categorical_frequency(config, summary, varid)) — always appended
                    + Sample Table (name="Sample", style=config.html.style) when config.vars.text.redact is False — constructed from summary["first_rows"] as described above
                - Optional "Words" Container (sequence_type="grid", anchor_id=f"{varid}word") when config.vars.text.words True and "word_counts" in summary, containing:
                    + FrequencyTable instance constructed from woc where:
                        - woc = freq_table(freqtable=summary["word_counts"], n=_get_n(summary["word_counts"]), max_number_to_print=10)
                        - FrequencyTable parameters: (woc, name="Common words", anchor_id=f"{varid}cwo", redact=config.vars.text.redact)
                    + Image instance with full wordcloud: Image(plot_word_cloud(config, summary["word_counts"]), image_format=config.plot.image_format, alt="Wordcloud")
                - Optional "Characters" Container (sequence_type="grid", anchor_id=f"{varid}characters") containing unitab if render_categorical_unicode returned it.
        - Redaction short-circuit:
            * If config.vars.text.redact is True, the function returns immediately the value returned by render_categorical(config, summary). No other objects are created.

## Raises:
    KeyError
        - If expected keys listed in Args are missing from summary when accessed (examples: "varid", "n_distinct", "first_rows", or conditional keys like "word_counts" when a config flag requires them).
    TypeError / ValueError
        - Possible when summary["first_rows"] has unexpected shape for the branch taken, or when downstream helpers receive incompatible input shapes.
    No custom exceptions are raised by this function itself.

## Constraints:
    Preconditions:
        - config must implement the attributes enumerated above.
        - summary must contain the basic metadata and statistics; if feature flags are enabled, corresponding summary fields must be present and compatible with helper functions.
    Postconditions:
        - On success (non-redacted path), template_variables contains "top" and "bottom" keys with fully populated Container presentation objects as described.
        - On redacted path, return value is exactly whatever render_categorical(config, summary) returned.

## Side Effects:
    - Calls into these helper/rendering utilities:
        * render_common(config, summary)
        * render_categorical(config, summary) (delegation on redact)
        * render_categorical_length(config, summary, varid)
        * render_categorical_unicode(config, summary, varid)
        * render_categorical_frequency(config, summary, varid)
        * freq_table(...) and _get_n(...) to prepare a limited frequency list
        * plot_word_cloud(config, summary["word_counts"]) to generate image payloads for Image objects
    - Constructs presentation objects: VariableInfo, Table, FrequencyTable, Image, Container.
    - Does not perform file, network, or stdout I/O and does not mutate global state.

## Control Flow:
flowchart TD
    Start[Start: render_text(config, summary)] --> CheckRedact{config.vars.text.redact?}
    CheckRedact -- True --> ReturnCat[RETURN render_categorical(config, summary)]
    CheckRedact -- False --> ExtractFlags[Read flags: words, characters, length; varid = summary["varid"]]
    ExtractFlags --> BaseTemplate[template_variables = render_common(config, summary)]
    BaseTemplate --> BuildTop[Create VariableInfo + stats Table]
    BuildTop --> WordsMini?{words True AND "word_counts" in summary?}
    WordsMini? -- Yes --> AddMiniImage[Create mini Image via plot_word_cloud -> append to top_items]
    WordsMini? -- No --> SkipMini
    AddMiniImage --> SetTop[Set template_variables["top"] = Container(top_items, grid)]
    SkipMini --> SetTop
    SetTop --> PrepareOverview[overview_items = []]
    PrepareOverview --> Length?{length True AND "max_length" in summary?}
    Length? -- Yes --> AddLength[render_categorical_length -> append length_table]
    Length? -- No --> SkipLength
    AddLength --> Char?{characters True AND "category_alias_counts" in summary?}
    SkipLength --> Char?
    Char? -- Yes --> AddChar[render_categorical_unicode -> append overview_table_char and set unitab]
    Char? -- No --> unitabNone[unitab = None]
    AddChar --> AddUnique[render_categorical_frequency -> append unique_stats]
    unitabNone --> AddUnique
    AddUnique --> Sample?{not config.vars.text.redact?}
    Sample? -- True --> BuildSample[Create Sample Table from summary["first_rows"] (handles two shapes) -> append]
    Sample? -- False --> SkipSample
    BuildSample --> OverviewContainer[Create Overview Container -> append to bottom_items]
    OverviewContainer --> WordsBlock?{words True AND "word_counts" in summary?}
    WordsBlock? -- Yes --> BuildWords[Create freq_table, FrequencyTable, Image -> append Words Container]
    WordsBlock? -- No --> SkipWords
    BuildWords --> UnitabCheck{unitab is not None?}
    SkipWords --> UnitabCheck
    UnitabCheck -- True --> AppendChars[Append Characters Container with unitab]
    UnitabCheck -- False --> SkipChars
    AppendChars --> SetBottom[Set template_variables["bottom"] = Container(bottom_items, tabs)]
    SkipChars --> SetBottom
    SetBottom --> ReturnVars[Return template_variables]

## Examples:
- Example A: sample rows as simple iterable (most common)
    summary["first_rows"] = ["first example", "second example", "third example"]
    - The Sample Table will pair "1st row" -> "first example", "2nd row" -> "second example", etc. If fewer than five values are provided, the table contains fewer rows (zip truncation).

- Example B: sample rows as list-of-iterables (multi-valued sample cells)
    summary["first_rows"] = [
        ["row1_col1", "row2_col1", ...],
        ["row1_col2", "row2_col2", ...]
    ]
    - The comprehension uses zip(rows, *summary["first_rows"]) and for each label produces value as a list of elements taken from each inner iterable. Each Sample Table cell value becomes a list (formatted by fmt) containing corresponding values from each inner iterable.

- Practical usage (conceptual):
    - The profiling pipeline produces `summary` for a text variable (including tokenization results if enabled).
    - Call template_variables = render_text(config, summary)
    - The rendering engine consumes template_variables["top"] and template_variables["bottom"] to produce the final HTML/JSON for that variable's section.

- Failure scenario:
    - If config.vars.text.words is enabled but summary lacks "word_counts", a KeyError will be raised when the function attempts to access summary["word_counts"]. Disable the corresponding feature or ensure the summary includes required keys.

