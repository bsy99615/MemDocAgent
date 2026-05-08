# `context.py`

## `src.ydata_profiling.visualisation.context.manage_matplotlib_context` · *function*

## Summary:
Temporarily apply a predefined matplotlib/seaborn plotting style and backend for the duration of a plotting context, then reliably restore the original matplotlib rcParams and converter registration on exit.

## Description:
This generator sets a consistent plotting style (rcParams and seaborn style), registers pandas' matplotlib converters, and forces a non-interactive "agg" backend while yielding control to the caller to perform plotting. It always performs cleanup in a finally block: deregistering converters and restoring the exact rcParams snapshot taken at entry.

Known callers within the repository:
    - No explicit call sites were discovered in the supplied context. Typical callers are functions that render static matplotlib figures for profiling reports or other visualization pipelines; these callers wrap the generator as a context manager around the plotting code so styling applies only while creating the figures.

Why this is a standalone function:
    - Centralizes global plotting configuration for consistent visuals across the codebase.
    - Encapsulates side-effecting changes to global matplotlib state and ensures they are reverted even on exceptions.
    - Makes it easy to update plotting defaults in one place and reduces duplication.

## Args:
    - None.

## Returns:
    - Any: The function is a generator that yields exactly once (yielding None). Behavior depends on how it is used:
        * If called directly (manage_matplotlib_context()), it returns a generator object.
        * To use as a context manager with a with-statement, the generator must be wrapped with contextlib.contextmanager (for example contextlib.contextmanager(manage_matplotlib_context) or by decorating the function with @contextlib.contextmanager). When used as a wrapped context manager, the yield point provides no value to the with-block.

## Raises:
    - No explicit exceptions are raised by the function itself. However, exceptions raised by underlying library calls (for example register_matplotlib_converters, matplotlib.rcParams.update, or sns.set_style) will propagate to the caller.
    - If invalid keys or values are provided to matplotlib.rcParams.update (via the hard-coded customRcParams), matplotlib may raise errors; those are not intercepted here.
    - deregister_matplotlib_converters() is called unconditionally in the finally block; if that function raises, the exception will propagate after the finally block begins (restoration attempt may still have been partially executed).

## Constraints:
Preconditions:
    - matplotlib and pandas.plotting (register/deregister converters) must be importable and functional in the environment.
    - seaborn must be importable and referenced in the module namespace as sns (the function calls sns.set_style). Common pattern: import seaborn as sns.
    - Callers must accept that this function mutates global plotting state (rcParams and backend) and thus affects all plotting in the same process while active.

Postconditions (guaranteed when the generator completes its finally block):
    - matplotlib.rcParams are restored to the exact snapshot stored in originalRcParams (including the original backend).
    - register_matplotlib_converters effects are reversed by calling deregister_matplotlib_converters().
    - Deprecation warnings from matplotlib (matplotlib.cbook.mplDeprecation category) are suppressed only during the rcParams restoration step.

## Side Effects:
    - Updates global matplotlib.rcParams with a specific dictionary (customRcParams) that includes style, sizing, font, colors, and backend="agg".
    - Calls register_matplotlib_converters() on entry and deregister_matplotlib_converters() on exit, affecting pandas' plotting converters.
    - Calls sns.set_style(style="white") (i.e., seaborn style is set while the context is active).
    - Suppresses matplotlib.cbook.mplDeprecation warnings during the restoration of rcParams.
    - No file, network, or other external I/O is performed by this function directly.

## Control Flow:
flowchart TD
    A[Call manage_matplotlib_context()] --> B[originalRcParams = matplotlib.rcParams.copy()]
    B --> C[Define customRcParams dict (including backend="agg")]
    C --> D[Enter try block]
    D --> E[register_matplotlib_converters()]
    E --> F[matplotlib.rcParams.update(customRcParams)]
    F --> G[sns.set_style("white")]
    G --> H[Yield None to caller (plotting occurs)]
    H --> I[Caller plotting completes or raises]
    I --> J[Finally block begins]
    J --> K[deregister_matplotlib_converters()]
    K --> L[with warnings.catch_warnings(): filter mplDeprecation]
    L --> M[matplotlib.rcParams.update(originalRcParams)]
    M --> N[Generator exits; cleanup complete]

## Examples:
1) Use as a context manager by wrapping with contextlib.contextmanager:
    import contextlib
    from your_module import manage_matplotlib_context

    cm = contextlib.contextmanager(manage_matplotlib_context)
    with cm():
        # plotting code here uses the profiling style and backend "agg"
        fig, ax = matplotlib.pyplot.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])

    # after the with-block, rcParams and converters are restored

2) Equivalent pattern if you can decorate the function (makes it directly usable):
    from contextlib import contextmanager

    @contextmanager
    def manage_matplotlib_context_decorated():
        # (implementation identical to the generator body)
        yield

    # Usage:
    with manage_matplotlib_context_decorated():
        # plotting code

3) Wrong usage (common pitfall):
    gen = manage_matplotlib_context()  # returns a generator object
    # This does not activate the intended context. Either wrap with contextmanager
    # or decorate the function to use it in a with-statement.

## Implementation notes for reimplementation:
    - Snapshot matplotlib.rcParams at entry using .copy() to capture all current settings (including backend).
    - Apply a custom rcParams dict that includes fonts, colors, figure size, and backend="agg".
    - Register pandas' matplotlib converters for consistent datetime plotting and deregister them in teardown.
    - Use a try/finally so that cleanup always runs even if plotting code raises.
    - Suppress matplotlib.cbook.mplDeprecation warnings only while restoring rcParams to avoid noisy logs from matplotlib internals.

