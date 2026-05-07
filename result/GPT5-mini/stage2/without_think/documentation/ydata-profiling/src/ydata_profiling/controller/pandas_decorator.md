# `pandas_decorator.py`

## `src.ydata_profiling.controller.pandas_decorator.profile_report` · *function*

## Summary:
Creates and returns a ProfileReport instance for the provided pandas DataFrame by forwarding the DataFrame and any additional keyword arguments to the ProfileReport constructor.

## Description:
This small wrapper centralizes the creation of a ProfileReport from a pandas DataFrame. It:
- Accepts a DataFrame and any constructor options supported by ProfileReport, constructs the ProfileReport, and returns it unchanged.
- Does not perform validation or transformation of the DataFrame itself; that responsibility is delegated to the ProfileReport constructor.

Known callers within the codebase:
- This function implementation does not reference any internal callers in the same file. It is intended as a convenience entry point for external code or user-facing code that wants to create a ProfileReport from a DataFrame and pass configuration options.

Why this is extracted into its own function:
- Encapsulates the one-step creation of a ProfileReport in a single, named function for discoverability and to provide a stable import location (e.g., consumer code can import this helper rather than directly importing ProfileReport).
- Keeps call sites concise and makes it possible to apply cross-cutting concerns in one place in the future (logging, instrumentation, input validation) if needed.

## Args:
    df (pandas.DataFrame):
        The tabular data to be profiled. The function expects a pandas DataFrame object; the type is indicated by the type hint but not enforced at runtime here.
    **kwargs:
        Any keyword arguments supported by ydata_profiling.profile_report.ProfileReport.__init__. All kwargs are forwarded directly to the ProfileReport constructor. Typical kwargs control report configuration (e.g., title, config, minimal), but exact accepted keys and value types are defined by ProfileReport.

Interdependencies:
    - kwargs are passed verbatim to ProfileReport; their meaning and allowed values depend entirely on ProfileReport's API.

## Returns:
    ydata_profiling.profile_report.ProfileReport
        A newly constructed ProfileReport instance configured with the given DataFrame and kwargs.

Possible return values / edge cases:
    - Always returns the ProfileReport instance returned by the ProfileReport constructor on successful construction.
    - If ProfileReport.__init__ raises an exception, this function does not catch it and no value is returned (exception propagates).

## Raises:
    - Any exception raised by ydata_profiling.profile_report.ProfileReport when invoked with (df, **kwargs).
      Because the function does not catch exceptions from ProfileReport, typical errors may include constructor validation errors or runtime errors thrown while profiling the DataFrame. This wrapper itself does not raise exceptions directly.

## Constraints:
Preconditions:
    - The caller should pass an object that is a pandas.DataFrame (or an object acceptable to ProfileReport). There is no runtime type enforcement in this wrapper; invalid types will surface as errors from ProfileReport.
    - Any kwargs used must be valid for ProfileReport.__init__.

Postconditions:
    - On successful return, the caller receives a ProfileReport instance representing the profiling of the provided DataFrame with the supplied options.
    - No further guarantees are made about side effects; side effects are determined by ProfileReport's implementation and the provided kwargs (for example: saving files, writing to disk, or network calls may occur inside ProfileReport).

## Side Effects:
    - This wrapper itself performs no I/O and mutates no global state.
    - Indirect side effects may occur inside ProfileReport.__init__ or related behavior triggered by kwargs (e.g., report generation that writes files). Those side effects are not implemented here and depend on ProfileReport's configuration and implementation.
    - Any logging, caching, or external interactions executed by ProfileReport will be observed when calling this function.

## Control Flow:
flowchart TD
    A[Start: Call profile_report(df, **kwargs)] --> B[Invoke ProfileReport(df, **kwargs)]
    B --> |Constructor succeeds| C[Return ProfileReport instance]
    B --> |Constructor raises exception| D[Exception propagates to caller]

## Examples (usage described in prose):
- Typical happy-path usage:
    1. Prepare a pandas DataFrame containing the data to profile.
    2. Call the function with the DataFrame and any desired ProfileReport options (for example, configuration settings exposed by ProfileReport).
    3. Receive a ProfileReport instance and then use its methods or properties to render or save the report as appropriate.

- Error handling usage (described):
    1. If you expect that the DataFrame may be invalid for profiling, wrap the call in a try/except block that catches the exceptions that ProfileReport may raise (e.g., ValueError or custom validation exceptions) and handle them (log, clean data, rethrow, or inform the user).
    2. Because this wrapper does not validate inputs itself, all validation and error messages will originate from ProfileReport.

Notes:
    - To learn the exact kwargs accepted and their semantics, consult the documentation or source of ydata_profiling.profile_report.ProfileReport.

