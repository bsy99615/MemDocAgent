# `nb_to_doc.py`

## `docs.tutorials.tools.nb_to_doc.convert_nb` · *function*

## Summary:
Runs three jupyter nbconvert steps for a notebook basename: executes the notebook, exports it to reStructuredText, then clears outputs in the source notebook — all invoked through an external process-runner helper.

## Description:
Known callers within the codebase:
    - No direct callers were discovered in the available repository snapshot. This function is intended for use by documentation build scripts or tutorial conversion tooling that need to transform Jupyter notebooks into documentation artifacts as part of a docs generation pipeline.

Why this function exists:
    - Converting a notebook into documentation requires a fixed sequence of CLI invocations (execute → export → clear). Encapsulating that sequence in one function ensures consistent options and ordering across the codebase and avoids duplicating the command sequence at each call site.

Behavior summary:
    - The function constructs a filename by concatenating nbname + ".ipynb" and invokes a helper named sh three times with these argument lists (shown here in command form):
        1) jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=60 <nbname>.ipynb
        2) jupyter nbconvert --to rst <nbname>.ipynb
        3) jupyter nbconvert --to notebook --inplace --ClearOutputPreprocessor.enabled=True <nbname>.ipynb
    - Calls are performed sequentially. The function returns None on success and propagates exceptions raised by sh on failure.

## Args:
    nbname (str):
        - Required. The notebook basename without the .ipynb extension (for example "intro" to operate on "intro.ipynb").
        - If nbname already includes the suffix ".ipynb", the function will construct a filename like "foo.ipynb.ipynb", which will likely cause the jupyter commands to fail because the file does not exist. Callers should pass the basename without the extension.
        - Type requirements: must support string concatenation with ".ipynb" (typically a str). Passing a non-string will raise a TypeError during concatenation.

## Returns:
    None
    - No value is returned. Success is indicated by normal completion (no exception).

## Raises:
    - NameError: if the helper sh is not defined in the runtime scope when convert_nb is called.
    - TypeError: if nbname is not a string-like object and cannot be concatenated with ".ipynb".
    - Any exception raised by the helper sh when invoking the external processes. In common implementations where sh wraps subprocess.check_call, this will be subprocess.CalledProcessError if the jupyter command exits with a non-zero status.
    - Any file- or CLI-related errors surfaced by the jupyter executable (e.g., FileNotFoundError if the .ipynb file is missing, or OSError if jupyter is not on PATH) will propagate through sh.

## Constraints:
    Preconditions:
        - A callable named sh must be available in the module/global scope. Expected minimal contract for sh:
            * Accepts a single positional argument: a sequence (list/tuple) of command arguments, e.g. ["jupyter", "nbconvert", "--to", "rst", "file.ipynb"].
            * Synchronously executes the command and either returns on success or raises an exception on failure (for example, subprocess.CalledProcessError).
            * sh may capture or forward stdout/stderr; convert_nb does not inspect those streams.
        - The jupyter CLI (jupyter nbconvert) must be installed and reachable on the environment PATH.
        - The current working directory (or the resolved path) must contain the target nbname + ".ipynb" file.
        - nbname should not include the ".ipynb" extension to avoid double extensions.

    Postconditions (on successful completion):
        - A file named nbname + ".rst" will be created or overwritten by nbconvert.
        - The source notebook nbname + ".ipynb" will have been executed and then left with cleared outputs (i.e., outputs removed).
        - The function returns None.

## Side Effects:
    - Runs external processes via the jupyter CLI; these processes perform file reads/writes.
    - Mutates files on disk:
        * Overwrites/updates nbname + ".ipynb" twice (first to store executed outputs, then to clear outputs).
        * Creates/overwrites nbname + ".rst".
    - Any logging, stdout/stderr behavior, or retry semantics are determined by the sh helper implementation.
    - No network calls are made by convert_nb itself beyond what jupyter nbconvert might perform internally (e.g., if notebook cells make network requests during execution).

## Control Flow:
flowchart TD
    Start --> Validate_nbname[Is nbname provided and string-like?]
    Validate_nbname --> Build_fname[Construct fname = nbname + ".ipynb"]
    Build_fname --> Exec_step[Call sh with execute command]
    Exec_step --> Exec_failed{sh raised exception?}
    Exec_failed -- Yes --> Propagate_error[Propagate exception to caller]
    Exec_failed -- No --> Rst_step[Call sh to convert to rst]
    Rst_step --> Rst_failed{sh raised exception?}
    Rst_failed -- Yes --> Propagate_error
    Rst_failed -- No --> Clear_step[Call sh to clear outputs in-place]
    Clear_step --> Clear_failed{sh raised exception?}
    Clear_failed -- Yes --> Propagate_error
    Clear_failed -- No --> Success[Return None]

## Examples:
Basic usage (preserve success/failure handling):
    try:
        # Convert "getting_started.ipynb" -> executes it, writes getting_started.rst, then clears outputs
        convert_nb("getting_started")
    except Exception as e:
        # Typical handling: log error and abort or retry
        print("Notebook conversion failed:", e)

Avoid double-extension mistake:
    # Incorrect: will attempt to operate on "foo.ipynb.ipynb"
    convert_nb("foo.ipynb")

    # Correct:
    convert_nb("foo")

Customization note:
    - If callers need to keep executed outputs in the source notebook, they should not call convert_nb as-is; instead, implement a variant that omits the final clear step or modify this function to accept a flag controlling the clear step.

