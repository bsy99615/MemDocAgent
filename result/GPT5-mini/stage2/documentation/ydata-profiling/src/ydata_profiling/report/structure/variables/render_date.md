# `render_date.py`

## `src.ydata_profiling.report.structure.variables.render_date.render_date` · *function*

## Summary:
Produce presentation objects for a date-typed variable summary: builds a top grid (variable info, two summary tables, mini histogram) and a bottom tab with a full histogram image, returning a dict of template variables used by the report renderer.

## Description:
This function converts a computed summary for a date variable into presentation-layer objects (Container, Table, Image, VariableInfo) that the HTML report generator consumes.

Typical callers and context:
- Invoked by the report generation pipeline when rendering a single variable of type "date" (the variable-rendering dispatcher that maps variable types to renderer functions).
- Called during the "structure/variables" stage of report creation after the statistical summary for the variable has been computed.

Why this logic is extracted:
- Encapsulates presentation concerns (layout, formatting, calling plotting helpers) separate from summary computation.
- Keeps the variable-type-specific layout in one place so renderers for other types (numeric, categorical, etc.) remain isolated and consistent.

## Args:
    config (Settings):
        - The global configuration object for the report.
        - Used to obtain display style and the desired image format (config.html.style, config.plot.image_format).
        - Type: ydata_profiling.config.Settings (configuration with at least html.style and plot.image_format attributes).
    summary (Dict[str, Any]):
        - A dict containing the computed summary information for the date variable.
        - Required keys and expected value types:
            * "varid" (str): unique identifier for the variable, used for HTML anchor ids.
            * "varname" (str): readable variable name shown in the VariableInfo.
            * "alerts" (list[str] or similar): alerts for this variable (passed to VariableInfo).
            * "description" (str): description string for the variable (passed to VariableInfo).
            * "n_distinct" (int): number of distinct values.
            * "p_distinct" (float): proportion distinct (0..1).
            * "n_missing" (int): number of missing values.
            * "p_missing" (float): proportion missing (0..1).
            * "memory_size" (int): memory size in bytes for the variable.
            * "min" (Any): minimum value (presented via fmt).
            * "max" (Any): maximum value (presented via fmt).
            * "histogram" (Either a list or an indexable pair):
                - If list: an iterable where each element is a pair/sequence (bin_edges, counts). The function will extract [x[0] for x in histogram] and [x[1] for x in histogram] and pass them to the plotting helpers.
                - Otherwise: histogram[0] is interpreted as bin edges sequence and histogram[1] as counts sequence.
        - The function expects the values to be compatible with the formatters (fmt, fmt_percent, fmt_bytesize) and plotting helpers (mini_histogram, histogram).

## Returns:
    Dict[str, Any]:
        - A mapping with at least the keys:
            * "top": Container — a grid container containing:
                - VariableInfo (varid, varname, type "Date", alerts, description)
                - Table with distinct/missing/memory metrics
                - Table with min/max values
                - Image for a mini histogram
            * "bottom": Container — a tabs container containing:
                - Image for the full histogram with caption that includes the number of bins computed as (len(summary['histogram'][1]) - 1)
        - Each value is an instance from ydata_profiling.report.presentation.core (Container, Image, Table, VariableInfo). The calling code should render these containers into the final HTML page.

Edge-case returns:
- The function always returns a dict with "top" and "bottom" if inputs satisfy the preconditions; if required keys are missing a KeyError will occur before a return.

## Raises:
    - KeyError: If any required key is missing from the summary dict (e.g., "varid", "histogram", "n_missing", etc.). The code accesses keys directly.
    - TypeError / IndexError: If summary["histogram"] is present but not indexable as expected (e.g., histogram[0] / histogram[1] access fails) or elements inside histogram are not sequences of length >= 2 when a list-of-pairs representation is expected.
    - Any exceptions raised by:
        * formatters fmt, fmt_percent, fmt_bytesize if given incompatible values,
        * plotting helpers mini_histogram or histogram if passed invalid data,
      will propagate to the caller.

## Constraints:
Preconditions (what must be true before calling):
    - config must provide:
        * config.html.style (used to style Table and VariableInfo)
        * config.plot.image_format (string used for Image.image_format)
    - summary must contain the keys listed in Args with value types compatible with the formatters and plotting helpers.
    - summary["histogram"] must be either:
        * A list/iterable of pair-like items where each item supports indexing [0] and [1], or
        * An indexable pair/sequence (histogram[0], histogram[1]) where histogram[0] is bin edges and histogram[1] counts.

Postconditions (guarantees after return):
    - A dictionary with keys "top" and "bottom" is returned where:
        * "top" is a Container configured as a "grid" sequence containing presentation items for the variable.
        * "bottom" is a Container configured as "tabs" with an Image presenting the full histogram and an anchor id built from summary["varid"].
    - No I/O has been performed by this function itself (presentation objects are created but not written to disk here).

## Side Effects:
    - No direct I/O (no file or network writes) are performed by this function.
    - No global state is mutated within this function.
    - Calls out to:
        * formatters: fmt, fmt_percent, fmt_bytesize — pure formatting functions (assumed no side effects).
        * plotting helpers: mini_histogram, histogram — produce plotting data/objects consumed by Image; any internal side effects of these helpers are not introduced by render_date itself (they may allocate in-memory plot data).
    - Creates presentation-layer objects (Container, Image, Table, VariableInfo) which are returned for downstream rendering.

## Control Flow:
flowchart TD
    A[Start render_date] --> B{summary contains "histogram" as list?}
    B -- yes --> C[Extract edges series = [x[0] for x in histogram]]
    B -- yes --> D[Extract counts series = [x[1] for x in histogram]]
    B -- no --> E[Use histogram[0] as edges and histogram[1] as counts]
    C --> F[Call mini_histogram(config, edges series, counts series, date=True)]
    D --> F
    E --> F
    F --> G[Wrap mini histogram in Image]
    G --> H[Create VariableInfo and two Tables (distinct/missing/memory and min/max)]
    H --> I[Compose top Container (grid) with info, tables, mini histogram]
    E --> J[Call histogram(config, edges, counts, date=True)]
    D --> J
    J --> K[Wrap full histogram in Image with caption and anchor]
    K --> L[Compose bottom Container (tabs) with histogram Image]
    L --> M[Return {"top": top_container, "bottom": bottom_container}]

## Examples:
Example usage (conceptual — presentation objects are returned for the report renderer):

    from ydata_profiling.config import Settings

    config = Settings()  # must be a Settings instance with html.style and plot.image_format
    summary = {
        "varid": "var1",
        "varname": "order_date",
        "alerts": [],
        "description": "Order date for transactions",
        "n_distinct": 123,
        "p_distinct": 0.8,
        "n_missing": 2,
        "p_missing": 0.01,
        "memory_size": 1024,
        "min": "2020-01-01",
        "max": "2022-12-31",
        # Accepted histogram shapes:
        # Option A: pair-like: (bin_edges, counts)
        "histogram": ([ "2020-01-01", "2021-01-01", "2022-01-01", "2023-01-01" ],
                      [100, 150, 20]),
        # Option B: list of pairs: [ (edges_series1, counts1), (edges_series2, counts2) ]
    }

    try:
        template_vars = render_date(config, summary)
        top_container = template_vars["top"]     # Container for grid display
        bottom_container = template_vars["bottom"]  # Container for histogram tab
        # The report renderer will take these containers and convert to HTML.
    except KeyError as e:
        # Handle missing summary fields
        raise RuntimeError(f"Invalid summary for render_date; missing key: {e}") from e

