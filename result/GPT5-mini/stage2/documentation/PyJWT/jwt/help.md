# `help.py`

## `jwt.help.info` · *function*

*No documentation generated.*

## `jwt.help.main` · *function*

## Summary:
Formats the object returned by the module-level info() function as pretty-printed JSON and writes it to standard output.

## Description:
- Known callers:
    - None found in the provided code snapshot. The function is a small presentation wrapper in this module that serializes and prints information returned by info().
- Purpose and responsibility:
    - Separates presentation (JSON serialization and printing) from data collection. main() is responsible only for converting info()'s return value into a human-readable JSON string and emitting it to stdout; it does not perform data collection itself.

## Args:
    None

## Returns:
    None
    - The function has no return value; its observable effect is writing a JSON string (plus a terminating newline produced by print()) to standard output.
    - There are no alternate successful return values.

## Raises:
    - Any exception raised by info() will propagate unchanged out of main().
    - TypeError: Raised by json.dumps if the object returned by info() contains values that the JSON encoder cannot serialize (for example, arbitrary Python objects without a conversion to JSON-serializable primitives).
    - OSError / BrokenPipeError / IOError: May be raised by print() when writing to stdout fails (for example, if stdout is a pipe and the reader has closed). These I/O-related exceptions will propagate out of main().

## Constraints:
- Preconditions:
    - No strict preconditions enforced by main(); however, for successful serialization and output, info() should return a JSON-serializable Python value (commonly a dict, list, str, int, float, bool, or None).
- Postconditions:
    - If no exception is raised, stdout will contain the pretty-printed JSON representation of the object returned by info() and the function will have returned None.

## Side Effects:
- I/O:
    - Writes text to standard output through print(), producing one line (the JSON string) followed by a newline.
- Calls:
    - Invokes the module-level info() function. Any side effects performed by info() (I/O, network access, reading globals, etc.) occur before serialization and are not modified by main().
- No global state in this module is modified by main() itself.

## Control Flow:
flowchart TD
    Start --> CallInfo[Call info()]
    CallInfo -->|exception| PropagateInfoEx[Propagate exception from info()]
    CallInfo -->|returns value v| Serialize[Call json.dumps(v, sort_keys=True, indent=2)]
    Serialize -->|exception (TypeError)| PropagateJSONEx[Propagate json.dumps exception]
    Serialize -->|success (json_str)| Print[print(json_str)]
    Print -->|exception (OSError/BrokenPipeError)| PropagateIOEx[Propagate print exception]
    Print -->|success| End[Return None]

## Examples:
- Basic usage (conceptual; assumes info() is available in the same module):
    - Call main() to print a pretty JSON representation of info()'s return value.
- Example with error handling around main():
    - Wrap a call to main() if the caller needs to handle serialization or I/O errors explicitly:
        - Catch TypeError to detect non-serializable return values from info() and either transform the data or report the error.
        - Catch BrokenPipeError/OSError if the process writes to a pipe and the reader might close early; decide whether to ignore or log and exit.

