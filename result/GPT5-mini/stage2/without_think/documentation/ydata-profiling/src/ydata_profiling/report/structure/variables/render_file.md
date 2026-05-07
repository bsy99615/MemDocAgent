# `render_file.py`

## `src.ydata_profiling.report.structure.variables.render_file.render_file` · *function*

## Summary:
Generates and returns the template variables for rendering a "File" variable section in the report by building file-specific presentation components (histogram image and frequency tables) and appending them to the provided template structure.

## Description:
This function prepares UI components for file-typed variables and integrates them into the existing template variables produced by the common path renderer.

Known callers:
- Not explicitly referenced within this file. Typically this function is invoked by the variables rendering pipeline when a dataset variable has been classified as a file-type (i.e., inside a dispatcher that selects a render_* function based on variable type). In that pipeline stage, each variable summary dict is passed to the specialized render function for that variable type.

Why this is a separate function:
- It encapsulates the file-specific rendering logic (histogram of file sizes and date-related frequency tables), keeping the common path rendering (handled by render_path) separate from the file-specific UI composition. This enforces a clear responsibility boundary: render_path builds the shared template skeleton; render_file populates file-specific tabs and appends them to the template.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Description: Global configuration object. Used to access visualization and rendering options used below:
            * config.n_freq_table_max: maximum number of rows to show in frequency tables
            * config.plot.image_format: image format passed to Image presentation component
        - Required: yes

    summary (dict):
        - Type: dict
        - Description: Variable summary dictionary produced earlier in the profiling pipeline. The function reads the following keys (presence rules given alongside):
            * "varid" (str) — REQUIRED. Unique variable identifier used to build anchor_id strings.
            * "n" (int) — REQUIRED if any file date fields are present (used as total count in freq_table).
            * "file_size" (any) — Optional flag/key used to indicate that size/histogram info is available.
            * "histogram_file_size" (sequence-like, e.g., tuple) — Required when "file_size" is present. Expected to be an object unpackable into args accepted by histogram(config, ...), where the second element contains bin edges (used to compute displayed bin count).
            * "file_created_time", "file_accessed_time", "file_modified_time" (values with .value_counts()):
                - Optional. If present, each is expected to be an object supporting a value_counts() call (for example, a pandas Series). Their value_counts() result is used to create a FrequencyTable via freq_table(...).
        - Notes: Other keys and structure may be present but are not used by this function.

## Returns:
    dict: The template_variables dictionary returned by render_path(config, summary) but mutated with file-specific UI components appended:
        - The "top" template's first item's "var_type" is set to "File".
        - A new Container named "File" (sequence_type="tabs") is appended to template_variables["bottom"].content["items"]. This container holds:
            * An Image component for file size histogram (if "file_size" in summary).
            * One FrequencyTable per present file date field (Created/Accessed/Modified).
    Edge-case returns:
        - If none of the optional fields are present (no file_size and no file date entries), the returned dict is still the template_variables but with an appended empty "File" Container (with no children inside its tabs list).

## Raises:
    KeyError:
        - If "varid" is missing from summary (accessed immediately).
        - If "file_size" is present in summary but "histogram_file_size" is missing (unpacking/usage will raise KeyError).
        - If any expected mandatory keys referenced in the summary usage are missing.
    AttributeError:
        - If an expected file date field is present but its value does not implement value_counts(), calling .value_counts() will raise AttributeError.
    Any exceptions raised by called functions:
        - histogram(config, ...), freq_table(...), Image(...), FrequencyTable(...), and render_path(...) may raise their own exceptions which will propagate. Examples include errors from plotting libraries or invalid configuration values.

## Constraints:
Preconditions:
    - summary must contain "varid" (string).
    - The Settings object must have the attributes used: n_freq_table_max and plot.image_format.
    - If "file_size" is present, "histogram_file_size" must provide the expected structure that histogram(...) accepts.
    - If any file date keys are present, their values must support .value_counts() semantics.

Postconditions:
    - The returned dictionary is the same object produced by render_path(config, summary) but mutated:
        * top.content.items[0].content.var_type == "File"
        * bottom.content.items contains a new Container with anchor_id f"{varid}file" and child renderables representing file visuals/tables
    - No external files or network calls are performed by this function itself (rendering backends may perform I/O).

## Side Effects:
    - Mutates the template_variables dict returned by render_path (in-place modification).
    - Constructs presentation objects (Image, FrequencyTable, Container) but does not itself write files or network calls.
    - Calls histogram(...) to create the image data used as the Image content — any heavy computations or library calls happen inside histogram.
    - No global state in this function is modified.

## Control Flow:
flowchart TD
    Start[Start] --> GetVarid[Read summary["varid"]]
    GetVarid --> RenderPath[Call render_path(config, summary)]
    RenderPath --> SetVarType[Set template_variables["top"].content["items"][0].content["var_type"]="File"]
    SetVarType --> InitTabs[Initialize empty file_tabs list]
    InitTabs --> CheckFileSize{Is "file_size" in summary?}
    CheckFileSize -- Yes --> MakeHistogram[Call histogram(config, *summary["histogram_file_size"])]
    MakeHistogram --> AppendImage[Create Image(...) and append to file_tabs]
    CheckFileSize -- No --> SkipHistogram[Skip histogram]
    AppendImage --> DateLoop[For each file date key in (created, accessed, modified)]
    SkipHistogram --> DateLoop
    DateLoop --> DateEntry{Is file_date key in summary?}
    DateEntry -- Yes --> CreateFreqTable[Call value_counts() then freq_table(...)]
    CreateFreqTable --> AppendFreq[Create FrequencyTable(...) and append to file_tabs]
    DateEntry -- No --> NextDate[Continue loop]
    NextDate --> DateEntry
    AppendFreq --> NextDate
    DateLoop --> MakeContainer[Create Container(file_tabs, name="File", sequence_type="tabs")]
    MakeContainer --> AppendToBottom[Append container to template_variables["bottom"].content["items"]]
    AppendToBottom --> Return[Return template_variables]
    Return --> End[End]

## Examples (usage scenario):
- Typical usage context (described in steps):
    1. Upstream, each variable in the profiling pipeline is summarized into a dictionary (summary) and classified with a type (e.g., "file").
    2. The main report renderer chooses render_file for file-typed variables and calls render_file(config, summary).
    3. render_file mutates the returned template variables to include a "File" tab container with:
        - A histogram image of file sizes when size data is available.
        - Frequency tables for created/accessed/modified times when those series are present.
    4. The caller then embeds this template_variables dictionary into the larger report HTML/template rendering process.

- Error handling guidance:
    * If you supply summary dictionaries from external sources, validate presence of "varid" and any keys you expect ("histogram_file_size", date fields) before calling render_file to avoid KeyError or AttributeError.
    * If a file date column may be absent or have unexpected types, pre-normalize it to a pandas Series (or an object implementing .value_counts()) so freq_table(...) receives correct input.

