# `notebook.py`

## `src.ydata_profiling.utils.notebook.full_width` · *function*

## Summary:
Injects a small CSS style into the current Jupyter/IPython notebook output to cause notebook container elements to render at 100% browser width.

## Description:
Known callers within the codebase:
- No direct internal callers were detected in the provided snapshot. This helper is intended for interactive use or to be called by notebook-aware setup routines before rendering wide reports or visualizations.

Context and typical usage:
- Run once in an interactive Jupyter/IPython notebook session (for example, near the top of a notebook) when you want the notebook's rendered report or wide widgets/tables to span the full browser width.
- The function is intentionally minimal: it injects an HTML <style> element into the notebook cell output stream so the change is applied by the notebook frontend.

Responsibility boundary:
- Encapsulates only the presentation change required to widen the notebook container. It does not alter report generation, data processing, file I/O, or persistent settings; callers remain responsible for when to invoke it.

## Args:
- None

## Returns:
- None. The function has no return value; its observable effect is the injected CSS in the notebook frontend.

## Raises:
- ImportError: raised at call time if the required IPython display utilities cannot be imported (IPython is not installed or the import fails).
- Any exception raised by IPython.core.display.display or HTML may propagate; the function does not catch exceptions from the display call.

## Constraints:
Preconditions:
- Best-effort expectation that the code is executed where IPython.core.display.HTML and display are importable (i.e., an environment with IPython installed).
- The visible result requires a notebook frontend (browser) connected to the kernel; in headless or logger-only environments the CSS injection will not be visible even if the call succeeds.

Postconditions:
- An HTML style element with the exact content <style>.container { width:100% !important; }</style> has been emitted to the notebook output stream. If the frontend renders cell outputs, elements matching the CSS selector ".container" will be displayed at full width until the page is reloaded or another rule overrides it.

## Side Effects:
- Emits HTML output to the current IPython display output stream; this is the only direct side effect.
- Does not perform file, network, or database I/O.
- Does not explicitly mutate module-level variables. (Note: the Python import performed at call time will populate sys.modules per normal import semantics.)
- No external service calls are made.

## Implementation details (what the function does):
- Performs an inline import: from IPython.core.display import HTML, display
- Constructs an HTML object containing the CSS string "<style>.container { width:100% !important; }</style>"
- Calls display(HTML(...)) to emit that HTML into the notebook output

## Control Flow:
flowchart TD
    A[Call full_width()] --> B{Import IPython.display?}
    B -- No --> C[ImportError raised and propagates]
    B -- Yes --> D[Create HTML object with CSS string]
    D --> E[Call display(HTML(...))]
    E --> F{Notebook frontend connected?}
    F -- Yes --> G[CSS applied; visible container becomes full width]
    F -- No --> H[HTML emitted but has no visible effect in headless/non-frontend environment]
    G --> I[Effect persists until page reload or overwritten by later CSS]
    H --> I

## Examples:
Interactive notebook (simple):
- Place this in a notebook cell early in the session and execute the cell. There is no return value; look for layout change in subsequent outputs.
    full_width()

Guarded usage for non-notebook environments:
- If your code may run where IPython is not available, call the function inside a try/except to avoid crashing the process:
    try:
        full_width()
    except ImportError:
        # IPython not present — continue without changing layout
        pass

Notes and caveats:
- The CSS targets elements with class selector ".container". Whether this selector affects every notebook UI depends on the frontend and theme (Jupyter Notebook, JupyterLab, or third-party themes). If a frontend uses a different container class or higher-specificity rules, the effect may vary.
- The function injects a style element into the current output; to revert the change you must reload the page or inject a different overriding CSS rule.

