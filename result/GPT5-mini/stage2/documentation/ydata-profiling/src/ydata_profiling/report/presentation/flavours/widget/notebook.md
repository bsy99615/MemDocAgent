# `notebook.py`

## `src.ydata_profiling.report.presentation.flavours.widget.notebook.get_notebook_iframe_srcdoc` · *function*

## Summary:
Return an IPython HTML display object that embeds a ProfileReport's rendered HTML inside a sized iframe (using the iframe srcdoc attribute) so the report appears inline in Jupyter notebooks.

## Description:
Known callers within the codebase:
- Intended for use by notebook-oriented presentation layers (flavours/widget) that need to show a ProfileReport inside a Jupyter notebook cell. No explicit direct callers were found in the provided snapshot.

Typical usage context:
- Called during the interactive "display" stage after a ProfileReport has been created (and possibly rendered lazily). The function obtains the report HTML via profile.to_html(), escapes it for safe inclusion inside an HTML attribute, and returns an IPython.core.display.HTML object wrapping a single <iframe> element.

Responsibility boundary:
- Encapsulates: reading iframe dimensions from configuration, retrieving the report HTML, escaping it for safe in-attribute embedding, composing the iframe markup, and returning an IPython HTML object. It does not perform file I/O, nor does it host or write the report to disk — use ProfileReport.to_file or a separate IFrame with a file URL for those needs.

## Args:
    config (Settings)
        - The Settings object (from ydata_profiling.config).
        - Required nested attributes: config.notebook.iframe.width and config.notebook.iframe.height.
        - Acceptable values: any object whose string representation is acceptable for an iframe width/height attribute (common values are integers, e.g. 800, or strings like "800px" or "100%").
        - The function uses the values verbatim via f-string interpolation (str() is applied implicitly).

    profile (ProfileReport)
        - The ProfileReport instance to display.
        - The function calls profile.to_html() (no arguments) and expects a str result (see Returns).
        - If profile.to_html() triggers lazy rendering, this call may perform expensive computation.

Interdependencies:
- Correct behavior depends on config exposing the specified nested attributes.
- The function depends on ProfileReport.to_html() returning a string containing the full HTML report.

## Returns:
    IPython.core.display.HTML
    - An HTML display object whose content is a single <iframe> element string:
        - width and height attributes are set from config.notebook.iframe.width and config.notebook.iframe.height.
        - srcdoc attribute is set to the HTML-escaped output of profile.to_html().
        - frameborder="0" and allowfullscreen are present.
    - Edge cases:
        - If profile.to_html() returns an empty string, the srcdoc will be empty and the iframe will display an empty document.
        - If profile.to_html() returns a non-string, html.escape will raise TypeError; the function does not coerce non-string outputs.
        - The returned HTML object is always produced only when the function completes without exception.

## Raises:
    ImportError
        - If IPython.core.display.HTML cannot be imported (IPython not installed), the import inside the function will raise ImportError.

    AttributeError
        - If config or one of the nested attributes (notebook, iframe, width, height) is missing, accessing them will raise AttributeError.

    Any exception propagated from profile.to_html()
        - profile.to_html() may raise exceptions (ValueError, RuntimeError, TypeError, etc.) originating from report generation or rendering. These exceptions are not caught and will propagate to the caller.

    TypeError
        - If profile.to_html() returns a non-str value, html.escape(...) will raise TypeError.

## Constraints:
Preconditions:
    - config must be a Settings-like object with notebook.iframe.width and notebook.iframe.height.
    - profile must be a fully-constructed ProfileReport instance (its __init__ must have completed).
    - Calling this function may trigger expensive rendering (if the report is lazily generated).

Postconditions:
    - On successful return, an IPython.display.HTML object wrapping an iframe string has been created and returned.
    - The iframe's srcdoc contains the HTML-escaped version of the string returned by profile.to_html() (so the attribute value is safe). Browsers will unescape the attribute value when constructing the embedded document, producing the original report HTML in the embedded context.

## Important implementation details (why escape is used)
    - The function calls html.escape(profile.to_html()) with the default quote=True.
        - This escapes &, <, > and both single and double quotes (so attribute boundaries are not broken).
        - Escaping ensures the long HTML string can be safely inserted into the double-quoted srcdoc="..." attribute without prematurely terminating the attribute or injecting malformed markup.
        - When the browser reads the iframe's srcdoc attribute, entity references (e.g., &lt;, &quot;) are interpreted so the embedded document receives the intended HTML content.
    - Because the escaped HTML is placed in an attribute rather than in nested HTML nodes, this approach avoids the need for additional JS or multipart document construction.

## Side Effects:
    - Triggers whatever side effects profile.to_html() performs (lazy generation, caching of internal HTML, CPU/memory usage, possible progress output).
    - No filesystem or network I/O is performed by this function itself.
    - No global state is mutated directly by this function.

## Practical constraints & recommendations:
    - Browser/size limits: Extremely large HTML strings may cause performance issues or hit browser/DOM limits when inserted into srcdoc. For very large reports, prefer writing the report to disk and embedding via a file URL (see example below).
    - Memory: Because the full HTML is kept in memory (ProfileReport._html and the HTML attribute), ensure sufficient memory is available when rendering large reports.

## Control Flow:
flowchart TD
    A[Start] --> B[Import IPython.core.display.HTML]
    B --> C[Read width,height from config.notebook.iframe]
    C --> D[Call profile.to_html()]
    D -->|returns str| E[Call html.escape(..., quote=True)]
    E --> F[Compose iframe string with width,height,srcdoc]
    F --> G[Return IPython HTML(iframe string)]
    D -->|raises| H[Propagate exception from to_html()]
    B -->|ImportError| I[Propagate ImportError]
    C -->|missing attribute| J[Propagate AttributeError]
    D -->|returns non-str| K[html.escape raises TypeError]

## Examples:

Typical notebook usage (inline display):
    try:
        iframe_display = get_notebook_iframe_srcdoc(config, profile)
        # In a Jupyter notebook, either evaluate iframe_display as the cell value
        # or call IPython.display.display(iframe_display) to render it.
    except ImportError:
        print("IPython is not available in this environment; cannot render inline.")
    except Exception as e:
        # Catches rendering exceptions propagated from profile.to_html()
        print("Failed to render profile inline:", type(e).__name__, str(e))

Alternative for very large reports (avoid srcdoc size limits):
    - Write the report to a temporary HTML file and embed using an IFrame that points to the file URL (this avoids embedding the entire HTML inside an attribute).
    - Example flow:
        1. profile.to_file("report.html")  # writes HTML to disk
        2. from IPython.lib.display import IFrame
        3. display(IFrame(src="report.html", width=config.notebook.iframe.width, height=config.notebook.iframe.height))

Notes:
    - This function intentionally does not attempt to sanitize or alter the report HTML itself; it relies on HTML-escaping for safe embedding in an attribute and on the ProfileReport renderer to produce valid HTML.
    - If you need the raw report HTML string (for further processing), call profile.to_html() directly instead of using this helper.

## `src.ydata_profiling.report.presentation.flavours.widget.notebook.get_notebook_iframe_src` · *function*

## Summary:
Create a local HTML export of a ProfileReport in a temporary directory and return an IPython IFrame that embeds that HTML with width and height taken from the provided settings.

## Description:
This helper extracts the logic to persist a ProfileReport to a temporary HTML file and return an IPython.lib.display.IFrame pointing to that file for inline embedding inside Jupyter/IPython notebook front-ends.

Known callers / typical usage context:
- Notebook or widget rendering code that embeds profiling reports inline in notebooks (presentation layer for the "notebook" flavour).
- Typical trigger: after a ProfileReport instance has been generated and a notebook-oriented display is requested (for example, when rendering the report inside a notebook cell or a widget that displays notebook content).
- No specific repository function callers are enumerated here; this function is intended for use by the notebook-flavour presentation code path that needs an IFrame referencing an on-disk HTML export.

Why this is extracted:
- Producing an IFrame requires multiple steps (temporary filename generation, directory creation, calling ProfileReport.to_file(), and constructing the IFrame) that are orthogonal to higher-level presentation logic. Splitting this out keeps the rendering pipeline focused on orchestration while isolating filesystem and IFrame construction concerns, making tests and maintenance simpler.

## Args:
    config (Settings):
        - The configuration object for the report presentation.
        - Required to provide nested attributes at: config.notebook.iframe.width and config.notebook.iframe.height.
        - Allowed values: the width and height values are passed through to IPython.lib.display.IFrame; typical values are integers representing pixels or strings understood by IFrame (e.g., '100%'). The function does not validate or coerce these values.
        - Interdependency: width and height are read from config.notebook.iframe.*. If these attributes are missing or incorrectly typed, an AttributeError may be raised by attribute access or the IFrame constructor may raise.

    profile (ProfileReport):
        - The ProfileReport instance to export to HTML.
        - The function calls profile.to_file(tmp_file). The behavior and exceptions from to_file (including I/O errors or rendering exceptions) propagate to the caller.

## Returns:
    IPython.lib.display.IFrame
    - An IFrame object that references the newly created HTML file on disk (path converted to string).
    - The IFrame's width and height are set to config.notebook.iframe.width and config.notebook.iframe.height respectively.
    - Edge cases:
        * If profile.to_file or filesystem operations fail, no IFrame is returned (an exception is raised instead).
        * The returned IFrame references a persistent file in ./ipynb_tmp; the file is not removed by this function.

## Raises:
    - Any exceptions raised by Path.mkdir when creating the temporary directory:
        * FileExistsError / PermissionError / OSError if the directory cannot be created or parent permissions prevent creation. (mkdir is called with exist_ok=True; FileExistsError is not expected for existing directories, but permission errors and other OSErrors can occur.)
    - Any exceptions raised by profile.to_file(tmp_file):
        * See ProfileReport.to_file for a full list (e.g., FileNotFoundError when parent directory is missing is unlikely here because this function creates the parent directory; other I/O errors, serialization/rendering errors, or asset creation errors may propagate).
    - ImportError:
        * If IPython.lib.display.IFrame is unavailable in the runtime environment, importing IFrame will raise ImportError/ModuleNotFoundError when the function attempts "from IPython.lib.display import IFrame".
    - Any exceptions raised by the IFrame constructor:
        * If width/height values are invalid for IFrame, the constructor may raise TypeError or ValueError depending on IPython version/implementation.

## Constraints:
Preconditions:
    - The caller has a valid ProfileReport instance whose to_file() method can render the report to disk.
    - The runtime environment allows importing IPython.lib.display.IFrame (i.e., running in an environment where IPython is installed).
    - The current working directory must be writable (the function writes into ./ipynb_tmp beneath the current working directory).

Postconditions:
    - A directory ./ipynb_tmp exists (created if necessary).
    - An HTML file named <uuid>.html exists inside ./ipynb_tmp containing the exported report (assuming profile.to_file succeeds).
    - An IPython.lib.display.IFrame object is returned that references the file path string of that HTML file and has width/height set from the provided config.

## Side Effects:
    - Filesystem:
        * Creates the directory ./ipynb_tmp if it does not exist.
        * Writes a single HTML file: ./ipynb_tmp/<uuid>.html via ProfileReport.to_file.
        * The temporary file is not deleted by this function; repeated calls produce multiple files.
    - No network I/O or external service calls are performed by this function itself (but profile.to_file may perform operations that have additional side effects—see its documentation).
    - No global variables are mutated by this function.

## Control Flow:
flowchart TD
    Start --> GenFilename[Generate tmp filename: ./ipynb_tmp/<uuid>.html]
    GenFilename --> EnsureDir[Ensure ./ipynb_tmp exists (mkdir exist_ok=True)]
    EnsureDir --> Export[Call profile.to_file(tmp_file)]
    Export --> ImportIFrame[Import IFrame from IPython.lib.display]
    ImportIFrame --> CreateIFrame[Return IFrame(str(tmp_file), width, height)]
    Export -->|profile.to_file raises| RaiseExportError[Propagate exception]
    EnsureDir -->|mkdir raises| RaiseMkdirError[Propagate exception]
    ImportIFrame -->|import raises| RaiseImportError[Propagate exception]

## Examples:
Example inline notebook usage (conceptual; not-executable snippet):
- Typical successful usage inside a Jupyter notebook cell:
    1) Create or obtain a ProfileReport instance: profile = ProfileReport(df, config=...)
    2) Use the notebook presentation config object: cfg = profile.config (or a Settings instance with necessary nested attributes)
    3) Call the helper to obtain an IFrame: iframe = get_notebook_iframe_src(cfg, profile)
    4) Display the IFrame in the notebook: from IPython.display import display; display(iframe)

- Example with basic error handling (pseudocode):
    try:
        iframe = get_notebook_iframe_src(cfg, profile)
        display(iframe)
    except ImportError:
        # IPython not installed in environment
        print("Cannot embed report: IPython is not available.")
    except Exception as exc:
        # Propagated I/O or rendering error from profile.to_file or filesystem
        print(f"Failed to create notebook iframe: {exc}")

## `src.ydata_profiling.report.presentation.flavours.widget.notebook.get_notebook_iframe` · *function*

## Summary:
Dispatches to the notebook iframe strategy configured by the Settings and returns either an IPython IFrame (file-backed) or an IPython HTML display (srcdoc-embedded) for inline display of a ProfileReport.

## Description:
This function is the small dispatcher used by the notebook-flavour presentation layer to obtain the appropriate IPython display object for embedding a ProfileReport inside a Jupyter/IPython environment. It reads the iframe attribute from the provided Settings and chooses the corresponding helper:

- If the configuration requests a file-backed iframe (IframeAttribute.src), it calls the helper that exports the report to a temporary HTML file and returns an IPython.lib.display.IFrame referencing that file.
- If the configuration requests an in-attribute embedding (IframeAttribute.srcdoc), it calls the helper that obtains the report HTML, escapes it, and returns an IPython.core.display.HTML that contains an <iframe srcdoc="...">.

Known callers and typical usage:
- Notebook and widget presentation code paths that render a ProfileReport inline in a Jupyter notebook cell or widget.
- Typical trigger: after a ProfileReport has been generated and the presentation layer needs an object suitable for immediate display (e.g., in a notebook cell or via IPython.display.display).

Why this logic is extracted:
- Selecting between two distinct embedding strategies (file-backed vs srcdoc-embedded) is a single decision point used by the notebook presentation flow. Extracting this decision into its own function keeps higher-level rendering code concise and centralizes the configuration-dependent policy. The function delegates the concrete work (filesystem export or HTML composition) to focused helpers so those concerns remain isolated and testable.

## Args:
    config (Settings)
        - Type: ydata_profiling.config.Settings
        - Must expose: config.notebook.iframe.attribute (value compared to IframeAttribute.src and IframeAttribute.srcdoc).
        - Side attributes required by callees (depending on attribute):
            * If attribute == IframeAttribute.src: callees will read config.notebook.iframe.width and config.notebook.iframe.height.
            * If attribute == IframeAttribute.srcdoc: callees will read config.notebook.iframe.width and config.notebook.iframe.height.
        - Interdependencies: The function only reads config.notebook.iframe.attribute itself; the invoked helper expects additional nested attributes (width/height). Missing nested attributes may cause AttributeError when accessed by this dispatcher or the helper functions.

    profile (ProfileReport)
        - Type: ydata_profiling.ProfileReport
        - The ProfileReport instance that will be exported or rendered by the selected helper.
        - The function does not inspect profile itself; it passes it directly to the chosen helper. Any behavior, cost, or exceptions from profile.to_file() or profile.to_html() are delegated to and propagated from those helpers.

## Returns:
    Union[IPython.lib.display.IFrame, IPython.core.display.HTML]
    - If config.notebook.iframe.attribute == IframeAttribute.src:
        * Returns an IPython.lib.display.IFrame referencing a filesystem HTML file produced by exporting the report (file-backed embedding).
        * The concrete helper creates a file (./ipynb_tmp/<uuid>.html) and sets IFrame width/height from the configuration.
    - If config.notebook.iframe.attribute == IframeAttribute.srcdoc:
        * Returns an IPython.core.display.HTML object containing an <iframe> whose srcdoc attribute is the HTML-escaped string produced by profile.to_html(), and whose width/height are taken from the configuration.
    - Edge-case returns:
        * No return value is produced if an exception is raised by attribute lookup, the selected helper, or side-effect operations — exceptions propagate to the caller.

## Raises:
    ValueError
        - Raised when config.notebook.iframe.attribute has a value other than IframeAttribute.src or IframeAttribute.srcdoc.
        - Exact message produced by the implementation:
            Iframe Attribute can be "src" or "srcdoc" (current: {attribute}).
          (where {attribute} is replaced with the actual attribute value)

    AttributeError
        - Can occur if config or nested attributes (notebook, iframe, attribute) are missing; attribute access fails.
        - Also may occur later in the invoked helper when accessing width/height if those attributes are absent.

    Any exception raised by the selected helper (propagated):
        - If attribute == IframeAttribute.src: exceptions from the file-backed helper may include filesystem errors (OSError, PermissionError), exceptions raised by ProfileReport.to_file(), or ImportError if IPython.lib.display.IFrame is unavailable.
        - If attribute == IframeAttribute.srcdoc: exceptions may include ImportError if IPython.core.display.HTML is unavailable, TypeError from html.escape if profile.to_html() returns a non-str, or exceptions propagated from profile.to_html() (ValueError, RuntimeError, etc.).

## Constraints:
Preconditions:
    - config must be a Settings-like object with notebook.iframe.attribute set to a valid IframeAttribute enum member.
    - profile must be a valid ProfileReport instance suitable for the chosen embedding strategy.
    - The runtime environment should have IPython available for display objects if embedding is required; otherwise the invoked helper will raise ImportError.

Postconditions:
    - On successful return, the caller receives an IPython display object appropriate to the configured attribute:
        * file-backed IFrame referencing a written HTML file, or
        * HTML object containing an iframe with srcdoc equal to the escaped report HTML.
    - No additional guarantees are made about the persistence of any filesystem artifacts — file-backed helper leaves the exported HTML file on disk.

## Side Effects:
    - This dispatcher does not directly perform I/O or mutate global state; however the chosen helper may:
        * Write a temporary HTML file to disk (file-backed path).
        * Trigger expensive in-memory report generation (srcdoc path via profile.to_html()).
    - Any side effects produced by profile.to_file() or profile.to_html() (caching, resource allocation, disk writes) are propagated.

## Control Flow:
flowchart TD
    Start --> ReadAttr[Read config.notebook.iframe.attribute]
    ReadAttr --> IsSrc{attribute == IframeAttribute.src?}
    IsSrc -->|Yes| CallSrc[get_notebook_iframe_src(config, profile)]
    IsSrc -->|No| IsSrcdoc{attribute == IframeAttribute.srcdoc?}
    IsSrcdoc -->|Yes| CallSrcdoc[get_notebook_iframe_srcdoc(config, profile)]
    IsSrcdoc -->|No| RaiseValue[Raise ValueError: Iframe Attribute can be "src" or "srcdoc" (current: {attribute}).]
    CallSrc --> ReturnIFrame[Return IFrame]
    CallSrcdoc --> ReturnHTML[Return HTML]
    CallSrc -->|callee raises| PropagateSrcError[Propagate exception from src helper]
    CallSrcdoc -->|callee raises| PropagateSrcdocError[Propagate exception from srcdoc helper]
    ReadAttr -->|missing attr| PropagateAttrError[Propagate AttributeError]

## Examples:
Typical notebook usage (file-backed embedding):
    # Conceptual flow:
    # 1) Create or obtain a ProfileReport: profile = ProfileReport(df, config=...)
    # 2) Obtain the Settings object: cfg = profile.config  (or another Settings instance)
    # 3) Ensure cfg.notebook.iframe.attribute is set to IframeAttribute.src
    # 4) Call the dispatcher: iframe = get_notebook_iframe(cfg, profile)
    # 5) Display in a Jupyter notebook cell: from IPython.display import display; display(iframe)
    # Error handling:
    try:
        iframe = get_notebook_iframe(cfg, profile)
        display(iframe)
    except ValueError as exc:
        # Unrecognized attribute value
        print("Invalid iframe configuration:", exc)
    except ImportError:
        # IPython not available
        print("IPython is required to render notebook iframe.")
    except Exception as exc:
        # Propagated errors from exporting/rendering
        print("Failed to create notebook iframe:", type(exc).__name__, str(exc))

Typical notebook usage (srcdoc embedding):
    # Ensure cfg.notebook.iframe.attribute is set to IframeAttribute.srcdoc
    try:
        html_display = get_notebook_iframe(cfg, profile)
        display(html_display)  # Renders the iframe whose srcdoc contains the report HTML
    except Exception as exc:
        # Handle rendering/export errors or missing dependencies
        print("Could not render profile inline:", type(exc).__name__, str(exc))

